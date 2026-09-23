from __future__ import annotations
import hashlib
import os
import boto3
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from .auth import Principal, require_permission
from .db import SessionLocal, EvidenceObjectRecord, EvidenceRecord

router=APIRouter(prefix="/api/v1/evidence-objects",tags=["evidence-objects"])
MAX_BYTES=10*1024*1024
S3_BUCKET=os.getenv("ARANYA_EVIDENCE_BUCKET")
S3_ENDPOINT=os.getenv("ARANYA_EVIDENCE_ENDPOINT")
S3_REGION=os.getenv("ARANYA_EVIDENCE_REGION","auto")
S3_ACCESS_KEY=os.getenv("ARANYA_EVIDENCE_ACCESS_KEY")
S3_SECRET_KEY=os.getenv("ARANYA_EVIDENCE_SECRET_KEY")

def store_object(key:str,data:bytes,content_type:str|None):
    if not S3_BUCKET or not S3_ACCESS_KEY or not S3_SECRET_KEY:
        return None, "RECEIVED"
    client=boto3.client("s3",region_name=S3_REGION,endpoint_url=S3_ENDPOINT or None,aws_access_key_id=S3_ACCESS_KEY,aws_secret_access_key=S3_SECRET_KEY)
    client.put_object(Bucket=S3_BUCKET,Key=key,Body=data,ContentType=content_type or "application/octet-stream")
    return f"s3://{S3_BUCKET}/{key}", "STORED"

@router.post("",status_code=201)
async def upload_evidence(entity_id:str,evidence_type:str,file:UploadFile=File(...),principal:Principal=require_permission("evidence:create")):
    data=await file.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES: raise HTTPException(413,"Evidence object exceeds 10MB limit")
    digest=hashlib.sha256(data).hexdigest()
    object_id=f"AREO-{uuid4().hex[:12].upper()}"
    now=datetime.now(timezone.utc)
    # Storage abstraction: metadata is durable now; object_uri identifies the future S3-compatible/edge object.
    key=f"{entity_id}/{object_id}"
    stored_uri, storage_status = store_object(key,data,file.content_type)
    object_uri=stored_uri or f"evidence://{key}"
    with SessionLocal() as db:
        obj=EvidenceObjectRecord(id=object_id,entity_id=entity_id,evidence_type=evidence_type,object_uri=object_uri,content_hash=digest,mime_type=file.content_type,size_bytes=len(data),captured_by=principal.user_id,captured_at=now,storage_status=storage_status)
        db.add(obj);db.commit()
        return {"id":object_id,"entity_id":entity_id,"evidence_type":evidence_type,"object_uri":object_uri,"content_hash":digest,"mime_type":file.content_type,"size_bytes":len(data),"storage_status":storage_status}

@router.get("/{object_id}")
def get_evidence_object(object_id:str,principal:Principal=require_permission("lot:read")):
    with SessionLocal() as db:
        o=db.get(EvidenceObjectRecord,object_id)
        if not o: raise HTTPException(404,"Evidence object not found")
        return {"id":o.id,"entity_id":o.entity_id,"evidence_type":o.evidence_type,"object_uri":o.object_uri,"content_hash":o.content_hash,"mime_type":o.mime_type,"size_bytes":o.size_bytes,"captured_by":o.captured_by,"captured_at":o.captured_at,"storage_status":o.storage_status}
