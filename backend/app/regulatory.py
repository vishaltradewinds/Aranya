from dataclasses import dataclass, field
from enum import Enum

class RegulatoryStatus(str,Enum):
    TRADE_ELIGIBLE="TRADE_ELIGIBLE"
    CONDITIONAL="CONDITIONAL"
    HOLD="HOLD"
    RESTRICTED="RESTRICTED"
    UNKNOWN="UNKNOWN"

@dataclass(frozen=True)
class Rule:
    rule_id:str
    jurisdiction:str
    product_class:str
    source_type:str|None
    activity:str
    requirement:str
    version:str
    effective_from:str
    authority:str
    source_reference:str

@dataclass(frozen=True)
class RegulatoryContext:
    product_class:str
    origin_state:str
    origin_district:str
    source_type:str
    activity:str
    evidence_status:str
    rule_version:str|None=None

@dataclass(frozen=True)
class RegulatoryDecision:
    status:RegulatoryStatus
    rule_ids:tuple[str,...]
    missing_requirements:tuple[str,...]
    authority:str|None
    reason:str

class RuleRegistry:
    def __init__(self,rules:list[Rule]|None=None):
        self.rules=rules or []

    def evaluate(self,ctx:RegulatoryContext)->RegulatoryDecision:
        matches=[r for r in self.rules
                 if r.jurisdiction==ctx.origin_state
                 and r.product_class==ctx.product_class
                 and r.activity==ctx.activity
                 and (r.source_type is None or r.source_type==ctx.source_type)
                 and (ctx.rule_version is None or r.version==ctx.rule_version)]
        if not matches:
            return RegulatoryDecision(RegulatoryStatus.UNKNOWN,(),("Applicable rule determination",),None,
                                      "No configured rule matched the supplied context.")
        missing=tuple(r.requirement for r in matches if r.requirement)
        if ctx.evidence_status=="CLAIMED":
            return RegulatoryDecision(RegulatoryStatus.CONDITIONAL,tuple(r.rule_id for r in matches),missing,
                                      matches[0].authority,"Evidence is not yet sufficient for an unconditional eligibility determination.")
        return RegulatoryDecision(RegulatoryStatus.CONDITIONAL,tuple(r.rule_id for r in matches),missing,
                                  matches[0].authority,"Applicable requirements require completion/verification; statutory authority remains external.")

MP_BASELINE_RULES=[
 Rule("MP-TRANSIT-2022-CORE","Madhya Pradesh","FOREST_PRODUCE",None,"MOVE",
      "Determine applicable transit-pass requirement before movement.","2022","2022-08-29",
      "Madhya Pradesh Forest Department","MP Abhivahan (Vanopaj) Rules 2022"),
 Rule("MP-BAMBOO-2022-FEE","Madhya Pradesh","BAMBOO",None,"MOVE",
      "Check applicable bamboo transit authorization/fee requirements.","2022","2022-07-12",
      "Madhya Pradesh Forest Department","Government notification 367"),
 Rule("MP-BIODIVERSITY-2005","Madhya Pradesh","FOREST_PRODUCE",None,"HARVEST",
      "Check applicable sustainable-harvesting/closed-area/closed-season controls.","2005","2005-02-03",
      "Madhya Pradesh Forest Department","M.P. Forest Produce (Conservation of Biodiversity and Sustainable Harvesting) Rules 2005"),
]
