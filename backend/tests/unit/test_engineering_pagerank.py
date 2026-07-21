import pytest
from app.knowledge.evidence.ranking.ranking import OrganizationalPageRankEngine

def test_engineering_pagerank_dynamic_inversion():
    engine = OrganizationalPageRankEngine(damping_factor=0.85, max_iterations=100)
    
    # 1. The Scenario: Create a mock graph with 10 nodes.
    nodes = [
        "Dev_A", "Dev_B", "Dev_C",
        "CSS_File_1", "CSS_File_2", "CSS_File_3", "CSS_File_4", "CSS_File_5",
        "Core_Router", "Random_Node"
    ]
    
    edges = []
    
    # Dev_A (The Grinder) connects to 5 isolated CSS_File nodes via AUTHORED
    for i in range(1, 6):
        edges.append({"source": "Dev_A", "target": f"CSS_File_{i}", "type": "AUTHORED", "weight": 1.0})
        
    # Dev_B (The Architect) connects to 1 Core_Router module via AUTHORED
    edges.append({"source": "Dev_B", "target": "Core_Router", "type": "AUTHORED", "weight": 1.0})
    
    # The 5 CSS_File nodes all connect back to the Core_Router node via DEPENDS_ON
    for i in range(1, 6):
        edges.append({"source": f"CSS_File_{i}", "target": "Core_Router", "type": "DEPENDS_ON", "weight": 1.0})
        
    # Dev_C (The Liability) connects to Core_Router via INTRODUCED_BUG_IN
    edges.append({"source": "Dev_C", "target": "Core_Router", "type": "INTRODUCED_BUG_IN", "weight": 1.0})
    
    # 2. Execute
    ranks = engine.calculate_authority(nodes, edges)
    
    # 3. Assert
    # Assert that ranks['Dev_B'] is significantly greater than ranks['Dev_A']
    assert ranks['Dev_B'] > ranks['Dev_A'], "Gravity should defeat Volume"
    
    # Assert that ranks['Dev_C'] does not mathematically benefit from the bug injection
    # In standard PageRank without topological inversion, Dev_C might gain rank because Core_Router is important.
    # With topological inversion, the gravity flows FROM Dev_C TO Core_Router, penalizing Dev_C's authority.
    assert ranks['Dev_C'] <= (1.0 / len(nodes)) + 0.05, "Dev_C should have baseline or lower authority"
    assert ranks['Core_Router'] > ranks['Dev_C'], "Core_Router should absorb the gravity"
    assert ranks['Dev_C'] < ranks['Dev_A'], "The Liability should have less rank than The Grinder"
