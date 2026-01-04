import logging
from typing import List, Dict, Set
from datetime import datetime
from ..protocol.workflow_engine_protocol import WorkflowEngineProtocol
from ..protocol.task_executor_protocol import TaskExecutorProtocol
from ..protocol.run_repository_protocol import RunRepositoryProtocol
from ..entity.workflow import Workflow
from ..entity.workflow_node import WorkflowNode
from ..entity.workflow_run import WorkflowRun
from ..entity.run_state import RunState

logger = logging.getLogger(__name__)

class SimpleWorkflowEngine(WorkflowEngineProtocol):
    def __init__(self, task_executor: TaskExecutorProtocol, run_repository: RunRepositoryProtocol):
        self.task_executor = task_executor
        self.run_repository = run_repository

    def _get_topological_sort(self, workflow: Workflow) -> List[WorkflowNode]:
        """
        Performs topological sort on the workflow DAG.
        Returns a list of nodes in execution order.
        """
        adjacency: Dict[str, List[str]] = {node.id: [] for node in workflow.nodes}
        in_degree: Dict[str, int] = {node.id: 0 for node in workflow.nodes}
        nodes_by_id = {node.id: node for node in workflow.nodes}

        for edge in workflow.edges:
            if edge.source in adjacency and edge.target in in_degree:
                adjacency[edge.source].append(edge.target)
                in_degree[edge.target] += 1

        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        sorted_nodes = []

        while queue:
            u = queue.pop(0)
            sorted_nodes.append(nodes_by_id[u])

            for v in adjacency[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(sorted_nodes) != len(workflow.nodes):
            raise ValueError("Cycle detected in workflow graph")

        return sorted_nodes

    def _resolve_inputs(self, node: WorkflowNode, run: WorkflowRun, workflow: Workflow) -> List[Dict]:
        """
        Resolves input values. If input comes from another node, it assumes the previous node
        returned a value that can be used.
        
        Note: The current specification for `BotManager` inputs is `List[Dict]`.
        RunState tracking only tracks status, not output values.
        
        LIMITATION: To support data passing between nodes, we would need to persist node outputs.
        For this MVP/Spec, we assume inputs are static (configured in UI) OR the execution context handles it.
        However, `InputItem` has `source` which implies value passing.
        
        For now, we will pass the configured inputs as-is. If `source` is present, 
        we would ideally fetch the output of that source node.
        Since `RunRepository` interface does not explicitly allow storing outputs in `node_states` (just Enum),
        we'll log a warning if source-based input is found but not fully supported in this Engine version,
        OR we pass the raw InputItem definitions to the Executor if it can handle them.
        
        The spec says: "The WorkflowEngine executes a node, it passes these inputs to the BotManager." 
        And "BotManager ... handles InputItem -> List[Dict] conversion".
        
        So we just convert our Pydantic InputItems to Dicts/Pydantic objects and pass them.
        """
        # BotManager expects dynamic input, usually straight form the Request model.
        # We will convert our `InputItem` list to list of dicts.
        return [i.model_dump() for i in node.inputs]

    async def execute_run(self, workflow: Workflow, run: WorkflowRun) -> None:
        try:
            # 1. Update Run Status to RUNNING
            run.status = RunState.RUNNING
            run.started_at = datetime.now()
            self.run_repository.save(run)

            # 2. Sort Nodes
            execution_order = self._get_topological_sort(workflow)

            # 3. Iterate
            for node in execution_order:
                # RESUME LOGIC: Check if node is already completed
                current_node_state = run.node_states.get(node.id)
                if current_node_state == RunState.COMPLETED:
                    logger.info(f"Skipping completed node: {node.task_name} ({node.id})")
                    continue
                
                # Update Node State -> RUNNING
                self.run_repository.update_node_state(run.id, node.id, RunState.RUNNING)
                
                try:
                    # Resolve Inputs
                    inputs = self._resolve_inputs(node, run, workflow)
                    
                    # Execute
                    logger.info(f"Executing node: {node.task_name} ({node.id})")
                    # We await the result. If it's a stream, we might want to consume it fully 
                    # to ensure completion, or just trigger it. 
                    # Spec says "Execute workflows deterministically".
                    # If stream=False (default in execute signature we strictly used in repo but let's check),
                    # TaskExecutor protocol has `stream: bool = False`. We should use False here to wait for completion.
                    
                    # For APPLICATION tasks that *only* stream, we might need stream=True and consume it.
                    # But `PravahaTaskExecutor` handles `stream=False` for APPLICATION by wrapping `stream_run`.
                    # So we allow the executor to handle the waiting.
                    
                    result = await self.task_executor.execute(
                        task_type=node.task_type,
                        task_name=node.task_name,
                        inputs=inputs,
                        stream=False # We want to wait for completion
                    )
                    
                    # If result is async generator (double safety check), consume it
                    if hasattr(result, '__aiter__'):
                        async for _ in result: pass

                    # Update Node State -> COMPLETED
                    self.run_repository.update_node_state(run.id, node.id, RunState.COMPLETED)
                
                except Exception as e:
                    logger.error(f"Node execution failed: {node.id}. Error: {e}")
                    self.run_repository.update_node_state(run.id, node.id, RunState.FAILED)
                    run.status = RunState.FAILED
                    run.error_message = str(e)
                    run.completed_at = datetime.now()
                    self.run_repository.save(run)
                    return # Stop execution on failure

            # 4. Finish Run
            run.status = RunState.COMPLETED
            run.completed_at = datetime.now()
            self.run_repository.save(run)

        except Exception as e:
             # Global failures (e.g. cycle detect)
             logger.error(f"Workflow execution failed. Error: {e}")
             run.status = RunState.FAILED
             run.error_message = str(e)
             run.completed_at = datetime.now()
             self.run_repository.save(run)
