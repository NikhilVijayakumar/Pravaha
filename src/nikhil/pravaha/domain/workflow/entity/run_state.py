from enum import Enum

class RunState(str, Enum):
    NEW = "NEW"  # Node waiting in queue, dependencies not met
    PENDING = "PENDING"  # Node ready to execute, waiting for client pickup
    IN_PROGRESS = "IN_PROGRESS"  # Client is currently executing this node
    RUNNING = "RUNNING"  # Overall run status (for compatibility)
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
