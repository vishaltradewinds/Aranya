# Madhya Pradesh Regulatory Pack — Baseline

This is an executable configuration baseline, not legal advice and not a statutory decision engine.

## Authority sources checked

The Madhya Pradesh Forest Department currently publishes notifications covering the 2022 Abhivahan (Forest Produce) Rules, amendments/notifications concerning forest-produce transit, and a 2022 notification concerning bamboo transit authorization fees. The Department's official material also describes the 2005 biodiversity and sustainable-harvesting rules. citeturn0search4turn0search26

A recent Madhya Pradesh High Court judgment discussing the transit framework states that Rule 3 regulates movement of forest produce into/out of/within Madhya Pradesh through prescribed transit passes, subject to specified exemptions, and distinguishes government forest produce from privately grown/owned forest produce under Rule 4A/4B. ARANYA therefore must not assume one rule applies identically to all source types. citeturn0search24

## ARANYA implementation

Regulatory evaluation inputs are:

**Product + Origin + Activity + Source Type + Evidence + Rule Version**

The engine returns:
- TRADE_ELIGIBLE
- CONDITIONAL
- HOLD
- RESTRICTED
- UNKNOWN

The current baseline intentionally does **not** return TRADE_ELIGIBLE. It identifies applicable requirements and keeps unresolved cases conditional/unknown until the evidence and authoritative determination are available.

## Initial MP rule families

1. Forest-produce movement/transit controls.
2. Bamboo-specific movement/authorization requirements.
3. Biodiversity and sustainable-harvesting controls.
4. Product/source-specific rules to be added only after authoritative verification.

## Critical governance rule

ARANYA facilitates compliance and interoperability. It does not replace the Forest Department or another competent statutory authority. A rule record must carry its authority, source reference, version and effective date.

Before real pilot onboarding, the MP pack must be expanded into a versioned rule catalogue with authoritative source documents, exemptions, species/product classifications, source-type distinctions, competent authorities, fees, forms, pass workflows, effective dates and test cases.
