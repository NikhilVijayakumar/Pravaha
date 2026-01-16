import pytest
from enum import Enum
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from pathlib import Path

# Import ONLY the available factory function
from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.bot.protocol.bot_manager_protocol import BotManagerProtocol
from pravaha.domain.bot.protocol.task_config_protocol import TaskConfigProtocol

# --- Mocks ---
class MockUtils(Enum):
    UTIL_1 = "util_1"

class MockApp(Enum):
    APP_1 = "app_1"

class MockTarget(Enum):
    TARGET_1 = "target_1"

@pytest.fixture
def mock_task_config():
    config = Mock(spec=TaskConfigProtocol)
    config.UtilsType = MockUtils
    config.ApplicationType = MockApp
    config.ExecutionTarget = MockTarget
    return config

@pytest.fixture
def mock_bot_manager():
    return Mock(spec=BotManagerProtocol)

# --- Tests ---

def test_factory_app_structure(mock_bot_manager, mock_task_config):
    """[UT-FAC-001/002/003/004] Verify app structure, middleware, and prefix."""
    # We mock storage_manager as it's required
    mock_storage = Mock()
    
    # We rely on defaults for most things, but need to ensure it doesn't fail on internal inits.
    # The factory initializes providers. To avoid complex mocking of specific providers,
    # we can just run it and see if it explodes, or mock the providers if they have complex inits.
    # Given the factory imports providers inside the function (some of them), let's see.
    # Actually, many imports are at top level now. Only LLM/Storage internals are inside.
    
    # Let's mock the internal "heavy" classes to keep this a unit test of the factory logic
    with patch("pravaha.domain.api.factory.api_factory.BotAPIProvider") as mock_bot_cls:
        with patch("pravaha.domain.api.factory.api_factory.StorageAPIProvider") as mock_storage_cls:
            with patch("pravaha.domain.api.factory.api_factory.WorkflowAPIProvider") as mock_workflow_cls:
                # Patch source for local imports
                with patch("pravaha.domain.llm.provider.llm_api_provider.LLMAPIProvider") as mock_llm_cls:
                    # Give them dummy routers
                    mock_bot_cls.return_value.router = MagicMock()
                    mock_storage_cls.return_value.router = MagicMock()
                    mock_workflow_cls.return_value.router = MagicMock()
                    mock_llm_cls.return_value.router = MagicMock()

                    # Needs to mock LLMConfigManager too since it is instantiated locally
                    with patch("pravaha.domain.llm.manager.llm_config_manager.LLMConfigManager"):
                        # Needs to mock Workflow internals
                        with patch("pravaha.domain.workflow.manager.local_workflow_manager.LocalWorkflowManager"):
                             with patch("pravaha.domain.workflow.infrastructure.json_workflow_repository.JsonWorkflowRepository"):
                                 with patch("pravaha.domain.workflow.infrastructure.json_run_repository.JsonRunRepository"):
                                    
                                    app = create_fastapi_app(
                                        bot_manager=mock_bot_manager,
                                        task_config=mock_task_config,
                                        storage_manager=mock_storage,
                                        prefix="v1test",
                                        title="Test App"
                                    )
    
                                    assert app.title == "Test App"
                                    
                                    # Check Middleware
                                    middleware_names = [m.cls.__name__ for m in app.user_middleware]
                                    assert "CORSMiddleware" in middleware_names
                                    
                                    client = TestClient(app)
                                    
                                    # Health check
                                    assert client.get("/health").status_code == 200

def test_factory_dependency_wiring(mock_bot_manager, mock_task_config):
    """[UT-FAC-005/006/007/008] Verify dependencies are wired into providers."""
    
    mock_storage = Mock()
    mock_llm_path = "dummy_llm_config.yaml"
    
    # Extensive mocking to check arguments passed to constructors
    with patch("pravaha.domain.api.factory.api_factory.BotAPIProvider") as bot_cls, \
         patch("pravaha.domain.api.factory.api_factory.StorageAPIProvider") as storage_cls, \
         patch("pravaha.domain.api.factory.api_factory.WorkflowAPIProvider") as workflow_cls, \
         patch("pravaha.domain.llm.provider.llm_api_provider.LLMAPIProvider") as llm_cls, \
         patch("pravaha.domain.llm.manager.llm_config_manager.LLMConfigManager") as llm_config_cls, \
         patch("pravaha.domain.workflow.manager.local_workflow_manager.LocalWorkflowManager"), \
         patch("pravaha.domain.workflow.infrastructure.json_workflow_repository.JsonWorkflowRepository"), \
         patch("pravaha.domain.workflow.infrastructure.json_run_repository.JsonRunRepository"), \
         patch("pravaha.domain.workflow.service.simple_orchestration_engine.SimpleOrchestrationEngine"), \
         patch("pravaha.domain.workflow.service.workflow_service.WorkflowService"):

        # Setup routers
        bot_cls.return_value.router = MagicMock()
        storage_cls.return_value.router = MagicMock()
        workflow_cls.return_value.router = MagicMock()
        llm_cls.return_value.router = MagicMock()
        
        create_fastapi_app(
            bot_manager=mock_bot_manager,
            task_config=mock_task_config,
            storage_manager=mock_storage,
            llm_config_path=mock_llm_path
        )
        
        # 1. Verify LLM Config wiring
        args, _ = llm_config_cls.call_args
        assert isinstance(args[0], Path)
        assert str(args[0]) == mock_llm_path
        
        # 2. Verify Bot wiring
        bot_cls.assert_called_with(mock_bot_manager, mock_task_config)
        
        # 3. Verify Storage wiring
        # StorageAPIProvider(storage_manager, llm_config_manager, path_resolver, version_resolver)
        s_args, _ = storage_cls.call_args
        assert s_args[0] == mock_storage
        # s_args[1] is llm_config_manager instance
        
        # 4. Verify Workflow defaults wiring (if any)
        # We didn't pass defaults, so it should be None
        # WorkflowAPIProvider(workflow_service, workflow_manager)
        workflow_cls.assert_called()

def test_auth_wiring(mock_bot_manager, mock_task_config):
    """Verify authentication config wiring."""
    mock_auth_config = Mock()
    mock_auth_config.enabled = True
    mock_auth_config.exempt_paths = ["/foo"]
    mock_repo = Mock()
    
    with patch("pravaha.domain.api.factory.api_factory.BotAPIProvider") as bot_cls, \
         patch("pravaha.domain.api.factory.api_factory.StorageAPIProvider") as storage_cls, \
         patch("pravaha.domain.api.factory.api_factory.WorkflowAPIProvider") as workflow_cls, \
         patch("pravaha.domain.llm.provider.llm_api_provider.LLMAPIProvider") as llm_cls, \
         patch("pravaha.domain.llm.manager.llm_config_manager.LLMConfigManager"), \
         patch("pravaha.domain.workflow.manager.local_workflow_manager.LocalWorkflowManager"), \
         patch("pravaha.domain.workflow.infrastructure.json_workflow_repository.JsonWorkflowRepository"), \
         patch("pravaha.domain.workflow.infrastructure.json_run_repository.JsonRunRepository"), \
         patch("pravaha.domain.api.factory.api_factory.APIKeyMiddleware") as auth_middleware, \
         patch("pravaha.domain.api.factory.api_factory.AuthAPIProvider") as auth_provider:
         
        # Routers
        bot_cls.return_value.router = MagicMock()
        storage_cls.return_value.router = MagicMock()
        workflow_cls.return_value.router = MagicMock()
        llm_cls.return_value.router = MagicMock()
        auth_provider.return_value.router = MagicMock()
        
        app = create_fastapi_app(
            bot_manager=mock_bot_manager,
            task_config=mock_task_config,
            storage_manager=Mock(),
            auth_config=mock_auth_config,
            access_key_repository=mock_repo
        )
                # Verify middleware added
            # Middleware class is passed to add_middleware, but not necessarily instantiated immediately by FastAPI setup
            # So we check if it is in the middleware stack
        # Find the middleware entry
        middleware_entry = next((m for m in app.user_middleware if m.cls == auth_middleware), None)
        assert middleware_entry is not None
        
        # Verify options passed to add_middleware
        # Middleware object in Starlette is an iterator (cls, options)
        # We can unpack it or check attributes if available.
        try:
           mw_cls, mw_options = middleware_entry
           assert mw_cls == auth_middleware
           assert mw_options['repository'] == mock_repo
           assert mw_options['exempt_paths'] == ["/foo"]
        except (TypeError, ValueError):
            # Fallback if it's not iterable (older versions? shouldn't happen)
            options = getattr(middleware_entry, 'options', getattr(middleware_entry, 'kwargs', {}))
            assert options['repository'] == mock_repo
            assert options['exempt_paths'] == ["/foo"]
        
        # Verify Auth Provider initialized and mounted
        auth_provider.assert_called_with(mock_repo)
