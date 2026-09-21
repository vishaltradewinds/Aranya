import os
os.environ["ARANYA_JWT_SECRET"]="test-secret"
from fastapi.testclient import TestClient
from app.main import app
from app.auth import Principal,Role,issue_token
client=TestClient(app)
def auth(role=Role.PRODUCER,user="producer-001",org="org-001"):
    return {"Authorization":f"Bearer {issue_token(Principal(user,org,role))}"}
def test_health():
    response=client.get("/health"); assert response.status_code==200
def test_auth_required():
    response=client.post("/api/v1/lots",json={"producer_id":"producer-001","product":"bamboo","quantity_kg":500,"origin_state":"Madhya Pradesh","origin_district":"Jabalpur","source_type":"DECLARED"})
    assert response.status_code==401
def test_lot_starts_unknown_and_audited():
    response=client.post("/api/v1/lots",headers=auth(),json={"producer_id":"producer-001","product":"bamboo","species":"Bambusa bambos","quantity_kg":500,"origin_state":"Madhya Pradesh","origin_district":"Jabalpur","source_type":"DECLARED"})
    assert response.status_code==201
    lot=response.json(); assert lot["regulatory_status"]=="UNKNOWN"; assert lot["status"]=="ELIGIBILITY_REVIEW"
    audit_response=client.get(f"/api/v1/audit/{lot['id']}",headers=auth())
    assert audit_response.status_code==200
    assert len(audit_response.json())==1
