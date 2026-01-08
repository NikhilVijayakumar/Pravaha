#!/usr/bin/env python3
"""
Simple verification script to test workflow model changes
without requiring full server setup
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nikhil.pravaha.domain.workflow.entity.workflow_node import InputItem, WorkflowNode
from nikhil.pravaha.domain.workflow.entity.workflow_edge import WorkflowEdge
from nikhil.pravaha.domain.workflow.entity.workflow import Workflow


def test_frontend_payload():
    """Test the exact payload from the issue documentation"""
    print("=" * 60)
    print("Testing Frontend Payload from Issue Documentation")
    print("=" * 60)
    
    # This is the exact payload the frontend sends
    payload = {
        "name": "Test Workflow",
        "nodes": [
            {
                "id": "node_1",
                "task_type": "APP",
                "task_name": "generate_scientific_knowledge_application",
                "inputs": {},
                "position": {
                    "x": 500,
                    "y": 400
                }
            }
        ],
        "edges": [],
        "created_at": "2026-01-08T03:15:25.000Z",
        "updated_at": "2026-01-08T03:15:25.000Z"
    }
    
    try:
        # Try to create Workflow from payload
        workflow = Workflow(**payload)
        print("✅ Workflow created successfully!")
        print(f"   Name: {workflow.name}")
        print(f"   Nodes: {len(workflow.nodes)}")
        print(f"   Edges: {len(workflow.edges)}")
        print(f"   Created at: {workflow.created_at}")
        
        # Verify node structure
        node = workflow.nodes[0]
        print(f"\n✅ Node structure validated:")
        print(f"   ID: {node.id}")
        print(f"   Task type: {node.task_type}")
        print(f"   Task name: {node.task_name}")
        print(f"   Inputs (dict): {node.inputs}")
        print(f"   Position: {node.position}")
        
        # Test serialization back to JSON
        serialized = workflow.model_dump(mode='json')
        print(f"\n✅ Serialization successful!")
        print(f"   JSON output:\n{json.dumps(serialized, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_input_item_variations():
    """Test different InputItem variations"""
    print("\n" + "=" * 60)
    print("Testing InputItem Variations")
    print("=" * 60)
    
    tests = [
        {
            "name": "Direct input",
            "data": {"key_name": "param1", "source": "direct", "value": 42}
        },
        {
            "name": "File input (JSON)",
            "data": {"key_name": "config", "source": "file", "path": "/data/config.json", "format": "json"}
        },
        {
            "name": "Node reference",
            "data": {"key_name": "result", "source": "node_123", "value": None}
        }
    ]
    
    all_passed = True
    for test in tests:
        try:
            item = InputItem(**test["data"])
            print(f"✅ {test['name']}: {item.key_name} (source: {item.source})")
        except Exception as e:
            print(f"❌ {test['name']}: {e}")
            all_passed = False
    
    return all_passed


def test_workflow_edge_handles():
    """Test WorkflowEdge with handles"""
    print("\n" + "=" * 60)
    print("Testing WorkflowEdge with Handles")
    print("=" * 60)
    
    try:
        edge = WorkflowEdge(
            id="edge_1",
            source="node_1",
            target="node_2",
            sourceHandle="output_1",
            targetHandle="input_1"
        )
        print(f"✅ Edge created with handles:")
        print(f"   {edge.source} ({edge.sourceHandle}) → {edge.target} ({edge.targetHandle})")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_workflow_with_llm_config():
    """Test WorkflowNode with LLM configuration"""
    print("\n" + "=" * 60)
    print("Testing WorkflowNode with LLM Config")
    print("=" * 60)
    
    try:
        node = WorkflowNode(
            id="node_with_llm",
            task_type="APP",
            task_name="test_app",
            inputs={},
            position={"x": 100.0, "y": 200.0},
            llm_config={
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
        )
        print(f"✅ Node with LLM config created:")
        print(f"   Mode: {node.llm_config['ui_mode']}")
        print(f"   Model: {node.llm_config['ui_model_id']}")
        print(f"   Temperature: {node.llm_config['llm_parameters']['temperature']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all verification tests"""
    print("\n" + "=" * 60)
    print("WORKFLOW MODEL VERIFICATION SCRIPT")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Frontend Payload", test_frontend_payload()))
    results.append(("InputItem Variations", test_input_item_variations()))
    results.append(("Edge Handles", test_workflow_edge_handles()))
    results.append(("LLM Config", test_workflow_with_llm_config()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! The workflow models are ready for frontend integration.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
