import os
os.environ.setdefault("ARANYA_JWT_SECRET", "test-secret")
from app.intent import IntentType, understand

def test_hindi_mahua_intent():
    result = understand("Mere paas 500 kilo mahua hai, Dindori se bechna hai")
    assert result.intent_type == IntentType.HAVE
    assert result.object == "mahua"
    assert result.quantity == "500 kilo"
    assert result.journey_key == "resource_to_outcome"

def test_need_intent():
    result = understand("Mujhe 20 tonne bamboo chahiye")
    assert result.intent_type == IntentType.NEED
    assert result.object == "bamboo"
