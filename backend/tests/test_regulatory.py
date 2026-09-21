from app.regulatory import *

def test_unknown_when_no_rule_matches():
    r=RuleRegistry()
    d=r.evaluate(RegulatoryContext("UNKNOWN","Madhya Pradesh","Jabalpur","PRIVATE","MOVE","CLAIMED"))
    assert d.status==RegulatoryStatus.UNKNOWN

def test_mp_rule_requires_review():
    r=RuleRegistry(MP_BASELINE_RULES)
    d=r.evaluate(RegulatoryContext("BAMBOO","Madhya Pradesh","Jabalpur","PRIVATE","MOVE","CLAIMED"))
    assert d.status==RegulatoryStatus.CONDITIONAL
    assert "MP-BAMBOO-2022-FEE" in d.rule_ids
