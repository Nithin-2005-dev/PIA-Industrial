import logging
from app.knowledge.evidence.ranking import RankingService
from app.intelligence.risk.knowledge_risk_service import KnowledgeRiskService
from app.knowledge.graph.graph_service import GraphService

logger = logging.getLogger(__name__)

class NightlyAnalysisJob:
    """
    Decoupled batch job to run $O(V \\times E)$ algorithms (like PageRank) 
    and recursive N-hop Transitive Risk safely off the real-time event bus.
    """
    
    def __init__(
        self,
        ranking_service: RankingService,
        knowledge_risk_service: KnowledgeRiskService,
        graph_service: GraphService,
    ):
        self._ranking_service = ranking_service
        self._knowledge_risk_service = knowledge_risk_service
        self._graph_service = graph_service

    def run(self) -> None:
        logger.info("Starting Nightly Analysis Job...")
        
        # 1. Execute PageRank globally
        try:
            logger.info("Executing Global PageRank Ranking...")
            self._ranking_service.execute_global_ranking()
        except Exception as e:
            logger.error(f"Failed to execute PageRank: {e}")
            
        # 2. Execute Transitive Risk calculations for all modules
        try:
            logger.info("Executing Transitive Risk Calculations...")
            nodes = self._graph_service.get_nodes()
            for node in nodes:
                # We can trigger the calculation which may internally cache the result
                # or just run it to warm up caches.
                # Assuming node has an ID.
                node_id = getattr(node, 'id', str(node))
                self._knowledge_risk_service.analyze(node_id)
        except Exception as e:
            logger.error(f"Failed to execute Risk Calculations: {e}")
            
        logger.info("Nightly Analysis Job completed.")
