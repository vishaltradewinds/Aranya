import os
os.environ.setdefault("ARANYA_JWT_SECRET","test-secret")
from fastapi.testclient import TestClient
from app.main import app
from app.auth import Principal, Role, issue_token

client=TestClient(app)
def auth(role=Role.FPO,user="fpo-001",org="org-fpo"):
    return {"Authorization":f"Bearer {issue_token(Principal(user,org,role))}"}

def test_network_create_and_match():
    producer=client.post("/api/v1/networks",headers=auth(),json={
        "name":"Dindori Producer Network","network_type":"FPO","capabilities":["mahua","aggregation"],"needs":["buyer","logistics"],"jurisdiction":"Madhya Pradesh"
    })
    assert producer.status_code==201
    buyer=client.post("/api/v1/networks",headers=auth(),json={
        "name":"Herbal Buyer Network","network_type":"BUYER","capabilities":["buyer","procurement"],"needs":["mahua"],"jurisdiction":"India"
    })
    assert buyer.status_code==201
    matches=client.get(f"/api/v1/networks/{producer.json()['id']}/matches",headers=auth())
    assert matches.status_code==200
    assert any(x["network"]["id"]==buyer.json()["id"] for x in matches.json())

def test_network_requires_auth():
    assert client.get("/api/v1/networks").status_code==401
