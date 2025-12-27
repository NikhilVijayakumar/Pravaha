import asyncio
from typing import Dict, Any, List, Optional, AsyncIterable
from pravaha.domain.bot.model.application_request import ApplicationRequest

class MathBot:
    async def stream_run(self, inputs: Optional[List[Dict[str, Any]]] = None) -> AsyncIterable[str]:
        yield "Hello! I am the Math Assistant.\n"
        await asyncio.sleep(0.1)
        yield "I can help you with simple calculations.\n"
        
        if inputs:
            yield f"You provided {len(inputs)} inputs.\n"
            for inp in inputs:
                 yield f"Processing: {inp}\n"
                 await asyncio.sleep(0.1)
        
        yield "Done."
