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

def test_evidence_chain_is_append_only_and_verifiable():
    response=client.post("/api/v1/lots",headers=auth(),json={"producer_id":"producer-001","product":"bamboo","species":"Bambusa bambos","quantity_kg":100,"origin_state":"Madhya Pradesh","origin_district":"Jabalpur","source_type":"DECLARED"})
    assert response.status_code==201
    lot=response.json()
    lot_id=lot["id"]
    evidence=client.post(f"/api/v1/lots/{lot_id}/evidence",headers=auth(),json={"evidence_type":"ORIGIN","source":"producer-declaration","reference":"doc://origin-001","metadata":{"note":"initial"}})
    assert evidence.status_code==201
    first=evidence.json()
    verify=client.post(f'/api/v1/evidence/{first["id"]}/verify',headers=auth(Role.COMPLIANCE,user="reviewer-001",org="org-compliance"),json={"status":"DOCUMENTED","verifier_note":"document checked"})
    assert verify.status_code==200
    second=verify.json()
    assert second["id"] != first["id"]
    listed=client.get(f"/api/v1/lots/{lot_id}/evidence",headers=auth())
    assert listed.status_code==200
    records=listed.json()
    assert len(records)==2
    assert records[0]["status"]=="CLAIMED"
    assert records[1]["status"]=="DOCUMENTED"
