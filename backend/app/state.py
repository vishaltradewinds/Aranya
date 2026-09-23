from enum import Enum

class LotStatus(str, Enum):
    DRAFT="DRAFT"
    ELIGIBILITY_REVIEW="ELIGIBILITY_REVIEW"
    TRADE_ELIGIBLE="TRADE_ELIGIBLE"
    CONDITIONAL="CONDITIONAL"
    HOLD="HOLD"
    RESTRICTED="RESTRICTED"
    UNKNOWN="UNKNOWN"
    MATCHED="MATCHED"
    ORDERED="ORDERED"
    IN_TRANSIT="IN_TRANSIT"
    DELIVERED="DELIVERED"
    SETTLED="SETTLED"

ALLOWED_TRANSITIONS={
    LotStatus.DRAFT:{LotStatus.ELIGIBILITY_REVIEW},
    LotStatus.ELIGIBILITY_REVIEW:{LotStatus.TRADE_ELIGIBLE,LotStatus.CONDITIONAL,LotStatus.HOLD,LotStatus.RESTRICTED,LotStatus.UNKNOWN},
    LotStatus.CONDITIONAL:{LotStatus.MATCHED,LotStatus.HOLD,LotStatus.RESTRICTED},
    LotStatus.TRADE_ELIGIBLE:{LotStatus.MATCHED,LotStatus.HOLD,LotStatus.RESTRICTED},
    LotStatus.MATCHED:{LotStatus.ORDERED,LotStatus.HOLD},
    LotStatus.ORDERED:{LotStatus.IN_TRANSIT,LotStatus.HOLD},
    LotStatus.IN_TRANSIT:{LotStatus.DELIVERED,LotStatus.HOLD},
    LotStatus.DELIVERED:{LotStatus.SETTLED},
    LotStatus.HOLD:{LotStatus.ELIGIBILITY_REVIEW,LotStatus.RESTRICTED},
    LotStatus.UNKNOWN:{LotStatus.ELIGIBILITY_REVIEW,LotStatus.HOLD,LotStatus.RESTRICTED},
    LotStatus.RESTRICTED:set(),
    LotStatus.SETTLED:set(),
}

def can_transition(current:LotStatus,target:LotStatus)->bool:
    return target in ALLOWED_TRANSITIONS.get(current,set())
