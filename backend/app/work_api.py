from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .auth import Principal, require_permission
from .db import SessionLocal, WorkTaskRecord, WorkOutcomeRecord, JourneyRecord, NetworkRecord

router=APIRouter(prefix="/api/v1/work",tags=["work"])
class TaskIn(BaseModel):
    journey_id:str
    network_id:str|None=None
    task_type:str=Field(min_length=2,max_length=80)
    title:str=Field(min_length=2,max_length=200)
    quantity:float|None=None
    unit:str|None=None
    location:str|None=None
    due_at:datetime|None=None
    evidence_required:list[str]=Field(default_factory=list,max_length=30)
class TaskStateIn(BaseModel):
    state:str=Field(min_length=2,max_length=50)
class OutcomeIn(BaseModel):
    outcome_type:str=Field(min_length=2,max_length=80)
    evidence_id:str|None=None
    notes:str|None=Field(default=None,max_length=1000)

def task_view(t):
    return {"id":t.id,"journey_id":t.journey_id,"network_id":t.network_id,"assigned_to":t.assigned_to,"task_type":t.task_type,"title":t.title,"state":t.state,"quantity":t.quantity,"unit":t.unit,"location":t.location,"due_at":t.due_at,"evidence_required":t.evidence_required or [],"created_at":t.created_at,"updated_at":t.updated_at}

@router.post("/tasks",status_code=201)
def create_task(p:TaskIn,principal:Principal=require_permission("work:create")):
    with SessionLocal() as db:
        j=db.get(JourneyRecord,p.journey_id)
        if not j: raise HTTPException(404,"Journey not found")
        if principal.role.value!="ADMIN" and j.stakeholder_id!=principal.user_id: raise HTTPException(403,"Journey access denied")
        if p.network_id and not db.get(NetworkRecord,p.network_id): raise HTTPException(404,"Network not found")
        now=datetime.now(timezone.utc)
        t=WorkTaskRecord(id=f"ART-{uuid4().hex[:12].upper()}",journey_id=p.journey_id,network_id=p.network_id,assigned_to=None,task_type=p.task_type,title=p.title,state="OPEN",quantity=p.quantity,unit=p.unit,location=p.location,due_at=p.due_at,evidence_required=p.evidence_required,created_at=now,updated_at=now)
        db.add(t);db.commit();db.refresh(t);return task_view(t)

@router.get("/tasks/{task_id}")
def get_task(task_id:str,principal:Principal=require_permission("work:read")):
    with SessionLocal() as db:
        t=db.get(WorkTaskRecord,task_id)
        if not t: raise HTTPException(404,"Task not found")
        j=db.get(JourneyRecord,t.journey_id)
        if principal.role.value!="ADMIN" and (not j or j.stakeholder_id!=principal.user_id): raise HTTPException(403,"Task access denied")
        return task_view(t)

@router.post("/tasks/{task_id}/state")
def set_task_state(task_id:str,p:TaskStateIn,principal:Principal=require_permission("work:update")):
    allowed={"OPEN","ACCEPTED","IN_PROGRESS","EVIDENCE_PENDING","HANDOVER_PENDING","COMPLETED","CANCELLED"}
    if p.state not in allowed: raise HTTPException(400,"Invalid work state")
    with SessionLocal() as db:
        t=db.get(WorkTaskRecord,task_id)
        if not t: raise HTTPException(404,"Task not found")
        j=db.get(JourneyRecord,t.journey_id)
        if principal.role.value!="ADMIN" and (not j or j.stakeholder_id!=principal.user_id): raise HTTPException(403,"Task access denied")
        t.state=p.state;t.updated_at=datetime.now(timezone.utc);db.commit();db.refresh(t);return task_view(t)

@router.post("/tasks/{task_id}/outcomes",status_code=201)
def record_outcome(task_id:str,p:OutcomeIn,principal:Principal=require_permission("work:outcome")):
    with SessionLocal() as db:
        t=db.get(WorkTaskRecord,task_id)
        if not t: raise HTTPException(404,"Task not found")
        j=db.get(JourneyRecord,t.journey_id)
        if principal.role.value!="ADMIN" and (not j or j.stakeholder_id!=principal.user_id): raise HTTPException(403,"Task access denied")
        if p.evidence_id is None and t.evidence_required: raise HTTPException(409,{"code":"EVIDENCE_REQUIRED","required":t.evidence_required})
        o=WorkOutcomeRecord(id=f"ARO-{uuid4().hex[:12].upper()}",task_id=task_id,outcome_type=p.outcome_type,state="CLAIMED",evidence_id=p.evidence_id,notes=p.notes,created_at=datetime.now(timezone.utc))
        db.add(o);t.state="COMPLETED";t.updated_at=datetime.now(timezone.utc);db.commit();db.refresh(o)
        return {"id":o.id,"task_id":o.task_id,"outcome_type":o.outcome_type,"state":o.state,"evidence_id":o.evidence_id,"notes":o.notes,"created_at":o.created_at}
