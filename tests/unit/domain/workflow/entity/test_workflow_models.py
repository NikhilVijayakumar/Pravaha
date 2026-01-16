"""
Unit tests for updated workflow entity models
"""
import pytest
from pravaha.domain.workflow.entity.workflow_node import InputItem, WorkflowNode
from pravaha.domain.workflow.entity.workflow_edge import WorkflowEdge
from pravaha.domain.workflow.entity.workflow import Workflow


class TestInputItem:
    def test_direct_input(self):
        """Test InputItem with direct value"""
        item = InputItem(key_name="param1", source="direct", value=42)
        assert item.key_name == "param1"
        assert item.source == "direct"
        assert item.value == 42
        assert item.path is None
        assert item.format is None

    def test_file_input_json(self):
        """Test InputItem with JSON file"""
        item = InputItem(
            key_name="config_file",
            source="file",
            path="/data/config.json",
            format="json"
        )
        assert item.key_name == "config_file"
        assert item.source == "file"
        assert item.path == "/data/config.json"
        assert item.format == "json"
        assert item.value is None

    def test_file_input_text(self):
        """Test InputItem with text file"""
        item = InputItem(
            key_name="knowledge_file",
            source="file",
            path="/storage/knowledge/research.pdf",
            format="text"
        )
        assert item.format == "text"

    def test_node_reference(self):
        """Test InputItem referencing another node's output"""
        item = InputItem(
            key_name="input_data",
            source="node_123",
            value=None
        )
        assert item.source == "node_123"


class TestWorkflowNode:
    def test_node_with_dict_inputs(self):
        """Test WorkflowNode with dictionary inputs"""
        node = WorkflowNode(
            id="node1",
            node_type="APP",
            task_name="test_application",
            inputs={
                "param1": InputItem(key_name="param1", source="direct", value=10),
                "param2": InputItem(key_name="param2", source="direct", value="test")
            },
            position={"x": 100.0, "y": 200.0}
        )
        assert "param1" in node.inputs
        assert "param2" in node.inputs
        assert node.inputs["param1"].value == 10
        assert node.position["x"] == 100.0
        assert node.position["y"] == 200.0

    def test_node_with_empty_inputs(self):
        """Test WorkflowNode with empty inputs dict"""
        node = WorkflowNode(
            id="node2",
            node_type="UTIL",
            task_name="calculator",
            inputs={},
            position={"x": 500.0, "y": 400.0}
        )
        assert node.inputs == {}
        assert len(node.inputs) == 0

    def test_node_with_llm_config(self):
        """Test WorkflowNode with LLM configuration"""
        llm_config = {
            "ui_mode": "creative",
            "ui_model_id": "gpt-4",
            "model_config": {
                "model": "gpt-4",
                "api_key": "test-key"
            },
            "llm_parameters": {
                "temperature": 0.7,
                "max_completion_tokens": 1000
            }
        }
        node = WorkflowNode(
            id="node3",
            node_type="APP",
            task_name="generate_scientific_knowledge_application",
            inputs={},
            position={"x": 300.0, "y": 300.0},
            llm_config=llm_config
        )
        assert node.llm_config is not None
        assert node.llm_config["ui_mode"] == "creative"
        assert node.llm_config["llm_parameters"]["temperature"] == 0.7

    def test_node_with_environment_config(self):
        """Test WorkflowNode with environment configuration"""
        env_config = {
            "variables": [
                {"key": "API_KEY", "value": "secret", "description": "API key"},
                {"key": "DEBUG", "value": "true"}
            ]
        }
        node = WorkflowNode(
            id="node4",
            node_type="ENVIRONMENT",
            task_name="setup_env",
            inputs={},
            environment_config=env_config
        )
        assert node.environment_config is not None
        assert len(node.environment_config["variables"]) == 2

    def test_node_minimal(self):
        """Test WorkflowNode with minimal required fields"""
        node = WorkflowNode(
            id="minimal_node",
            node_type="APP",
            task_name="test_app"
        )
        assert node.id == "minimal_node"
        assert node.inputs == {}
        assert node.position is None
        assert node.llm_config is None
        assert node.environment_config is None


class TestWorkflowEdge:
    def test_edge_basic(self):
        """Test WorkflowEdge with basic fields"""
        edge = WorkflowEdge(
            id="edge1",
            source="node1",
            target="node2"
        )
        assert edge.id == "edge1"
        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.sourceHandle is None
        assert edge.targetHandle is None

    def test_edge_with_handles(self):
        """Test WorkflowEdge with source and target handles"""
        edge = WorkflowEdge(
            id="edge2",
            source="node1",
            target="node2",
            sourceHandle="output_1",
            targetHandle="input_1"
        )
        assert edge.sourceHandle == "output_1"
        assert edge.targetHandle == "input_1"


class TestWorkflow:
    def test_workflow_without_id(self):
        """Test Workflow creation without ID (should be auto-generated later)"""
        workflow = Workflow(
            name="Test Workflow",
            nodes=[],
            edges=[]
        )
        assert workflow.id is None
        assert workflow.name == "Test Workflow"
        assert workflow.created_at is None
        assert workflow.updated_at is None

    def test_workflow_with_id(self):
        """Test Workflow with explicit ID"""
        workflow = Workflow(
            id="workflow_123",
            name="Existing Workflow",
            nodes=[],
            edges=[]
        )
        assert workflow.id == "workflow_123"

    def test_workflow_with_timestamps(self):
        """Test Workflow with timestamps"""
        workflow = Workflow(
            id="workflow_456",
            name="Timestamped Workflow",
            nodes=[],
            edges=[],
            created_at="2026-01-08T13:30:00.000000",
            updated_at="2026-01-08T13:45:00.000000"
        )
        assert workflow.created_at == "2026-01-08T13:30:00.000000"
        assert workflow.updated_at == "2026-01-08T13:45:00.000000"

    def test_workflow_complete(self):
        """Test complete Workflow with nodes and edges"""
        node1 = WorkflowNode(
            id="node_1",
            node_type="APP",
            task_name="generate_scientific_knowledge_application",
            inputs={},
            position={"x": 500.0, "y": 400.0}
        )
        node2 = WorkflowNode(
            id="node_2",
            node_type="UTIL",
            task_name="calculator",
            inputs={
                "result": InputItem(key_name="result", source="node_1", value=None)
            },
            position={"x": 700.0, "y": 400.0}
        )
        edge = WorkflowEdge(
            id="edge_1",
            source="node_1",
            target="node_2"
        )
        
        workflow = Workflow(
            name="Complete Workflow",
            description="A workflow with nodes and edges",
            nodes=[node1, node2],
            edges=[edge]
        )
        
        assert len(workflow.nodes) == 2
        assert len(workflow.edges) == 1
        assert workflow.nodes[0].id == "node_1"
        assert workflow.edges[0].source == "node_1"
        assert workflow.edges[0].target == "node_2"


class TestWorkflowSerialization:
    def test_workflow_to_dict(self):
        """Test Workflow serialization to dict (for JSON)"""
        workflow = Workflow(
            name="Test Workflow",
            nodes=[
                WorkflowNode(
                    id="node_1",
                    node_type="APP",
                    task_name="test_app",
                    inputs={},
                    position={"x": 500.0, "y": 400.0}
                )
            ],
            edges=[]
        )
        
        data = workflow.model_dump()
        assert data["name"] == "Test Workflow"
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["id"] == "node_1"
        assert data["nodes"][0]["position"]["x"] == 500.0

    def test_workflow_from_dict(self):
        """Test Workflow deserialization from dict"""
        data = {
            "name": "Test Workflow",
            "nodes": [
                {
                    "id": "node_1",
                    "node_type": "APP",
                    "task_name": "generate_scientific_knowledge_application",
                    "inputs": {},
                    "position": {"x": 500, "y": 400}
                }
            ],
            "edges": []
        }
        
        workflow = Workflow(**data)
        assert workflow.name == "Test Workflow"
        assert len(workflow.nodes) == 1
        assert workflow.nodes[0].position["x"] == 500
