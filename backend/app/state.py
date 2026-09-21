from .main import LotStatus

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
def can_transition(current,target):
    return target in ALLOWED_TRANSITIONS.get(current,set())
