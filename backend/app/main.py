from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, List, Optional

app = FastAPI(title="ARANYA API", version="0.1.0")

class EvidenceStatus(str, Enum):
    CLAIMED="CLAIMED"
    DOCUMENTED="DOCUMENTED"
    REMOTE_VERIFIED="REMOTE_VERIFIED"
    FIELD_VERIFIED="FIELD_VERIFIED"
    AUTHORITY_VERIFIED="AUTHORITY_VERIFIED"
    OUTCOME_VERIFIED="OUTCOME_VERIFIED"

class LotStatus(str, Enum):
    DRAFT="DRAFT"
    ELIGIBILITY_REVIEW="ELIGIBILITY_REVIEW"
    TRADE_ELIGIBLE="TRADE_ELIGIBLE"
    CONDITIONAL="CONDITIONAL"
    HOLD="HOLD"
    RESTRICTED="RESTRICTED"
    UNKNOWN="UNKNOWN"
    MATCHED="MATCHED"
    ORDERED="ORDERED"
    IN_TRANSIT="IN_TRANSIT"
    DELIVERED="DELIVERED"
    SETTLED="SETTLED"

class ProduceIn(BaseModel):
    producer_id: str = Field(min_length=1)
    product: str = Field(min_length=1)
    species: Optional[str] = None
    quantity_kg: float = Field(gt=0)
    origin_state: str = Field(min_length=1)
    origin_district: str = Field(min_length=1)
    source_type: str = Field(min_length=1)

class Lot(BaseModel):
    id: str
    producer_id: str
    product: str
    species: Optional[str]
    quantity_kg: float
    origin_state: str
    origin_district: str
    source_type: str
    evidence_status: EvidenceStatus
    regulatory_status: LotStatus
    status: LotStatus
    created_at: datetime

lots: Dict[str, Lot] = {}
audit_events: List[dict] = []

def audit(action: str, entity_id: str, actor: str, data: dict):
    audit_events.append({
        "id": str(uuid4()),
        "action": action,
        "entity_id": entity_id,
        "actor": actor,
        "data": data,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    })

@app.get("/health")
def health():
    return {"status":"ok","service":"aranya-api","version":"0.1.0"}

@app.post("/api/v1/lots", response_model=Lot, status_code=201)
def create_lot(payload: ProduceIn):
    lot_id = f"ARL-{uuid4().hex[:12].upper()}"
    lot = Lot(
        id=lot_id,
        producer_id=payload.producer_id,
        product=payload.product,
        species=payload.species,
        quantity_kg=payload.quantity_kg,
        origin_state=payload.origin_state,
        origin_district=payload.origin_district,
        source_type=payload.source_type,
        evidence_status=EvidenceStatus.CLAIMED,
        regulatory_status=LotStatus.UNKNOWN,
        status=LotStatus.ELIGIBILITY_REVIEW,
        created_at=datetime.now(timezone.utc),
    )
    lots[lot_id] = lot
    audit("LOT_CREATED", lot_id, payload.producer_id, lot.model_dump(mode="json"))
    return lot

@app.get("/api/v1/lots/{lot_id}", response_model=Lot)
def get_lot(lot_id: str):
    lot = lots.get(lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    return lot

@app.get("/api/v1/audit/{entity_id}")
def get_audit(entity_id: str):
    return [e for e in audit_events if e["entity_id"] == entity_id]
