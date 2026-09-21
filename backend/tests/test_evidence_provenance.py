from datetime import datetime, timezone
from app.evidence import EvidenceItem,EvidenceType,EvidenceStatus
from app.provenance import ProvenanceEvent,validate_event_chain

def test_evidence_hash_is_deterministic():
    e=EvidenceItem("ev1","lot1",EvidenceType.ORIGIN,EvidenceStatus.DOCUMENTED,
                   "supplier","doc-1",datetime(2026,1,1,tzinfo=timezone.utc),{})
    assert e.content_hash()==e.content_hash()
    assert len(e.content_hash())==64

def test_provenance_chain():
    t=datetime(2026,1,1,tzinfo=timezone.utc)
    a=ProvenanceEvent("e1","lot1","LOT_CREATED","u1","MP",500,("ev1",),t)
    b=ProvenanceEvent("e2","lot1","WEIGHED","u2","MP",498,("ev2",),t,None)
    assert not validate_event_chain([a,b])
    b=ProvenanceEvent("e2","lot1","WEIGHED","u2","MP",498,("ev2",),t,"e1")
    assert validate_event_chain([a,b])
