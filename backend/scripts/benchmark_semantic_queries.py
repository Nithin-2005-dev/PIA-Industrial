import sys
import os
import json

# Add backend to path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.kernel.semantic_parser import SemanticQueryParser
from app.kernel.goal_builder import GoalGraphBuilder
from app.kernel.provider import LLMProvider

class MockProvider(LLMProvider):
    def generate(self, prompt: str, system: str = "", temperature: float = 0.0) -> str:
        # Simple mock for fallback
        if "who is the top developer" in prompt.lower() or "who knows" in prompt.lower():
            return '{"goals": ["FIND_CONTRIBUTOR"], "entities": [{"type": "MODULE", "value": "ReactDOM"}], "scope": "COMPONENT", "confidence": 0.9}'
        return '{"goals": ["UNKNOWN"], "entities": [], "scope": "REPOSITORY", "confidence": 0.0}'
        
    def stream(self, prompt: str, system: str = "", temperature: float = 0.0):
        pass

def main():
    print("\n=== M57.15 Semantic Paraphrase Benchmark ===\n")
    
    provider = MockProvider()
    parser = SemanticQueryParser(provider)
    builder = GoalGraphBuilder()
    
    test_cases = [
        # Group 1: Ownership
        ("Who owns ReactDOM?", "Ownership Group"),
        ("who maintains ReactDOM?", "Ownership Group"),
        ("owner of ReactDOM", "Ownership Group"),
        
        # Group 2: Expertise
        ("Who is the top developer for ReactDOM?", "Expertise Group"),
        ("key authors of ReactDOM", "Expertise Group"),
        ("who knows ReactDOM best", "Expertise Group"),
        
        # Group 3: Bus Factor
        ("bus factor of ReactDOM", "Risk Group"),
        ("knowledge loss in ReactDOM", "Risk Group"),
        
        # Group 4: Simulation
        ("what happens if Dan leaves", "Simulation Group"),
        ("simulate departure of Dan leaves", "Simulation Group"), # testing noise
    ]
    
    results = {}
    
    for query, group in test_cases:
        # Parse query
        sq = parser.parse(query)
        
        # Build graph
        graph = builder.build(sq)
        
        # Hash graph
        graph_hash = graph.hash()
        
        if group not in results:
            results[group] = []
            
        results[group].append({
            "query": query,
            "goals": [g.name for g in sq.goals],
            "entities": [e.value for e in sq.entities],
            "hash": graph_hash
        })
        
    # Evaluate Convergence
    print("Semantic Convergence Results")
    print(f"{'Intent Group':<20} | {'Query Variations':<40} | {'Graph Hash':<15} | {'Convergence'}")
    print("-" * 95)
    
    total_groups = len(results)
    converged_groups = 0
    
    for group, items in results.items():
        hashes = set(item["hash"] for item in items)
        is_converged = len(hashes) == 1
        if is_converged:
            converged_groups += 1
            
        queries_str = "\n".join([i["query"] for i in items])
        hash_val = list(hashes)[0] if is_converged else "DIVERGED"
        
        # We just print the first query for compactness in the table
        first_query = items[0]["query"]
        print(f"{group:<20} | {first_query:<40} | {hash_val:<15} | {'YES' if is_converged else 'NO'}")
        
    print(f"\nOverall Convergence Score: {converged_groups}/{total_groups} ({(converged_groups/total_groups)*100:.1f}%)\n")

if __name__ == "__main__":
    main()
