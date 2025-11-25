# src.nikhil.pravaha.domain.api.protocol.bot_manager_protocol
from typing import Protocol, Iterable, AsyncIterable, Any, Union, TypeVar
from enum import Enum

# Define TypeVars constrained by the base Enum type
UT = TypeVar('UT', bound=Enum) # Utility Task Type
AT = TypeVar('AT', bound=Enum) # Application Task Type


class BotManagerProtocol(Protocol[UT, AT]):
    """
    Protocol for the Bot Manager, parameterized by the Utility and Application Enum types.
    """
    def run(self, utility_task: UT) -> Any:
        """Synchronous execution of a utility task (typed by UT)."""
        ...

    def stream_run(self, application_task: AT) -> Union[Iterable[str], AsyncIterable[str]]:
        """Streamable execution of an application task (typed by AT)."""
        ...