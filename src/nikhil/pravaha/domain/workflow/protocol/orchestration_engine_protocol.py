from typing import Protocol, Optional, Dict, Any
from ..entity.workflow import Workflow
from ..entity.workflow_run import WorkflowRun
from ..entity.workflow_node import WorkflowNode

class OrchestrationEngineProtocol(Protocol):
    """
    Protocol for workflow orchestration (state management only, no execution).
    
    This protocol defines the contract for managing workflow run state transitions
    in a client-driven execution model. The orchestration engine is responsible for:
    - Initializing runs and determining initial PENDING nodes
    - Tracking node state transitions (NEW -> PENDING -> IN_PROGRESS -> COMPLETED/FAILED)
    - Advancing the workflow topology based on node completion
    - Handling node failures and retry logic
    
    The engine does NOT execute nodes - that responsibility lies with the client.
    """
    
    def initialize_run(self, workflow: Workflow, run: WorkflowRun) -> WorkflowRun:
        """
        Initialize run state for client-driven execution.
        
        Sets all nodes to NEW state and marks root nodes (no dependencies) as PENDING.
        Sets run status to RUNNING.
        
        Args:
            workflow: The workflow definition
            run: The run instance to initialize
            
        Returns:
            Updated run with initialized node states
        """
        ...
    
    def get_next_pending_node(self, workflow: Workflow, run: WorkflowRun) -> Optional[WorkflowNode]:
        """
        Get the current PENDING node ready for client execution.
        
        Only one node should be PENDING at a time (sequential execution).
        Returns None if no pending node exists or run is not RUNNING.
        Only returns executable nodes (APPLICATION or UTILITY).
        
        Args:
            workflow: The workflow definition
            run: The current run state
            
        Returns:
            The next pending node, or None if workflow complete or no node ready
        """
        ...
    
    def mark_node_in_progress(self, run: WorkflowRun, node_id: str) -> WorkflowRun:
        """
        Transition node from PENDING to IN_PROGRESS.
        
        Should be called by client before starting node execution.
        Validates that node is currently PENDING.
        
        Args:
            run: The current run state
            node_id: ID of the node to mark in progress
            
        Returns:
            Updated run with node marked IN_PROGRESS
            
        Raises:
            ValueError: If node is not in PENDING state
        """
        ...
    
    def complete_node(
        self, 
        run: WorkflowRun, 
        workflow: Workflow, 
        node_id: str, 
        output_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowRun:
        """
        Complete a node and advance workflow topology.
        
        Validates node is IN_PROGRESS, sets to COMPLETED, stores output data,
        and determines next node(s) to mark as PENDING based on DAG dependencies.
        If all nodes completed, sets run status to COMPLETED.
        
        Args:
            run: The current run state
            workflow: The workflow definition
            node_id: ID of the completed node
            output_data: Optional output data from node execution
            
        Returns:
            Updated run with node completed and topology advanced
            
        Raises:
            ValueError: If node is not in IN_PROGRESS state
        """
        ...
    
    def fail_node(
        self, 
        run: WorkflowRun, 
        node_id: str, 
        error: str, 
        retry: bool = False,
        max_retries: int = 3
    ) -> WorkflowRun:
        """
        Fail a node with optional retry logic.
        
        If retry is True and retry count < max_retries:
            - Increments retry count
            - Sets node back to PENDING for retry
        Else:
            - Sets node to FAILED
            - Sets run status to FAILED
            
        Args:
            run: The current run state
            node_id: ID of the failed node
            error: Error message describing the failure
            retry: Whether to retry the node
            max_retries: Maximum number of retry attempts (default 3)
            
        Returns:
            Updated run with node failed or queued for retry
        """
        ...
    
    def check_stale_nodes(self, run: WorkflowRun, timeout_minutes: int = 5) -> WorkflowRun:
        """
        Check for orphaned nodes stuck in IN_PROGRESS state.
        
        Marks nodes that have been IN_PROGRESS longer than timeout as FAILED.
        This handles cases where client crashes or loses connection mid-execution.
        
        Args:
            run: The current run state
            timeout_minutes: Minutes after which IN_PROGRESS node is considered stale
            
        Returns:
            Updated run with stale nodes marked as FAILED
        """
        ...
