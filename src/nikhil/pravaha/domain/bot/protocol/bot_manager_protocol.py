# src.nikhil.pravaha.domain.api.protocol.bot_manager_protocol
from enum import Enum
from typing import Protocol, Iterable, AsyncIterable, Any, Union, TypeVar, Optional, List, Dict

# Define TypeVars constrained by the base Enum type
UT = TypeVar('UT', bound=Enum)  # Utility Task Type
AT = TypeVar('AT', bound=Enum)  # Application Task Type


class BotManagerProtocol(Protocol[UT, AT]):
    """
    Protocol for the Bot Manager, parameterized by the Utility and Application Enum types.
    """

    def run(self, utility_task: UT, inputs: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Synchronous execution of a utility task (typed by UT)."""
        ...

    def stream_run(self, application_task: AT, inputs: Optional[List[Dict[str, Any]]] = None) -> Union[
        Iterable[str], AsyncIterable[str]]:
        """Streamable execution of an application task (typed by AT)."""
        ...

    def get_input_model(self, task: Union[UT, AT]) -> Optional[Any]:
        """Returns the Pydantic model for the task's input."""
        ...

    def get_output_model(self, task: Union[UT, AT]) -> Optional[Any]:
        """Returns the Pydantic model for the task's output."""
        ...
