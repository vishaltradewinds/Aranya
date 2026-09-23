from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from .auth import Principal, require_permission
from .db import SessionLocal, JourneyRecord
from .intent import understand

router=APIRouter(prefix="/api/v1/journeys",tags=["journeys"])

class JourneyStartIn(BaseModel):
    message:str=Field(min_length=1,max_length=4000)
    context:dict[str,Any]=Field(default_factory=dict)

class JourneyAdvanceIn(BaseModel):
    state:str=Field(min_length=2,max_length=50)
    next_action:str=Field(min_length=1,max_length=200)

def view(j:JourneyRecord)->dict[str,Any]:
    return {"id":j.id,"stakeholder_id":j.stakeholder_id,"intent_type":j.intent_type,"journey_key":j.journey_key,"state":j.state,"intent":j.intent_payload,"next_action":j.next_action,"created_at":j.created_at,"updated_at":j.updated_at}

@router.post("",status_code=201)
def start_journey(payload:JourneyStartIn,principal:Principal=require_permission("journey:create")):
    parsed=understand(payload.message,payload.context)
    now=datetime.now(timezone.utc)
    with SessionLocal() as db:
        j=JourneyRecord(id=f"ARJ-{uuid4().hex[:12].upper()}",stakeholder_id=principal.user_id,intent_type=parsed.intent_type.value,journey_key=parsed.journey_key,state="INTENT_IDENTIFIED",intent_payload=parsed.as_dict(),next_action=parsed.missing_questions[0] if parsed.missing_questions else "intent_confirm",created_at=now,updated_at=now)
        db.add(j);db.commit();db.refresh(j);return view(j)

@router.get("/{journey_id}")
def get_journey(journey_id:str,principal:Principal=require_permission("journey:read")):
    with SessionLocal() as db:
        j=db.get(JourneyRecord,journey_id)
        if not j: raise HTTPException(404,"Journey not found")
        if principal.role.value!="ADMIN" and j.stakeholder_id!=principal.user_id: raise HTTPException(403,"Journey access denied")
        return view(j)

@router.post("/{journey_id}/advance")
def advance_journey(journey_id:str,payload:JourneyAdvanceIn,principal:Principal=require_permission("journey:advance")):
    with SessionLocal() as db:
        j=db.get(JourneyRecord,journey_id)
        if not j: raise HTTPException(404,"Journey not found")
        if principal.role.value!="ADMIN" and j.stakeholder_id!=principal.user_id: raise HTTPException(403,"Journey access denied")
        j.state=payload.state;j.next_action=payload.next_action;j.updated_at=datetime.now(timezone.utc)
        db.commit();db.refresh(j);return view(j)
