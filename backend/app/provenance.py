from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ProvenanceEvent:
    event_id:str
    lot_id:str
    event_type:str
    actor_id:str
    location:str|None
    quantity_kg:float|None
    evidence_ids:tuple[str,...]
    occurred_at:datetime
    previous_event_id:str|None=None

def validate_event_chain(events:list[ProvenanceEvent])->bool:
    previous=None
    for event in events:
        if event.previous_event_id != previous:
            return False
        if not event.event_id or not event.lot_id or not event.actor_id:
            return False
        previous=event.event_id
    return True
