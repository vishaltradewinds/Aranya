from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from enum import Enum
from uuid import uuid4
from datetime import datetime,timezone
from typing import Optional
from .db import SessionLocal,init_db,LotRecord,AuditRecord,LotTransitionRecord,EvidenceRecord
from .state import LotStatus,can_transition
from .evidence import EvidenceType, EvidenceStatus as EvidenceLevel
from .regulatory import RuleRegistry,MP_BASELINE_RULES,RegulatoryStatus,RegulatoryContext
from .auth import Principal, require_permission
app=FastAPI(title="ARANYA API",version="0.3.0")
init_db()
registry=RuleRegistry(MP_BASELINE_RULES)
class EvidenceStatus(str,Enum):
    CLAIMED="CLAIMED"; DOCUMENTED="DOCUMENTED"; REMOTE_VERIFIED="REMOTE_VERIFIED"; FIELD_VERIFIED="FIELD_VERIFIED"; AUTHORITY_VERIFIED="AUTHORITY_VERIFIED"; OUTCOME_VERIFIED="OUTCOME_VERIFIED"
class ProduceIn(BaseModel):
    producer_id:str=Field(min_length=1); product:str=Field(min_length=1); species:Optional[str]=None; quantity_kg:float=Field(gt=0); origin_state:str=Field(min_length=1); origin_district:str=Field(min_length=1); source_type:str=Field(min_length=1)
class Lot(BaseModel):
    id:str; producer_id:str; product:str; species:Optional[str]; quantity_kg:float; origin_state:str; origin_district:str; source_type:str; evidence_status:EvidenceStatus; regulatory_status:LotStatus; status:LotStatus; created_at:datetime
class TransitionIn(BaseModel):
    target_status:LotStatus; reason:str=Field(min_length=1)
class EvidenceIn(BaseModel):
    evidence_type:EvidenceType
    source:str=Field(min_length=1)
    reference:str=Field(min_length=1)
    metadata:dict={}
class EvidenceVerifyIn(BaseModel):
    status:EvidenceLevel
    verifier_note:str=Field(min_length=1)
@app.on_event("startup")
def startup(): init_db()
def to_lot(r):
    return Lot(id=r.id,producer_id=r.producer_id,product=r.product,species=r.species,quantity_kg=r.quantity_kg,origin_state=r.origin_state,origin_district=r.origin_district,source_type=r.source_type,evidence_status=EvidenceStatus(r.evidence_status),regulatory_status=LotStatus(r.regulatory_status),status=LotStatus(r.status),created_at=r.created_at)
def audit(db,action,entity_id,actor,data):
    db.add(AuditRecord(id=str(uuid4()),entity_id=entity_id,action=action,actor=actor,data=data,occurred_at=datetime.now(timezone.utc)))
@app.get("/health")
def health(): return {"status":"ok","service":"aranya-api","version":"0.3.0","persistence":"sqlalchemy","regulatory_gate":True}
@app.post("/api/v1/lots",response_model=Lot,status_code=201)
def create_lot(payload:ProduceIn, principal:Principal=require_permission("lot:create")):
    with SessionLocal() as db:
        if principal.role.value=="PRODUCER" and payload.producer_id != principal.user_id: raise HTTPException(403,"Producer identity mismatch")
        lot_id=f"ARL-{uuid4().hex[:12].upper()}"; now=datetime.now(timezone.utc)
        r=LotRecord(id=lot_id,producer_id=payload.producer_id,product=payload.product,species=payload.species,quantity_kg=payload.quantity_kg,origin_state=payload.origin_state,origin_district=payload.origin_district,source_type=payload.source_type,evidence_status="CLAIMED",regulatory_status="UNKNOWN",status="ELIGIBILITY_REVIEW",created_at=now)
        db.add(r); audit(db,"LOT_CREATED",lot_id,principal.user_id,{"status":r.status,"regulatory_status":r.regulatory_status}); db.commit(); db.refresh(r); return to_lot(r)
@app.get("/api/v1/lots/{lot_id}",response_model=Lot)
def get_lot(lot_id:str, principal:Principal=require_permission("lot:read")):
    with SessionLocal() as db:
        r=db.get(LotRecord,lot_id)
        if not r: raise HTTPException(404,"Lot not found")
        return to_lot(r)
@app.get("/api/v1/audit/{entity_id}")
def get_audit(entity_id:str, principal:Principal=require_permission("audit:read:self")):
    with SessionLocal() as db:
        return [{"id":e.id,"action":e.action,"entity_id":e.entity_id,"actor":e.actor,"data":e.data,"occurred_at":e.occurred_at} for e in db.query(AuditRecord).filter(AuditRecord.entity_id==entity_id).order_by(AuditRecord.occurred_at).all()]

@app.post("/api/v1/lots/{lot_id}/evidence", status_code=201)
def add_evidence(lot_id:str,payload:EvidenceIn, principal:Principal=require_permission("evidence:create")):
    with SessionLocal() as db:
        lot=db.get(LotRecord,lot_id)
        if not lot: raise HTTPException(404,"Lot not found")
        if principal.role.value=="PRODUCER" and lot.producer_id != principal.user_id: raise HTTPException(403,"Evidence access denied")
        evidence_id=f"ARE-{uuid4().hex[:12].upper()}"
        now=datetime.now(timezone.utc)
        metadata=dict(payload.metadata)
        metadata["submitted_by"]=principal.user_id
        metadata["submitted_role"]=principal.role.value
        from .evidence import EvidenceItem
        item=EvidenceItem(evidence_id,lot_id,payload.evidence_type,EvidenceLevel.CLAIMED,payload.source,payload.reference,now,metadata)
        record=EvidenceRecord(id=evidence_id,entity_id=lot_id,evidence_type=payload.evidence_type.value,status=EvidenceLevel.CLAIMED.value,source=payload.source,reference=payload.reference,metadata_json=metadata,content_hash=item.content_hash(),captured_at=now)
        db.add(record)
        audit(db,"EVIDENCE_SUBMITTED",lot_id,principal.user_id,{"evidence_id":evidence_id,"evidence_type":payload.evidence_type.value,"status":"CLAIMED","content_hash":record.content_hash})
        db.commit()
        return {"id":evidence_id,"entity_id":lot_id,"evidence_type":record.evidence_type,"status":record.status,"content_hash":record.content_hash,"captured_at":record.captured_at}

@app.get("/api/v1/lots/{lot_id}/evidence")
def list_evidence(lot_id:str, principal:Principal=require_permission("lot:read")):
    with SessionLocal() as db:
        lot=db.get(LotRecord,lot_id)
        if not lot: raise HTTPException(404,"Lot not found")
        if principal.role.value=="PRODUCER" and lot.producer_id != principal.user_id: raise HTTPException(403,"Evidence access denied")
        return [{"id":e.id,"entity_id":e.entity_id,"evidence_type":e.evidence_type,"status":e.status,"source":e.source,"reference":e.reference,"metadata":e.metadata_json,"content_hash":e.content_hash,"captured_at":e.captured_at} for e in db.query(EvidenceRecord).filter(EvidenceRecord.entity_id==lot_id).order_by(EvidenceRecord.captured_at).all()]

@app.post("/api/v1/evidence/{evidence_id}/verify")
def verify_evidence(evidence_id:str,payload:EvidenceVerifyIn, principal:Principal=require_permission("evidence:review")):
    with SessionLocal() as db:
        previous=db.get(EvidenceRecord,evidence_id)
        if not previous: raise HTTPException(404,"Evidence not found")
        if payload.status==EvidenceLevel.CLAIMED: raise HTTPException(409,"Verification must advance evidence status")
        order=list(EvidenceLevel)
        if order.index(payload.status) <= order.index(EvidenceLevel(previous.status)): raise HTTPException(409,"Evidence status must advance")
        new_id=f"ARE-{uuid4().hex[:12].upper()}"
        now=datetime.now(timezone.utc)
        metadata=dict(previous.metadata_json)
        metadata.update({"previous_evidence_id":previous.id,"verifier_id":principal.user_id,"verifier_role":principal.role.value,"verifier_note":payload.verifier_note})
        from .evidence import EvidenceItem
        item=EvidenceItem(new_id,previous.entity_id,EvidenceType(previous.evidence_type),payload.status,previous.source,previous.reference,now,metadata,previous.content_hash)
        record=EvidenceRecord(id=new_id,entity_id=previous.entity_id,evidence_type=previous.evidence_type,status=payload.status.value,source=previous.source,reference=previous.reference,metadata_json=metadata,content_hash=item.content_hash(),captured_at=now)
        db.add(record)
        lot=db.get(LotRecord,previous.entity_id)
        if lot: lot.evidence_status=payload.status.value
        audit(db,"EVIDENCE_VERIFIED",previous.entity_id,principal.user_id,{"previous_evidence_id":previous.id,"evidence_id":new_id,"status":payload.status.value,"content_hash":record.content_hash})
        db.commit()
        return {"id":new_id,"entity_id":record.entity_id,"status":record.status,"content_hash":record.content_hash}
@app.post("/api/v1/lots/{lot_id}/transitions",response_model=Lot)
def transition_lot(lot_id:str,payload:TransitionIn, principal:Principal=require_permission("lot:transition")):
    with SessionLocal() as db:
        r=db.get(LotRecord,lot_id)
        if not r: raise HTTPException(404,"Lot not found")
        current=LotStatus(r.status); target=payload.target_status
        if not can_transition(current,target): raise HTTPException(409,f"Invalid transition: {current.value} -> {target.value}")
        product_class="BAMBOO" if r.product.strip().upper()=="BAMBOO" or (r.species and "bamboo" in r.species.lower()) else "FOREST_PRODUCE"
        activity="MOVE" if target==LotStatus.IN_TRANSIT else "HARVEST"
        d=registry.evaluate(RegulatoryContext(product_class,r.origin_state,r.origin_district,r.source_type,activity,r.evidence_status))
        if target==LotStatus.TRADE_ELIGIBLE and d.status!=RegulatoryStatus.TRADE_ELIGIBLE: raise HTTPException(409,{"code":"REGULATORY_GATE_BLOCKED","regulatory_status":d.status.value,"rule_ids":d.rule_ids,"missing_requirements":d.missing_requirements,"reason":d.reason})
        if target in {LotStatus.MATCHED,LotStatus.ORDERED,LotStatus.IN_TRANSIT} and current in {LotStatus.ELIGIBILITY_REVIEW,LotStatus.UNKNOWN}: raise HTTPException(409,{"code":"ELIGIBILITY_GATE_BLOCKED","reason":"Lot must first reach an eligible or conditional state through governed review."})
        previous=current.value; r.status=target.value; r.regulatory_status=d.status.value
        db.add(LotTransitionRecord(id=str(uuid4()),lot_id=lot_id,from_status=previous,to_status=target.value,actor=principal.user_id,reason=payload.reason,occurred_at=datetime.now(timezone.utc)))
        audit(db,"LOT_STATUS_CHANGED",lot_id,principal.user_id,{"from":previous,"to":target.value,"regulatory_status":d.status.value,"rule_ids":d.rule_ids,"reason":payload.reason})
        db.commit(); db.refresh(r); return to_lot(r)