import logging
from typing import List, Dict, Set, Optional, Any
from datetime import datetime, timedelta
from ..protocol.orchestration_engine_protocol import OrchestrationEngineProtocol
from ..protocol.run_repository_protocol import RunRepositoryProtocol
from ..entity.workflow import Workflow
from ..entity.workflow_node import WorkflowNode, NodeType
from ..entity.workflow_run import WorkflowRun
from ..entity.run_state import RunState

logger = logging.getLogger(__name__)

class SimpleOrchestrationEngine(OrchestrationEngineProtocol):
    """
    Concrete implementation of OrchestrationEngineProtocol.
    
    Manages workflow run state transitions without executing nodes.
    Uses topological sorting to determine execution order and ensures
    sequential execution (one PENDING node at a time).
    """
    
    def __init__(self, run_repository: RunRepositoryProtocol):
        self.run_repository = run_repository
    
    def _get_topological_sort(self, workflow: Workflow) -> List[WorkflowNode]:
        """
        Performs topological sort on the workflow DAG.
        Returns only executable nodes in execution order.
        
        Reused from SimpleWorkflowEngine with modification to filter executable nodes.
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

        # Filter to only executable nodes (APP or UTIL)
        return [node for node in sorted_nodes if node.is_executable()]
    
    def initialize_run(self, workflow: Workflow, run: WorkflowRun) -> WorkflowRun:
        """Initialize run state with all nodes NEW except root nodes which are PENDING."""
        execution_order = self._get_topological_sort(workflow)
        
        # Mark all nodes as NEW initially
        for node in execution_order:
            run.node_states[node.id] = RunState.NEW
            run.retry_counts[node.id] = 0
        
        # Find root nodes (nodes with no dependencies among executable nodes)
        executable_ids = {node.id for node in execution_order}
        has_dependency = set()
        
        for edge in workflow.edges:
            # Only count dependency if source is also executable
            if edge.source in executable_ids and edge.target in executable_ids:
                has_dependency.add(edge.target)
        
        root_nodes = [node.id for node in execution_order if node.id not in has_dependency]
        
        # Mark first root node as PENDING (sequential execution)
        if root_nodes:
            run.node_states[root_nodes[0]] = RunState.PENDING
            logger.info(f"Initialized run {run.id}: First pending node is {root_nodes[0]}")
        
        # Set run to RUNNING
        run.status = RunState.RUNNING
        run.started_at = datetime.now()
        
        # Persist changes
        self.run_repository.save(run)
        return run
    
    def get_next_pending_node(self, workflow: Workflow, run: WorkflowRun) -> Optional[WorkflowNode]:
        """Get the current PENDING node."""
        if run.status != RunState.RUNNING:
            return None
        
        # Find pending node
        for node_id, state in run.node_states.items():
            if state == RunState.PENDING:
                nodes_by_id = {n.id: n for n in workflow.nodes}
                return nodes_by_id.get(node_id)
        
        return None
    
    def mark_node_in_progress(self, run: WorkflowRun, node_id: str) -> WorkflowRun:
        """Transition node from PENDING to IN_PROGRESS."""
        current_state = run.node_states.get(node_id)
        
        if current_state != RunState.PENDING:
            raise ValueError(f"Node {node_id} is not PENDING (current: {current_state})")
        
        run.node_states[node_id] = RunState.IN_PROGRESS
        
        # Store timestamp for stale node detection
        if node_id not in run.node_outputs:
            run.node_outputs[node_id] = {}
        run.node_outputs[node_id]['started_at'] = datetime.now().isoformat()
        
        self.run_repository.save(run)
        logger.info(f"Node {node_id} marked IN_PROGRESS in run {run.id}")
        return run
    
    def complete_node(
        self, 
        run: WorkflowRun, 
        workflow: Workflow, 
        node_id: str, 
        output_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowRun:
        """Complete node and advance topology."""
        current_state = run.node_states.get(node_id)
        
        if current_state != RunState.IN_PROGRESS:
            raise ValueError(f"Node {node_id} is not IN_PROGRESS (current: {current_state})")
        
        # Mark node as COMPLETED
        run.node_states[node_id] = RunState.COMPLETED
        
        # Store output data
        run.node_outputs[node_id] = {
            'data': output_data or {},
            'timestamp': datetime.now().isoformat(),
            'version': 1  # Simple versioning
        }
        
        logger.info(f"Node {node_id} completed in run {run.id}")
        
        # Check if all nodes completed
        execution_order = self._get_topological_sort(workflow)
        all_completed = all(
            run.node_states.get(node.id) == RunState.COMPLETED 
            for node in execution_order
        )
        
        if all_completed:
            run.status = RunState.COMPLETED
            run.completed_at = datetime.now()
            logger.info(f"Run {run.id} completed - all nodes finished")
        else:
            # Advance topology: find next node to mark PENDING
            next_node = self._find_next_pending_node(run, workflow, execution_order)
            if next_node:
                run.node_states[next_node.id] = RunState.PENDING
                logger.info(f"Next pending node in run {run.id}: {next_node.id}")
        
        self.run_repository.save(run)
        return run
    
    def _find_next_pending_node(
        self, 
        run: WorkflowRun, 
        workflow: Workflow,
        execution_order: List[WorkflowNode]
    ) -> Optional[WorkflowNode]:
        """Find the next node that should be marked PENDING based on dependencies."""
        executable_ids = {node.id for node in execution_order}
        
        # Build dependency map (only executable nodes)
        dependencies: Dict[str, Set[str]] = {node.id: set() for node in execution_order}
        for edge in workflow.edges:
            if edge.source in executable_ids and edge.target in executable_ids:
                dependencies[edge.target].add(edge.source)
        
        # Find first NEW node whose dependencies are all COMPLETED
        for node in execution_order:
            if run.node_states.get(node.id) == RunState.NEW:
                deps = dependencies[node.id]
                if all(run.node_states.get(dep_id) == RunState.COMPLETED for dep_id in deps):
                    return node
        
        return None
    
    def fail_node(
        self, 
        run: WorkflowRun, 
        node_id: str, 
        error: str, 
        retry: bool = False,
        max_retries: int = 3
    ) -> WorkflowRun:
        """Fail node with optional retry logic."""
        current_retry_count = run.retry_counts.get(node_id, 0)
        
        if retry and current_retry_count < max_retries:
            # Retry: increment count and reset to PENDING
            run.retry_counts[node_id] = current_retry_count + 1
            run.node_states[node_id] = RunState.PENDING
            logger.warning(
                f"Node {node_id} failed in run {run.id}, retrying "
                f"(attempt {run.retry_counts[node_id]}/{max_retries}): {error}"
            )
        else:
            # Max retries exceeded or retry not requested: mark FAILED
            run.node_states[node_id] = RunState.FAILED
            run.status = RunState.FAILED
            run.error_message = f"Node {node_id} failed: {error}"
            run.completed_at = datetime.now()
            logger.error(f"Node {node_id} failed in run {run.id} (no retry): {error}")
        
        self.run_repository.save(run)
        return run
    
    def check_stale_nodes(self, run: WorkflowRun, timeout_minutes: int = 5) -> WorkflowRun:
        """Check for orphaned nodes stuck IN_PROGRESS."""
        if run.status != RunState.RUNNING:
            return run
        
        now = datetime.now()
        stale_found = False
        
        for node_id, state in run.node_states.items():
            if state == RunState.IN_PROGRESS:
                # Check if node has timestamp
                node_output = run.node_outputs.get(node_id, {})
                started_at_str = node_output.get('started_at')
                
                if started_at_str:
                    started_at = datetime.fromisoformat(started_at_str)
                    elapsed = now - started_at
                    
                    if elapsed > timedelta(minutes=timeout_minutes):
                        # Mark as FAILED
                        run.node_states[node_id] = RunState.FAILED
                        run.status = RunState.FAILED
                        run.error_message = f"Node {node_id} timed out (orphaned after {timeout_minutes} minutes)"
                        run.completed_at = now
                        stale_found = True
                        logger.warning(f"Stale node {node_id} detected in run {run.id} - marking as FAILED")
        
        if stale_found:
            self.run_repository.save(run)
        
        return run
