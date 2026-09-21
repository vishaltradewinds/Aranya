from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_lot_starts_unknown_and_audited():
    response = client.post("/api/v1/lots", json={
        "producer_id":"producer-001",
        "product":"bamboo",
        "species":"Bambusa bambos",
        "quantity_kg":500,
        "origin_state":"Madhya Pradesh",
        "origin_district":"Jabalpur",
        "source_type":"DECLARED"
    })
    assert response.status_code == 201
    lot=response.json()
    assert lot["regulatory_status"] == "UNKNOWN"
    assert lot["status"] == "ELIGIBILITY_REVIEW"
    audit_response=client.get(f"/api/v1/audit/{lot['id']}")
    assert audit_response.status_code == 200
    assert len(audit_response.json()) == 1
