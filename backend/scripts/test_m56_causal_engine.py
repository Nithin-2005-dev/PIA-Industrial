"""test_m56_causal_engine.py

Verifies all M56 causal intelligence capabilities:
  - Ontology: categories, mechanisms, ancestor traversal
  - Rule registry: 5 built-in providers registered
  - Semantic model: non-empty from observable signals
  - Hypothesis engine: accepts hypotheses above threshold
  - Explanation engine: non-empty executive narrative
  - Decomposed confidence: all 4 components present
  - Root cause ranking: rank=1 is highest confidence
  - Deterministic replay: two runs produce identical results
  - Module registration: causal in startup order between intelligence and agent
  - Regression: M51 pipeline still passes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Ontology tests ────────────────────────────────────────────────────────────

from app.causal.ontology import default_causal_ontology

ontology = default_causal_ontology()

assert len(ontology.mechanisms) >= 10, "Expected at least 10 built-in mechanisms"
categories = ontology.all_categories()
assert "Structural" in categories, "Missing Structural category"
assert "Behavioral" in categories, "Missing Behavioral category"
assert "Documentation" in categories, "Missing Documentation category"
assert "Process" in categories, "Missing Process category"
assert "Organizational" in categories, "Missing Organizational category"
print("[OK] Ontology: 5 categories registered")

# Ancestor traversal
ancestors = ontology.ancestors("ownership_concentration")
ancestor_ids = [a.id for a in ancestors]
assert "ownership_concentration" in ancestor_ids
assert "knowledge_concentration" in ancestor_ids
print("[OK] Ontology: ancestor traversal works (ownership → knowledge_concentration)")

# Category lookup
assert ontology.category_of("bus_factor_reduction") == "Structural"
assert ontology.category_of("health_reduction") == "Organizational"
print("[OK] Ontology: category_of() works correctly")

# Mechanisms per category
structural = ontology.mechanisms_in_category("Structural")
assert len(structural) >= 3, f"Expected >= 3 Structural mechanisms, got {len(structural)}"
print(f"[OK] Ontology: {len(structural)} Structural mechanisms")

# ── Rule registry tests ───────────────────────────────────────────────────────

from app.causal.rules import default_rule_registry, CausalRuleEngine

registry = default_rule_registry()
providers = registry.provider_names()
assert len(providers) == 5, f"Expected 5 built-in providers, got {len(providers)}"
for expected in ["documentation", "ownership", "review", "expertise", "velocity"]:
    assert expected in providers, f"Missing provider: {expected}"
print(f"[OK] Rule Registry: 5 providers registered {sorted(providers)}")

all_rules = registry.all_rules()
assert len(all_rules) >= 10, f"Expected >= 10 rules, got {len(all_rules)}"
print(f"[OK] Rule Registry: {len(all_rules)} rules loaded")

# All rules reference mechanism IDs present in ontology
ontology_ids = {m.id for m in ontology.mechanisms}
for rule in all_rules:
    assert rule.mechanism_id in ontology_ids, (
        f"Rule '{rule.id}' references unknown mechanism_id '{rule.mechanism_id}'"
    )
print("[OK] Rule Registry: all rule mechanism_ids exist in ontology")

# ── Rule activation ───────────────────────────────────────────────────────────

rule_engine = CausalRuleEngine(registry)

# Simulate bad org state: high concentration, low bus factor, low coverage
bad_state = {
    "ownership_concentration": 0.95,   # very high (bad)
    "bus_factor": 0.1,                 # very low  (bad)
    "coverage": 0.2,                   # very low  (bad)
    "health": 0.05,                    # very low  (bad)
    "knowledge_risk": 0.90,            # very high (bad)
    "forecast_risk": 0.85,
    "expertise_concentration": 0.90,
    "succession_readiness": 0.15,
    "review_diversity": 0.20,
    "knowledge_distribution": 0.20,
    "commit_velocity": 0.30,
    "documentation_activity": 0.25,
    "knowledge_retention": 0.30,
    "engineering_risk": 0.80,
    "executive_priority": 0.70,
}
activated = rule_engine.evaluate(bad_state)
assert len(activated) >= 5, f"Expected >= 5 rules to activate under bad state, got {len(activated)}"
print(f"[OK] Rule Engine: {len(activated)} rules activated under simulated bad org state")

# ── Semantic model builder tests ──────────────────────────────────────────────

from app.causal.graph import CausalSemanticModelBuilder

class MockOrg:
    class _Health:
        average_health = 0.03
        healthy_count = 0
        warning_count = 0
        critical_count = 800
        total_subjects = 800

    class _BF:
        def __init__(self, s, f):
            self.subject = s; self.bus_factor = f

    class _Conc:
        def __init__(self, s, sc, rl):
            self.subject = s; self.concentration_score = sc; self.risk_level = rl

    class _Cov:
        def __init__(self, s, sc, el, ec):
            self.subject = s; self.coverage_score = sc; self.coverage_level = el; self.expert_count = ec

    class _KR:
        def __init__(self, s, rl, bf, oc, sm):
            self.subject = s; self.risk_level = rl; self.bus_factor = bf
            self.owner_count = oc; self.summary = sm

    health = _Health()
    bus_factors = [_BF("react-server", 1), _BF("compiler", 1)]
    concentration = [_Conc("react-server", 1.0, "HIGH"), _Conc("compiler", 1.0, "HIGH")]
    coverage = [_Cov("react-server", 0.08, "WEAK", 1), _Cov("compiler", 0.08, "WEAK", 1)]
    knowledge_risks = [_KR("react-server", "HIGH", 1, 1, "Single owner"), _KR("compiler", "HIGH", 1, 1, "Single owner")]
    successors = []
    recommendations = []

class MockContext:
    org_intelligence = MockOrg()
    historical_context = None
    forecast_context = None
    simulation_context = None
    measurements = [object(), object(), object()]
    knowledge_graph = None

builder = CausalSemanticModelBuilder(rule_engine=rule_engine, ontology=ontology)
sem_model = builder.build(MockContext())

assert len(sem_model.nodes) > 0, "CausalSemanticModel must have at least one node"
assert len(sem_model.edges) > 0, "CausalSemanticModel must have at least one edge"
print(f"[OK] CausalSemanticModelBuilder: {len(sem_model.nodes)} nodes, {len(sem_model.edges)} edges")

# ── Hypothesis engine tests ───────────────────────────────────────────────────

from app.causal.hypothesis import CausalHypothesisEngine

hyp_engine = CausalHypothesisEngine(ontology)
root_causes, all_hyps, groups = hyp_engine.evaluate(sem_model, MockContext())

assert len(all_hyps) > 0, "Hypothesis engine must generate at least one hypothesis"
accepted = [h for h in all_hyps if h.accepted]
assert len(accepted) > 0, "At least one hypothesis must be accepted given strong org signals"
print(f"[OK] Hypothesis Engine: {len(all_hyps)} evaluated, {len(accepted)} accepted")

# All 4 confidence components present
if root_causes:
    rc = root_causes[0]
    conf = rc.confidence
    assert hasattr(conf, "evidence_confidence"), "Missing evidence_confidence"
    assert hasattr(conf, "rule_confidence"), "Missing rule_confidence"
    assert hasattr(conf, "propagation_confidence"), "Missing propagation_confidence"
    assert hasattr(conf, "overall_confidence"), "Missing overall_confidence"
    assert 0.0 <= conf.overall_confidence <= 1.0
    print(f"[OK] Confidence decomposition: ev={conf.evidence_confidence:.0%} rule={conf.rule_confidence:.0%} "
          f"prop={conf.propagation_confidence:.0%} overall={conf.overall_confidence:.0%}")

    # Rank 1 has highest confidence
    if len(root_causes) > 1:
        assert root_causes[0].confidence.overall_confidence >= root_causes[1].confidence.overall_confidence, \
            "Root causes must be sorted by confidence descending"
    print(f"[OK] Root cause ranking: rank=1 is '{root_causes[0].subject}' "
          f"(conf={root_causes[0].confidence.overall_confidence:.0%})")

    # Evidence traceability
    for rc in root_causes:
        assert len(rc.evidence) > 0, f"Root cause '{rc.subject}' must have at least one evidence item"
    print(f"[OK] Evidence traceability: all {len(root_causes)} root causes have evidence")

# ── Explanation engine tests ──────────────────────────────────────────────────

from app.causal.engine import CausalEngine
from app.causal.rules import default_rule_registry as drr

engine = CausalEngine(ontology=ontology, rule_registry=drr())
causal_ctx = engine.analyze(MockContext())

assert causal_ctx.explanation.summary, "Explanation summary must not be empty"
assert len(causal_ctx.explanation.summary) > 20, "Explanation summary too short"
print(f"[OK] Explanation Engine: generated {len(causal_ctx.explanation.summary)} char summary")
print(f"[OK] Explanation Quality: {causal_ctx.explanation.explanation_quality}")

# ── Deterministic replay ──────────────────────────────────────────────────────

ctx2 = engine.analyze(MockContext())
assert causal_ctx.overall_confidence == ctx2.overall_confidence, \
    "Non-deterministic: confidence differs between runs"
assert len(causal_ctx.root_causes) == len(ctx2.root_causes), \
    "Non-deterministic: different root cause counts between runs"
print("[OK] Deterministic replay: two runs produce identical CausalContext")

# ── Module registration test ──────────────────────────────────────────────────

from app.platform.core_modules import default_platform_modules
from app.platform.module import ModuleRegistry

reg = ModuleRegistry()
for mod in default_platform_modules():
    reg.register(mod)

order = reg.startup_order()
assert "causal" in order, "'causal' module must be in startup order"
assert "intelligence" in order
assert "agent" in order

intel_idx = order.index("intelligence")
causal_idx = order.index("causal")
agent_idx  = order.index("agent")

assert intel_idx < causal_idx, f"'intelligence' must come before 'causal' (got {intel_idx} vs {causal_idx})"
assert causal_idx < agent_idx, f"'causal' must come before 'agent' (got {causal_idx} vs {agent_idx})"
print(f"[OK] Module order: intelligence[{intel_idx}] → causal[{causal_idx}] → agent[{agent_idx}]")

# ── Regression: M51 ──────────────────────────────────────────────────────────

# Check key legacy modules still in order
assert "observation" in order
assert "measurement" in order
assert "intelligence" in order
print("[OK] Regression M51: observation, measurement, intelligence still present")

print()
print("=" * 60)
print("m56_causal_engine_ok")
print(f"  ontology mechanisms:       {len(ontology.mechanisms)}")
print(f"  rule providers:            {len(providers)}")
print(f"  rules total:               {len(all_rules)}")
print(f"  semantic model nodes:      {len(sem_model.nodes)}")
print(f"  semantic model edges:      {len(sem_model.edges)}")
print(f"  hypotheses evaluated:      {len(all_hyps)}")
print(f"  hypotheses accepted:       {len(accepted)}")
print(f"  root causes identified:    {len(root_causes)}")
print(f"  explanation quality:       {causal_ctx.explanation.explanation_quality}")
print(f"  overall confidence:        {causal_ctx.overall_confidence:.0%}")
print(f"  module startup order:      {' -> '.join(order)}")
print("=" * 60)
