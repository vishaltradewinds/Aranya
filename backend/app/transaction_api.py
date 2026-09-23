from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .auth import Principal, require_permission
from .db import SessionLocal, WorkTaskRecord, WorkOutcomeRecord, HandoverRecord, SettlementRecord, JourneyRecord

router=APIRouter(prefix="/api/v1/transactions",tags=["transactions"])
class HandoverIn(BaseModel):
    to_party:str=Field(min_length=1,max_length=100)
    quantity:float|None=None
    unit:str|None=None
    evidence_id:str|None=None
    notes:str|None=Field(default=None,max_length=1000)
class AcceptIn(BaseModel):
    notes:str|None=Field(default=None,max_length=1000)
class SettlementIn(BaseModel):
    payer:str=Field(min_length=1,max_length=100)
    payee:str=Field(min_length=1,max_length=100)
    amount:float=Field(gt=0)
    currency:str=Field(default="INR",min_length=3,max_length=10)
    basis:str=Field(min_length=3,max_length=500)
    outcome_id:str|None=None

def access(db,task,principal):
    j=db.get(JourneyRecord,task.journey_id)
    if principal.role.value!="ADMIN" and (not j or j.stakeholder_id!=principal.user_id): raise HTTPException(403,"Task access denied")

@router.post("/tasks/{task_id}/handover",status_code=201)
def create_handover(task_id:str,p:HandoverIn,principal:Principal=require_permission("transaction:handover")):
    with SessionLocal() as db:
        t=db.get(WorkTaskRecord,task_id)
        if not t: raise HTTPException(404,"Task not found")
        access(db,t,principal)
        if t.evidence_required and not p.evidence_id: raise HTTPException(409,{"code":"EVIDENCE_REQUIRED","required":t.evidence_required})
        h=HandoverRecord(id=f"ARH-{uuid4().hex[:12].upper()}",task_id=task_id,from_party=principal.user_id,to_party=p.to_party,quantity=p.quantity,unit=p.unit,evidence_id=p.evidence_id,state="PENDING_ACCEPTANCE",accepted_by=None,accepted_at=None,notes=p.notes,created_at=datetime.now(timezone.utc))
        db.add(h);t.state="HANDOVER_PENDING";t.updated_at=datetime.now(timezone.utc);db.commit();db.refresh(h)
        return {"id":h.id,"task_id":h.task_id,"from_party":h.from_party,"to_party":h.to_party,"quantity":h.quantity,"unit":h.unit,"evidence_id":h.evidence_id,"state":h.state}

@router.post("/handovers/{handover_id}/accept")
def accept_handover(handover_id:str,p:AcceptIn,principal:Principal=require_permission("transaction:accept")):
    with SessionLocal() as db:
        h=db.get(HandoverRecord,handover_id)
        if not h: raise HTTPException(404,"Handover not found")
        if h.state!="PENDING_ACCEPTANCE": raise HTTPException(409,"Handover is not pending acceptance")
        if h.to_party!=principal.user_id: raise HTTPException(403,"Only receiving party can accept")
        h.state="ACCEPTED";h.accepted_by=principal.user_id;h.accepted_at=datetime.now(timezone.utc)
        h.notes=p.notes or h.notes
        t=db.get(WorkTaskRecord,h.task_id)
        if t: t.state="COMPLETED";t.updated_at=datetime.now(timezone.utc)
        db.commit();return {"id":h.id,"state":h.state,"accepted_by":h.accepted_by,"accepted_at":h.accepted_at}

@router.post("/tasks/{task_id}/settlements",status_code=201)
def create_settlement(task_id:str,p:SettlementIn,principal:Principal=require_permission("transaction:settlement")):
    with SessionLocal() as db:
        t=db.get(WorkTaskRecord,task_id)
        if not t: raise HTTPException(404,"Task not found")
        access(db,t,principal)
        if p.outcome_id:
            o=db.get(WorkOutcomeRecord,p.outcome_id)
            if not o or o.task_id!=task_id: raise HTTPException(404,"Outcome not found")
        s=SettlementRecord(id=f"ARS-{uuid4().hex[:12].upper()}",task_id=task_id,outcome_id=p.outcome_id,payer=p.payer,payee=p.payee,amount=p.amount,currency=p.currency,basis=p.basis,state="PROPOSED",reference=None,created_at=datetime.now(timezone.utc))
        db.add(s);db.commit();db.refresh(s)
        return {"id":s.id,"task_id":s.task_id,"payer":s.payer,"payee":s.payee,"amount":s.amount,"currency":s.currency,"basis":s.basis,"state":s.state}

@router.post("/settlements/{settlement_id}/accept")
def accept_settlement(settlement_id:str,principal:Principal=require_permission("transaction:accept")):
    with SessionLocal() as db:
        s=db.get(SettlementRecord,settlement_id)
        if not s: raise HTTPException(404,"Settlement not found")
        if s.state!="PROPOSED": raise HTTPException(409,"Settlement is not proposed")
        if principal.user_id not in {s.payer,s.payee}: raise HTTPException(403,"Settlement party mismatch")
        s.state="ACCEPTED";db.commit();return {"id":s.id,"state":s.state}
