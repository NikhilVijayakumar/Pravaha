from unittest.mock import AsyncMock, MagicMock
from nikhil.pravaha.domain.workflow.infrastructure.pravaha_task_executor import PravahaTaskExecutor
from nikhil.pravaha.domain.bot.protocol.bot_manager_protocol import BotManagerProtocol

async def test_pravaha_task_executor_calls_app_stream_run():
    # Arrange
    mock_bot_manager = MagicMock(spec=BotManagerProtocol)
    mock_bot_manager.stream_run = AsyncMock(return_value=["chunk1", "chunk2"])
    
    executor = PravahaTaskExecutor(bot_manager=mock_bot_manager)
    task_name = "test_app"
    inputs = [{"key": "value"}]

    # Act
    result = await executor.execute(
        task_type="APPLICATION",
        task_name=task_name,
        inputs=inputs
    )

    # Assert
    mock_bot_manager.stream_run.assert_called_once_with(task_name, inputs=inputs)
    assert result == ["chunk1", "chunk2"]

async def test_pravaha_task_executor_calls_util_run():
    # Arrange
    mock_bot_manager = MagicMock(spec=BotManagerProtocol)
    mock_bot_manager.run = AsyncMock(return_value="util_result")
    
    executor = PravahaTaskExecutor(bot_manager=mock_bot_manager)
    task_name = "test_util"
    inputs = [{"key": "value"}]

    # Act
    result = await executor.execute(
        task_type="UTILITY",
        task_name=task_name,
        inputs=inputs
    )

    # Assert
    mock_bot_manager.run.assert_called_once_with(task_name, inputs=inputs)
    assert result == "util_result"

async def test_pravaha_task_executor_supports_aliases():
    # Arrange
    mock_bot_manager = MagicMock(spec=BotManagerProtocol)
    mock_bot_manager.stream_run = AsyncMock()
    mock_bot_manager.run = AsyncMock()
    executor = PravahaTaskExecutor(bot_manager=mock_bot_manager)

    # Act
    await executor.execute(task_type="APP", task_name="app_task")
    await executor.execute(task_type="UTIL", task_name="util_task")

    # Assert
    mock_bot_manager.stream_run.assert_called_once()
    mock_bot_manager.run.assert_called_once()

if __name__ == "__main__":
    import asyncio
    
    async def run_checks():
        print("Running manual checks...")
        try:
            await test_pravaha_task_executor_calls_app_stream_run()
            print("✓ test_pravaha_task_executor_calls_app_stream_run passed")
            await test_pravaha_task_executor_calls_util_run()
            print("✓ test_pravaha_task_executor_calls_util_run passed")
            await test_pravaha_task_executor_supports_aliases()
            print("✓ test_pravaha_task_executor_supports_aliases passed")
            print("All manual checks passed!")
        except Exception as e:
            print(f"❌ Check failed: {e}")
            raise

    asyncio.run(run_checks())
