from typing import Dict, Any, List
from app.infrastructure.database.models import KnowledgeGraphProjectionRecord

class ValidationContractResult:
    def __init__(self, name: str, status: str, score: float, findings: List[str], recommendations: List[str]):
        self.name = name
        self.status = status # 'PASS', 'WARN', 'FAIL'
        self.score = score # 0.0 to 100.0
        self.findings = findings
        self.recommendations = recommendations

class BaseContract:
    @classmethod
    def evaluate(cls, projection: KnowledgeGraphProjectionRecord) -> ValidationContractResult:
        raise NotImplementedError

class IdentityContract(BaseContract):
    @classmethod
    def evaluate(cls, projection: KnowledgeGraphProjectionRecord) -> ValidationContractResult:
        findings = []
        score = 100.0
        
        if not projection.projection_id:
            findings.append("Missing projection_id (UUID).")
            score -= 50
        if not projection.projection_hash:
            findings.append("Missing projection_hash (content-addressed hash).")
            score -= 50
            
        status = "PASS" if score == 100.0 else ("FAIL" if score == 0 else "WARN")
        return ValidationContractResult("Identity", status, max(0.0, score), findings, [])

class SchemaContract(BaseContract):
    @classmethod
    def evaluate(cls, projection: KnowledgeGraphProjectionRecord) -> ValidationContractResult:
        findings = []
        score = 100.0
        canonical_types = {"MEASUREMENT", "EVIDENCE", "DEVELOPER", "FILE", "MODULE", "REPOSITORY", "COMMIT"}
        
        unknown_types = set()
        for n in projection.nodes:
            if n.get("type", "").upper() not in canonical_types:
                unknown_types.add(n.get("type", ""))
                
        if unknown_types:
            findings.append(f"Unknown semantic types found: {unknown_types}")
            score -= 50
            
        status = "PASS" if score == 100.0 else "FAIL"
        return ValidationContractResult("Schema", status, max(0.0, score), findings, [])

class TopologyContract(BaseContract):
    @classmethod
    def evaluate(cls, projection: KnowledgeGraphProjectionRecord) -> ValidationContractResult:
        findings = []
        
        adj = {n["id"]: [] for n in projection.nodes}
        for e in projection.edges:
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
        for n in projection.nodes:
            if n["id"] not in visited:
                dfs(n["id"])
                components += 1
                
        score = 100.0
        if components > 1:
            findings.append(f"Graph is fragmented into {components} components.")
            score = 95.0 # Minor penalty since fragmentation is natural without global_repo
        
        return ValidationContractResult("Topology", "PASS", score, findings, [])

class ProvenanceContract(BaseContract):
    @classmethod
    def evaluate(cls, projection: KnowledgeGraphProjectionRecord) -> ValidationContractResult:
        findings = []
        
        nodes_with_provenance = sum(1 for n in projection.nodes if n.get("attributes", {}).get("provenance"))
        edges_with_provenance = sum(1 for e in projection.edges if e.get("provenance"))
        
        node_coverage = (nodes_with_provenance / len(projection.nodes)) * 100 if projection.nodes else 100.0
        edge_coverage = (edges_with_provenance / len(projection.edges)) * 100 if projection.edges else 100.0
        
        score = (node_coverage + edge_coverage) / 2.0
        status = "PASS" if score == 100.0 else "WARN"
        
        if score < 100.0:
            findings.append(f"Node provenance coverage: {node_coverage:.1f}%")
            findings.append(f"Edge provenance coverage: {edge_coverage:.1f}%")
            
        return ValidationContractResult("Provenance", status, score, findings, [])

class LayeredValidator:
    @classmethod
    def validate(cls, projection: KnowledgeGraphProjectionRecord) -> Dict[str, Any]:
        contracts = [
            IdentityContract,
            SchemaContract,
            TopologyContract,
            ProvenanceContract
        ]
        
        results = [c.evaluate(projection) for c in contracts]
        overall_score = sum(r.score for r in results) / len(results) if results else 100.0
        passed = all(r.status != "FAIL" for r in results)
        
        report = {
            "overall_score": overall_score,
            "passed": passed,
            "contracts": [
                {
                    "name": r.name,
                    "status": r.status,
                    "score": r.score,
                    "findings": r.findings,
                    "recommendations": r.recommendations
                } for r in results
            ]
        }
        return report
