from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from .auth import Principal, require_permission
from .db import SessionLocal, NetworkRecord, NetworkLinkRecord

router = APIRouter(prefix="/api/v1/networks", tags=["networks"])

class NetworkIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    network_type: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=1000)
    capabilities: list[str] = Field(default_factory=list, max_length=50)
    needs: list[str] = Field(default_factory=list, max_length=50)
    jurisdiction: str | None = Field(default=None, max_length=200)
    organization_id: str | None = None

class LinkIn(BaseModel):
    target_network_id: str
    relation: str = Field(min_length=2, max_length=80)
    evidence_id: str | None = None

def view(n: NetworkRecord) -> dict[str, Any]:
    return {"id":n.id,"name":n.name,"network_type":n.network_type,"description":n.description,"capabilities":n.capabilities or [],"needs":n.needs or [],"jurisdiction":n.jurisdiction,"organization_id":n.organization_id,"active":n.active,"created_at":n.created_at}

@router.post("", status_code=201)
def create_network(payload: NetworkIn, principal: Principal = require_permission("network:create")):
    with SessionLocal() as db:
        network_id=f"ARN-{uuid4().hex[:12].upper()}"
        n=NetworkRecord(id=network_id,organization_id=payload.organization_id or principal.organization_id,name=payload.name,network_type=payload.network_type,description=payload.description,capabilities=payload.capabilities,needs=payload.needs,jurisdiction=payload.jurisdiction,active=True,created_at=datetime.now(timezone.utc))
        db.add(n); db.commit(); db.refresh(n)
        return view(n)

@router.get("")
def list_networks(network_type: str | None = None, capability: str | None = None, need: str | None = None, principal: Principal = require_permission("network:read")):
    with SessionLocal() as db:
        rows=db.query(NetworkRecord).filter(NetworkRecord.active==True).all()
        result=[]
        for n in rows:
            if network_type and n.network_type.lower()!=network_type.lower(): continue
            caps=[str(x).lower() for x in (n.capabilities or [])]
            needs=[str(x).lower() for x in (n.needs or [])]
            if capability and capability.lower() not in caps: continue
            if need and need.lower() not in needs: continue
            result.append(view(n))
        return result

@router.get("/{network_id}")
def get_network(network_id: str, principal: Principal = require_permission("network:read")):
    with SessionLocal() as db:
        n=db.get(NetworkRecord,network_id)
        if not n or not n.active: raise HTTPException(404,"Network not found")
        return view(n)

@router.post("/{network_id}/links", status_code=201)
def link_network(network_id: str, payload: LinkIn, principal: Principal = require_permission("network:link")):
    with SessionLocal() as db:
        source=db.get(NetworkRecord,network_id); target=db.get(NetworkRecord,payload.target_network_id)
        if not source or not target or not source.active or not target.active: raise HTTPException(404,"Network not found")
        link=NetworkLinkRecord(id=f"ARLNK-{uuid4().hex[:12].upper()}",source_network_id=source.id,target_network_id=target.id,relation=payload.relation,status="PROPOSED",evidence_id=payload.evidence_id,created_at=datetime.now(timezone.utc))
        db.add(link); db.commit()
        return {"id":link.id,"source_network_id":source.id,"target_network_id":target.id,"relation":link.relation,"status":link.status}

@router.get("/{network_id}/matches")
def matches(network_id: str, capability: str | None = None, need: str | None = None, principal: Principal = require_permission("network:read")):
    with SessionLocal() as db:
        source=db.get(NetworkRecord,network_id)
        if not source or not source.active: raise HTTPException(404,"Network not found")
        wanted_capability=(capability or (source.needs[0] if source.needs else "")).lower()
        wanted_need=(need or (source.capabilities[0] if source.capabilities else "")).lower()
        rows=db.query(NetworkRecord).filter(NetworkRecord.active==True,NetworkRecord.id!=network_id).all()
        scored=[]
        for n in rows:
            caps={str(x).lower() for x in (n.capabilities or [])}; needs={str(x).lower() for x in (n.needs or [])}
            score=(2 if wanted_capability and wanted_capability in caps else 0)+(1 if wanted_need and wanted_need in needs else 0)
            reciprocal=len(caps.intersection({str(x).lower() for x in (source.needs or [])}))+len(needs.intersection({str(x).lower() for x in (source.capabilities or [])}))
            score+=reciprocal
            if score: scored.append((score,n))
        scored.sort(key=lambda x:x[0],reverse=True)
        return [{"score":score,"network":view(n)} for score,n in scored[:20]]
