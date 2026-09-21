from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    r=client.get("/health"); assert r.status_code==200; assert r.json()["persistence"]=="sqlalchemy"

def test_lot_persists_and_audit_exists():
    r=client.post("/api/v1/lots",json={"producer_id":"producer-001","product":"bamboo","species":"Bambusa bambos","quantity_kg":500,"origin_state":"Madhya Pradesh","origin_district":"Jabalpur","source_type":"DECLARED"})
    assert r.status_code==201
    lot=r.json(); assert lot["regulatory_status"]=="UNKNOWN"
    assert client.get(f"/api/v1/lots/{lot['id']}").status_code==200
    audit=client.get(f"/api/v1/audit/{lot['id']}").json()
    assert len(audit)==1 and audit[0]["action"]=="LOT_CREATED"
