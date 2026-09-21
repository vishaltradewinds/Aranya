from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from enum import Enum
from uuid import uuid4
from datetime import datetime,timezone
from typing import Optional
from .db import SessionLocal,init_db,LotRecord,AuditRecord,LotTransitionRecord
from .state import LotStatus,can_transition
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
    target_status:LotStatus; actor:str=Field(min_length=1); reason:str=Field(min_length=1)
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