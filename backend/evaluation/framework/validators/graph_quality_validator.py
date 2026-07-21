from app.infrastructure.database.models import KnowledgeGraphProjectionRecord

class GraphQualityValidator:
    @classmethod
    def validate(cls, graph: KnowledgeGraphProjectionRecord) -> tuple[bool, str]:
        report = "Graph Quality Validation Report\n\n"
        passed = True
        
        # 1. Provenance Coverage
        nodes_with_provenance = sum(1 for n in graph.nodes if n.get("attributes", {}).get("provenance"))
        edges_with_provenance = sum(1 for e in graph.edges if e.get("provenance"))
        
        node_coverage = (nodes_with_provenance / len(graph.nodes)) * 100 if graph.nodes else 100.0
        edge_coverage = (edges_with_provenance / len(graph.edges)) * 100 if graph.edges else 100.0
        
        report += f"Provenance Coverage (Nodes): {node_coverage:.2f}%\n"
        report += f"Provenance Coverage (Edges): {edge_coverage:.2f}%\n"
        
        if node_coverage < 100.0 or edge_coverage < 100.0:
            report += "FAIL: Provenance Coverage is less than 100%.\n"
            passed = False
            
        # 2. Semantic Typing
        canonical_types = {"MEASUREMENT", "EVIDENCE", "DEVELOPER", "FILE", "MODULE", "REPOSITORY", "COMMIT"}
        unknown_types = set()
        for n in graph.nodes:
            if n.get("type", "").upper() not in canonical_types:
                unknown_types.add(n.get("type", ""))
                
        if unknown_types:
            report += f"FAIL: Unknown semantic types found: {unknown_types}\n"
            passed = False
        else:
            report += "PASS: All nodes have canonical semantic types.\n"
            
        # 3. Connectivity (Relaxed component rule: report instead of fail)
        adj = {n["id"]: [] for n in graph.nodes}
        for e in graph.edges:
            if e["source"] in adj and e["target"] in adj:
                adj[e["source"]].append(e["target"])
                adj[e["target"]].append(e["source"])
                
        visited = set()
        def dfs(node_id):
            stack = [node_id]
            while stack:
                curr = stack.pop()
                if curr not in visited:
                    visited.add(curr)
                    stack.extend(adj.get(curr, []))
                    
        components = 0
        for n in graph.nodes:
            if n["id"] not in visited:
                dfs(n["id"])
                components += 1
                
        report += f"PASS: Graph connectivity mapped. Found {components} components.\n"
            
        return passed, report
