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
    Role.PRODUCER: {"lot:create","lot:read:self","audit:read:self"},
    Role.FPO: {"lot:create","lot:read:org","audit:read:org"},
    Role.AGGREGATOR: {"lot:read:org","movement:create","audit:read:org"},
    Role.PROCESSOR: {"lot:read:matched","order:create","audit:read:org"},
    Role.BUYER: {"lot:read:market","order:create","audit:read:org"},
    Role.TRANSPORTER: {"movement:read","movement:update","audit:read:assigned"},
    Role.WAREHOUSE: {"lot:read:assigned","movement:update","audit:read:assigned"},
    Role.GOVERNMENT: {"lot:read:jurisdiction","audit:read:jurisdiction"},
    Role.COMPLIANCE: {"audit:read:jurisdiction","evidence:review"},
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
