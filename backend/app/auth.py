import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dataclasses import dataclass
from enum import Enum

class Role(str, Enum):
    PRODUCER="PRODUCER"
    FPO="FPO"
    AGGREGATOR="AGGREGATOR"
    PROCESSOR="PROCESSOR"
    BUYER="BUYER"
    TRANSPORTER="TRANSPORTER"
    WAREHOUSE="WAREHOUSE"
    GOVERNMENT="GOVERNMENT"
    COMPLIANCE="COMPLIANCE"
    RESEARCH="RESEARCH"
    ADMIN="ADMIN"

ROLE_PERMISSIONS={
    Role.PRODUCER: {"lot:create","lot:read","audit:read:self","evidence:create"},
    Role.FPO: {"lot:create","lot:read","audit:read:org","lot:transition","evidence:create"},
    Role.AGGREGATOR: {"lot:read","movement:create","audit:read:org","lot:transition"},
    Role.PROCESSOR: {"lot:read","order:create","audit:read:org","lot:transition"},
    Role.BUYER: {"lot:read","order:create","audit:read:org","lot:transition"},
    Role.TRANSPORTER: {"movement:read","movement:update","audit:read:assigned","lot:transition"},
    Role.WAREHOUSE: {"lot:read","movement:update","audit:read:assigned","lot:transition"},
    Role.GOVERNMENT: {"lot:read:jurisdiction","audit:read:jurisdiction"},
    Role.COMPLIANCE: {"audit:read:jurisdiction","evidence:review","lot:transition"},
    Role.RESEARCH: {"read:anonymized"},
    Role.ADMIN: {"*"},
}

@dataclass(frozen=True)
class Principal:
    user_id:str
    organization_id:str
    role:Role

def allowed(principal:Principal, permission:str)->bool:
    permissions=ROLE_PERMISSIONS.get(principal.role,set())
    return "*" in permissions or permission in permissions

JWT_ALGORITHM="HS256"
JWT_SECRET=os.getenv("ARANYA_JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("ARANYA_JWT_SECRET must be configured")
bearer=HTTPBearer(auto_error=False)

def issue_token(principal:Principal, expires_minutes:int=60)->str:
    now=datetime.now(timezone.utc)
    payload={"sub":principal.user_id,"org":principal.organization_id,"role":principal.role.value,"iat":now,"exp":now+timedelta(minutes=expires_minutes)}
    return jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGORITHM)

def current_principal(credentials:HTTPAuthorizationCredentials=Depends(bearer))->Principal:
    if credentials is None: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication required")
    try:
        payload=jwt.decode(credentials.credentials,JWT_SECRET,algorithms=[JWT_ALGORITHM])
        return Principal(str(payload["sub"]),str(payload["org"]),Role(str(payload["role"])))
    except (jwt.InvalidTokenError,KeyError,ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid authentication token")

def require_permission(permission:str):
    def dependency(principal:Principal=Depends(current_principal))->Principal:
        if not allowed(principal,permission): raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Permission denied")
        return principal
    return dependency
