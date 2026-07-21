from app.kernel.graph import GraphEngine, NodeType
from app.kernel.resources import ResourceManager
from app.kernel.scheduler import Scheduler, Job

class ResourceAllocator:
    """
    Interfaces recommendations with the ResourceManager to plan capability execution.
    Turns RECOMMENDATION nodes into executable jobs if the platform can self-heal.
    """
    def __init__(self, graph: GraphEngine, resources: ResourceManager, scheduler: Scheduler):
        self.graph = graph
        self.resources = resources
        self.scheduler = scheduler
        
    def allocate_mitigations(self):
        recs = self.graph.get_all_nodes(NodeType.RECOMMENDATION)
        for rec in recs:
            if rec.properties.get("status") == "PENDING_ALLOCATION":
                # Mock allocation logic for Phase 4
                # In a real system we'd map "Trigger cross-training" to a capability ID like "cap_cross_training"
                # and submit a Job to the scheduler.
                
                job = Job(
                    id=f"job_mitigate_{rec.id}",
                    capability_id="cap_auto_mitigate",
                    arguments={"action": rec.properties["action"]}
                )
                self.scheduler.submit(job)
                rec.properties["status"] = "ALLOCATED"
                rec.properties["job_id"] = job.id
