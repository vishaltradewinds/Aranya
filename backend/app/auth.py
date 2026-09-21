import os\nfrom datetime import datetime, timedelta, timezone\nimport jwt\nfrom fastapi import Depends, HTTPException, status\nfrom fastapi.security import HTTPAuthorizationCredentials, HTTPBearer\n\nfrom dataclasses import dataclass
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
    Role.PRODUCER: {"lot:create","lot:read:self","audit:read:self"},
    Role.FPO: {"lot:create","lot:read:org","audit:read:org","lot:transition"},
    Role.AGGREGATOR: {"lot:read:org","movement:create","audit:read:org","lot:transition"},
    Role.PROCESSOR: {"lot:read:matched","order:create","audit:read:org","lot:transition"},
    Role.BUYER: {"lot:read:market","order:create","audit:read:org","lot:transition"},
    Role.TRANSPORTER: {"movement:read","movement:update","audit:read:assigned","lot:transition"},
    Role.WAREHOUSE: {"lot:read:assigned","movement:update","audit:read:assigned","lot:transition"},
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
\nJWT_ALGORITHM="HS256"\nJWT_SECRET=os.getenv("ARANYA_JWT_SECRET","dev-only-change-me")\nbearer=HTTPBearer(auto_error=False)\n\ndef issue_token(principal:Principal, expires_minutes:int=60)->str:\n    now=datetime.now(timezone.utc)\n    payload={"sub":principal.user_id,"org":principal.organization_id,"role":principal.role.value,"iat":now,"exp":now+timedelta(minutes=expires_minutes)}\n    return jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGORITHM)\n\ndef current_principal(credentials:HTTPAuthorizationCredentials=Depends(bearer))->Principal:\n    if credentials is None: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication required")\n    try:\n        payload=jwt.decode(credentials.credentials,JWT_SECRET,algorithms=[JWT_ALGORITHM])\n        return Principal(str(payload["sub"]),str(payload["org"]),Role(str(payload["role"])))\n    except (jwt.InvalidTokenError,KeyError,ValueError):\n        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid authentication token")\n\ndef require_permission(permission:str):\n    def dependency(principal:Principal=Depends(current_principal))->Principal:\n        if not allowed(principal,permission): raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Permission denied")\n        return principal\n    return dependency\n