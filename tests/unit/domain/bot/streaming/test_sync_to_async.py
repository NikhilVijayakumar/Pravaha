import pytest
import asyncio
from pravaha.domain.api.streaming.sync_to_async import stream_from_sync_iterable

@pytest.mark.asyncio
async def test_sync_to_async_iterator_success():
    sync_data = ["item1", "item2", "item3"]
    
    async_gen = stream_from_sync_iterable(sync_data)
    
    results = []
    async for item in async_gen:
        results.append(item)
    
    assert results == sync_data

@pytest.mark.asyncio
async def test_sync_to_async_iterator_empty():
    sync_data = []
    
    async_gen = stream_from_sync_iterable(sync_data)
    
    results = []
    async for item in async_gen:
        results.append(item)
    
    assert results == []

@pytest.mark.asyncio
async def test_sync_to_async_iterator_exception():
    def error_gen():
        yield "item1"
        raise ValueError("Test Error")
    
    async_gen = stream_from_sync_iterable(error_gen())
    
    results = []
    with pytest.raises(ValueError, match="Test Error"):
        async for item in async_gen:
            results.append(item)
    
    assert results == ["item1"]
