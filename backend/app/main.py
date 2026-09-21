from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .db import init_db, get_session, LotRecord, AuditRecord

app = FastAPI(title="ARANYA API", version="0.2.0")

class EvidenceStatus(str, Enum):
    CLAIMED="CLAIMED"; DOCUMENTED="DOCUMENTED"; REMOTE_VERIFIED="REMOTE_VERIFIED"
    FIELD_VERIFIED="FIELD_VERIFIED"; AUTHORITY_VERIFIED="AUTHORITY_VERIFIED"; OUTCOME_VERIFIED="OUTCOME_VERIFIED"

class LotStatus(str, Enum):
    DRAFT="DRAFT"; ELIGIBILITY_REVIEW="ELIGIBILITY_REVIEW"; TRADE_ELIGIBLE="TRADE_ELIGIBLE"
    CONDITIONAL="CONDITIONAL"; HOLD="HOLD"; RESTRICTED="RESTRICTED"; UNKNOWN="UNKNOWN"
    MATCHED="MATCHED"; ORDERED="ORDERED"; IN_TRANSIT="IN_TRANSIT"; DELIVERED="DELIVERED"; SETTLED="SETTLED"

class ProduceIn(BaseModel):
    producer_id: str = Field(min_length=1)
    product: str = Field(min_length=1)
    species: str | None = None
    quantity_kg: float = Field(gt=0)
    origin_state: str = Field(min_length=1)
    origin_district: str = Field(min_length=1)
    source_type: str = Field(min_length=1)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
async def health():
    return {"status":"ok","service":"aranya-api","version":"0.2.0","persistence":"sqlalchemy"}

@app.post("/api/v1/lots", status_code=201)
async def create_lot(payload: ProduceIn, session: AsyncSession = Depends(get_session)):
    lot_id=f"ARL-{uuid4().hex[:12].upper()}"
    now=datetime.now(timezone.utc)
    lot=LotRecord(id=lot_id, producer_id=payload.producer_id, product=payload.product,
        species=payload.species, quantity_kg=payload.quantity_kg,
        origin_state=payload.origin_state, origin_district=payload.origin_district,
        source_type=payload.source_type, evidence_status=EvidenceStatus.CLAIMED.value,
        regulatory_status=LotStatus.UNKNOWN.value, status=LotStatus.ELIGIBILITY_REVIEW.value,
        created_at=now)
    event=AuditRecord(id=str(uuid4()),entity_id=lot_id,action="LOT_CREATED",
        actor=payload.producer_id,data={"lot_id":lot_id,"product":payload.product,"quantity_kg":payload.quantity_kg},
        occurred_at=now)
    session.add_all([lot,event])
    await session.commit()
    return {"id":lot.id,"producer_id":lot.producer_id,"product":lot.product,"species":lot.species,
        "quantity_kg":lot.quantity_kg,"origin_state":lot.origin_state,"origin_district":lot.origin_district,
        "source_type":lot.source_type,"evidence_status":lot.evidence_status,
        "regulatory_status":lot.regulatory_status,"status":lot.status,"created_at":lot.created_at}

@app.get("/api/v1/lots/{lot_id}")
async def get_lot(lot_id:str, session:AsyncSession=Depends(get_session)):
    result=await session.execute(select(LotRecord).where(LotRecord.id==lot_id))
    lot=result.scalar_one_or_none()
    if not lot: raise HTTPException(status_code=404,detail="Lot not found")
    return {"id":lot.id,"producer_id":lot.producer_id,"product":lot.product,"species":lot.species,
        "quantity_kg":lot.quantity_kg,"origin_state":lot.origin_state,"origin_district":lot.origin_district,
        "source_type":lot.source_type,"evidence_status":lot.evidence_status,
        "regulatory_status":lot.regulatory_status,"status":lot.status,"created_at":lot.created_at}

@app.get("/api/v1/audit/{entity_id}")
async def get_audit(entity_id:str, session:AsyncSession=Depends(get_session)):
    result=await session.execute(select(AuditRecord).where(AuditRecord.entity_id==entity_id).order_by(AuditRecord.occurred_at))
    return [{"id":e.id,"entity_id":e.entity_id,"action":e.action,"actor":e.actor,"data":e.data,"occurred_at":e.occurred_at} for e in result.scalars()]
