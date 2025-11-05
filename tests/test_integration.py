"""
Integration tests for complete workflows.

Tests cover:
- Complete array spreading workflow
- Linear workflow chains
- Parallel processing workflows
- Error handling in workflows
- Edge cases (empty arrays, single items, etc.)
"""

import unittest
from workflow_engine import WorkflowEngine
from nodes import (
    RequestNode, ValidateNode, TransformNode, LogNode,
    ArraySpreadNode, ProcessItemNode, CollectNode, ResponseNode
)


class TestIntegrationWorkflows(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = WorkflowEngine()
    
    def test_simple_linear_workflow(self):
        """Test simple linear workflow: request -> validate -> transform -> response."""
        nodes = [
            RequestNode("request"),
            ValidateNode("validate"),
            TransformNode("transform", operation="uppercase"),
            ResponseNode("response", "transformed_data")
        ]
        initial_data = {}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("response", result)
        self.assertEqual(result["response"].value["status"], "success")
    
    def test_parallel_processing_workflow(self):
        """Test workflow with parallel branches."""
        nodes = [
            RequestNode("request"),
            ValidateNode("validate"),
            LogNode("log"),  # Runs in parallel with validate
        ]
        initial_data = {}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Both validation and logging should complete
        self.assertIn("validation_result", result)
        self.assertIn("log_entry", result)
    
    def test_complete_array_spreading_workflow(self):
        """Test complete array spreading workflow."""
        nodes = [
            ArraySpreadNode("spread", "users", "user"),
            ProcessItemNode("process", "user", "processed"),
            CollectNode("collect", "processed", "result", "user_meta"),
            ResponseNode("response", "result")
        ]
        initial_data = {"users": ["alice", "bob", "charlie"]}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Check that response was created
        self.assertIn("response", result)
        response_data = result["response"].value
        
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(len(response_data["data"]), 3)
        self.assertIn("ALICE", response_data["data"][0])
        self.assertIn("BOB", response_data["data"][1])
        self.assertIn("CHARLIE", response_data["data"][2])
    
    def test_array_workflow_with_single_item(self):
        """Test array workflow with only one item."""
        nodes = [
            ArraySpreadNode("spread", "items", "item"),
            ProcessItemNode("process", "item", "processed"),
            CollectNode("collect", "processed", "result", "item_meta"),
        ]
        initial_data = {"items": ["single"]}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("result", result)
        self.assertEqual(len(result["result"].value), 1)
        self.assertIn("SINGLE", result["result"].value[0])
    
    def test_array_workflow_with_empty_array(self):
        """Test array workflow with empty array."""
        nodes = [
            ArraySpreadNode("spread", "items", "item"),
            ProcessItemNode("process", "item", "processed"),
            CollectNode("collect", "processed", "result", "item_meta"),
        ]
        initial_data = {"items": []}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("result", result)
        self.assertEqual(result["result"].value, [])
    
    def test_array_workflow_with_large_array(self):
        """Test array workflow with larger array."""
        items = [f"item_{i}" for i in range(20)]
        nodes = [
            ArraySpreadNode("spread", "items", "item"),
            ProcessItemNode("process", "item", "processed"),
            CollectNode("collect", "processed", "result", "item_meta"),
        ]
        initial_data = {"items": items}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("result", result)
        self.assertEqual(len(result["result"].value), 20)
        
        # Verify all items were processed
        for i in range(20):
            self.assertIn(f"ITEM_{i}", result["result"].value[i])
    
    def test_multiple_array_workflows_in_parallel(self):
        """Test multiple independent array processing workflows."""
        nodes = [
            # First array workflow
            ArraySpreadNode("spread1", "users", "user"),
            ProcessItemNode("process1", "user", "processed_users"),
            CollectNode("collect1", "processed_users", "result_users", "user_meta"),
            
            # Second array workflow
            ArraySpreadNode("spread2", "items", "item"),
            ProcessItemNode("process2", "item", "processed_items"),
            CollectNode("collect2", "processed_items", "result_items", "item_meta"),
        ]
        initial_data = {
            "users": ["alice", "bob"],
            "items": ["x", "y", "z"]
        }
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Both arrays should be processed independently
        self.assertIn("result_users", result)
        self.assertIn("result_items", result)
        self.assertEqual(len(result["result_users"].value), 2)
        self.assertEqual(len(result["result_items"].value), 3)
    
    def test_workflow_with_no_runnable_nodes(self):
        """Test workflow that can't make progress (deadlock)."""
        nodes = [
            ValidateNode("validate"),  # Requires request_data
            TransformNode("transform"),  # Requires validation_result
        ]
        initial_data = {}  # No initial data provided
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # No nodes should run, workflow should terminate cleanly
        self.assertEqual(len(result), 0)
    
    def test_workflow_with_partial_completion(self):
        """Test workflow where only some nodes can run."""
        nodes = [
            RequestNode("request"),
            ValidateNode("validate"),
            # No transform node, so workflow stops after validation
        ]
        initial_data = {}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("request_data", result)
        self.assertIn("validation_result", result)
        # No transformed_data since TransformNode wasn't included
        self.assertNotIn("transformed_data", result)
    
    def test_workflow_execution_order(self):
        """Test that workflow respects data dependencies."""
        # Create nodes in wrong order - engine should execute in correct order
        nodes = [
            ResponseNode("response", "result"),  # Needs result
            CollectNode("collect", "processed", "result", "item_meta"),  # Needs all processed items
            ArraySpreadNode("spread", "items", "item"),  # Creates items
            ProcessItemNode("process", "item", "processed"),  # Processes items
        ]
        initial_data = {"items": ["a", "b"]}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Despite wrong order in node list, workflow should complete successfully
        self.assertIn("response", result)
        self.assertEqual(len(result["response"].value["data"]), 2)
    
    def test_workflow_with_mixed_indexed_and_non_indexed(self):
        """Test workflow mixing indexed and non-indexed parcels."""
        nodes = [
            RequestNode("request"),  # Creates request_data
            LogNode("log"),  # Uses request_data (non-indexed)
            ArraySpreadNode("spread", "items", "item"),  # Creates item[0], item[1]...
            ProcessItemNode("process", "item", "processed"),  # Processes indexed items
        ]
        initial_data = {"items": ["x", "y"]}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Both indexed and non-indexed parcels should exist
        self.assertIn("request_data", result)
        self.assertIn("log_entry", result)
        self.assertIn("processed[0]", result)
        self.assertIn("processed[1]", result)
    
    def test_workflow_termination_on_success(self):
        """Test workflow terminates when all nodes have run."""
        nodes = [
            RequestNode("req"),
            ValidateNode("val"),
        ]
        initial_data = {}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Should terminate cleanly
        self.assertIn("request_data", result)
        self.assertIn("validation_result", result)
        
        # Check execution log shows completion
        log = self.engine.get_execution_log()
        self.assertTrue(any("workflow complete" in entry.lower() for entry in log))
    
    def test_complex_workflow_with_all_features(self):
        """Test complex workflow combining all features."""
        nodes = [
            RequestNode("request"),
            LogNode("log"),  # Parallel with next nodes
            ArraySpreadNode("spread", "data", "item"),
            ProcessItemNode("process", "item", "processed"),
            CollectNode("collect", "processed", "result", "item_meta"),
            ValidateNode("validate"),  # Uses request_data
            ResponseNode("response", "result"),
        ]
        initial_data = {"data": ["alpha", "beta", "gamma"]}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # All outputs should exist
        self.assertIn("request_data", result)
        self.assertIn("log_entry", result)
        self.assertIn("validation_result", result)
        self.assertIn("result", result)
        self.assertIn("response", result)
        
        # Final response should contain processed data
        response_data = result["response"].value["data"]
        self.assertEqual(len(response_data), 3)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = WorkflowEngine()
    
    def test_workflow_with_duplicate_node_ids(self):
        """Test workflow with duplicate node IDs."""
        nodes = [
            RequestNode("same_id"),
            ValidateNode("same_id"),  # Same ID
        ]
        initial_data = {}
        
        # Should still work (nodes share same ID but are different instances)
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Both nodes should produce outputs
        self.assertIn("request_data", result)
        self.assertIn("validation_result", result)
    
    def test_empty_nodes_list(self):
        """Test workflow with no nodes."""
        nodes = []
        initial_data = {"data": "test"}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Should return initial data unchanged
        self.assertIn("data", result)
        self.assertEqual(result["data"].value, "test")
    
    def test_workflow_with_none_values(self):
        """Test workflow handling None values."""
        nodes = [
            ArraySpreadNode("spread", "items", "item"),
            ProcessItemNode("process", "item", "processed"),
        ]
        initial_data = {"items": [None, "test", None]}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Should process all items including None
        self.assertIn("processed[0]", result)
        self.assertIn("processed[1]", result)
        self.assertIn("processed[2]", result)


if __name__ == '__main__':
    unittest.main()
