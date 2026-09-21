from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json

class EvidenceType(str, Enum):
    IDENTITY="IDENTITY"
    OWNERSHIP="OWNERSHIP"
    ORIGIN="ORIGIN"
    QUANTITY="QUANTITY"
    QUALITY="QUALITY"
    HARVEST="HARVEST"
    TRANSIT="TRANSIT"
    AUTHORITY="AUTHORITY"
    DELIVERY="DELIVERY"

class EvidenceStatus(str, Enum):
    CLAIMED="CLAIMED"
    DOCUMENTED="DOCUMENTED"
    REMOTE_VERIFIED="REMOTE_VERIFIED"
    FIELD_VERIFIED="FIELD_VERIFIED"
    AUTHORITY_VERIFIED="AUTHORITY_VERIFIED"
    OUTCOME_VERIFIED="OUTCOME_VERIFIED"

@dataclass(frozen=True)
class EvidenceItem:
    id:str
    entity_id:str
    evidence_type:EvidenceType
    status:EvidenceStatus
    source:str
    reference:str
    captured_at:datetime
    metadata:dict
    previous_hash:str|None=None

    def content_hash(self)->str:
        payload={
            "id":self.id,"entity_id":self.entity_id,
            "evidence_type":self.evidence_type.value,
            "status":self.status.value,"source":self.source,
            "reference":self.reference,
            "captured_at":self.captured_at.isoformat(),
            "metadata":self.metadata,"previous_hash":self.previous_hash
        }
        return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def now_utc()->datetime:
    return datetime.now(timezone.utc)
