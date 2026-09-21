from app.auth import Principal,Role,allowed
from app.state import can_transition
from app.main import LotStatus

def test_role_permissions():
    assert allowed(Principal("u","o",Role.PRODUCER),"lot:create")
    assert not allowed(Principal("u","o",Role.PRODUCER),"evidence:review")
    assert allowed(Principal("a","o",Role.ADMIN),"evidence:review")

def test_safe_state_transitions():
    assert can_transition(LotStatus.ELIGIBILITY_REVIEW,LotStatus.TRADE_ELIGIBLE)
    assert not can_transition(LotStatus.DELIVERED,LotStatus.IN_TRANSIT)
    assert not can_transition(LotStatus.RESTRICTED,LotStatus.SETTLED)
