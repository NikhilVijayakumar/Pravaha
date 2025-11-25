# src.nikhil.amsha.toolkit.api.streaming.sync_to_async
import asyncio
import threading
from typing import Iterable, AsyncIterator, Any

_SENTINEL = object()

async def stream_from_sync_iterable(sync_iterable: Iterable[Any]) -> AsyncIterator[Any]:
    """
    Convert a synchronous iterable/generator into an async iterator
    without blocking the event loop by using a background thread and an asyncio.Queue.
    Yields items as they arrive.
    """
    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def producer():
        try:
            for item in sync_iterable:
                # schedule a coroutine to put item in the queue
                asyncio.run_coroutine_threadsafe(queue.put(item), loop).result()
        except Exception as e:
            # send an exception marker to the consumer
            asyncio.run_coroutine_threadsafe(queue.put((_SENTINEL, e)), loop).result()
            return
        # Normal completion marker
        asyncio.run_coroutine_threadsafe(queue.put((_SENTINEL, None)), loop).result()

    thread = threading.Thread(target=producer, daemon=True)
    thread.start()

    while True:
        payload = await queue.get()
        if isinstance(payload, tuple) and payload[0] is _SENTINEL:
            # completion marker
            exc = payload[1]
            if exc:
                raise exc
            break
        yield payload
