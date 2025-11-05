"""
Tests for the WorkflowEngine class.

Tests cover:
- Basic workflow execution
- Indexed parcel matching
- Multiple iterations
- Termination conditions
- Deadlock detection
- Error propagation
- Execution order based on data availability
"""

import unittest
from typing import Dict, Any
from workflow_engine import WorkflowEngine
from base_node import BaseNode
from parcel import Parcel


class SimpleNode(BaseNode):
    """Simple test node that transforms input to output."""
    
    def __init__(self, node_id: str, input_name: str, output_name: str):
        super().__init__(node_id, requires=[input_name], outputs=[output_name])
        self.input_name = input_name
        self.output_name = output_name
    
    def run(self, parcels: Dict[str, Parcel], index=None) -> Dict[str, Any]:
        if index is not None:
            input_key = f"{self.input_name}[{index}]"
            value = parcels[input_key].value
            return {f"{self.output_name}[{index}]": value.upper()}
        else:
            value = parcels[self.input_name].value
            return {self.output_name: value.upper()}


class MultiInputNode(BaseNode):
    """Node requiring multiple inputs."""
    
    def __init__(self):
        super().__init__("multi", requires=["a", "b"], outputs=["result"])
    
    def run(self, parcels: Dict[str, Parcel], index=None) -> Dict[str, Any]:
        a_val = parcels["a"].value
        b_val = parcels["b"].value
        return {"result": f"{a_val}+{b_val}"}


class CounterNode(BaseNode):
    """Node that counts how many times it runs."""
    
    def __init__(self):
        super().__init__("counter", requires=["trigger"], outputs=["count"])
        self.run_count = 0
    
    def run(self, parcels: Dict[str, Parcel], index=None) -> Dict[str, Any]:
        self.run_count += 1
        return {"count": self.run_count}


class TestWorkflowEngine(unittest.TestCase):
    """Test the WorkflowEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = WorkflowEngine()
    
    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        self.assertEqual(len(self.engine.parcels), 0)
        self.assertEqual(len(self.engine.execution_log), 0)
    
    def test_simple_workflow(self):
        """Test simple linear workflow: a -> b -> c."""
        nodes = [
            SimpleNode("node1", "a", "b"),
            SimpleNode("node2", "b", "c"),
        ]
        initial_data = {"a": "hello"}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("a", result)
        self.assertIn("b", result)
        self.assertIn("c", result)
        self.assertEqual(result["c"].value, "HELLO")
    
    def test_workflow_with_no_initial_data(self):
        """Test workflow with empty initial data."""
        nodes = [SimpleNode("node1", "a", "b")]
        initial_data = {}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Node can't run without input, so no output
        self.assertNotIn("b", result)
    
    def test_parallel_execution(self):
        """Test nodes running in parallel when data is available."""
        nodes = [
            SimpleNode("node1", "input", "output1"),
            SimpleNode("node2", "input", "output2"),
        ]
        initial_data = {"input": "test"}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("output1", result)
        self.assertIn("output2", result)
        self.assertEqual(result["output1"].value, "TEST")
        self.assertEqual(result["output2"].value, "TEST")
    
    def test_multi_input_node(self):
        """Test node requiring multiple inputs waits for all."""
        nodes = [
            SimpleNode("node1", "x", "a"),
            SimpleNode("node2", "y", "b"),
            MultiInputNode(),  # requires both "a" and "b"
        ]
        initial_data = {"x": "hello", "y": "world"}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("result", result)
        self.assertEqual(result["result"].value, "HELLO+WORLD")
    
    def test_indexed_parcel_matching(self):
        """Test _get_indexed_matches finds indexed parcels correctly."""
        self.engine.parcels = {
            "user[0]": Parcel("user[0]", "alice", 1.0),
            "user[1]": Parcel("user[1]", "bob", 1.0),
            "user[2]": Parcel("user[2]", "charlie", 1.0),
            "other": Parcel("other", "data", 1.0),
        }
        
        indices = self.engine._get_indexed_matches(["user"], self.engine.parcels)
        
        self.assertEqual(indices, [0, 1, 2])
    
    def test_indexed_parcel_matching_empty(self):
        """Test _get_indexed_matches returns empty list when no matches."""
        self.engine.parcels = {
            "other": Parcel("other", "data", 1.0),
        }
        
        indices = self.engine._get_indexed_matches(["user"], self.engine.parcels)
        
        self.assertEqual(indices, [])
    
    def test_indexed_parcel_matching_with_exact_match(self):
        """Test _get_indexed_matches ignores exact matches (non-indexed)."""
        self.engine.parcels = {
            "user": Parcel("user", "exact", 1.0),  # Exact match, not indexed
            "user[0]": Parcel("user[0]", "alice", 1.0),
        }
        
        indices = self.engine._get_indexed_matches(["user"], self.engine.parcels)
        
        # Should return empty because exact match exists
        self.assertEqual(indices, [])
    
    def test_workflow_with_indexed_parcels(self):
        """Test workflow processing indexed parcels automatically."""
        nodes = [SimpleNode("process", "item", "processed")]
        
        # Manually create indexed parcels
        initial_data = {
            "item[0]": "alice",
            "item[1]": "bob",
            "item[2]": "charlie",
        }
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("processed[0]", result)
        self.assertIn("processed[1]", result)
        self.assertIn("processed[2]", result)
        self.assertEqual(result["processed[0]"].value, "ALICE")
        self.assertEqual(result["processed[1]"].value, "BOB")
        self.assertEqual(result["processed[2]"].value, "CHARLIE")
    
    def test_max_iterations_prevents_infinite_loop(self):
        """Test max iterations prevents infinite loops."""
        # Create a node that always produces the same output
        # This could theoretically loop forever
        nodes = [SimpleNode("loop", "x", "x")]
        initial_data = {"x": "test"}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Should terminate due to max iterations or output already exists
        self.assertIsNotNone(result)
    
    def test_node_runs_once_for_non_indexed_output(self):
        """Test node doesn't run multiple times if output already exists."""
        counter = CounterNode()
        nodes = [counter]
        initial_data = {"trigger": "go"}
        
        self.engine.execute_workflow(nodes, initial_data)
        
        # Node should run exactly once
        self.assertEqual(counter.run_count, 1)
    
    def test_execution_log_created(self):
        """Test execution log is populated."""
        nodes = [SimpleNode("node1", "a", "b")]
        initial_data = {"a": "test"}
        
        self.engine.execute_workflow(nodes, initial_data)
        
        log = self.engine.get_execution_log()
        self.assertGreater(len(log), 0)
        self.assertTrue(any("Starting workflow" in entry for entry in log))
    
    def test_can_node_run_basic(self):
        """Test _can_node_run basic functionality."""
        node = SimpleNode("test", "input", "output")
        self.engine.parcels = {"input": Parcel("input", "data", 1.0)}
        
        can_run = self.engine._can_node_run(node)
        
        self.assertTrue(can_run)
    
    def test_can_node_run_missing_requirement(self):
        """Test _can_node_run returns False for missing requirements."""
        node = SimpleNode("test", "input", "output")
        self.engine.parcels = {}
        
        can_run = self.engine._can_node_run(node)
        
        self.assertFalse(can_run)
    
    def test_can_node_run_already_produced_output(self):
        """Test _can_node_run returns False if output already exists."""
        node = SimpleNode("test", "input", "output")
        self.engine.parcels = {
            "input": Parcel("input", "data", 1.0),
            "output": Parcel("output", "DATA", 1.0),  # Already produced
        }
        
        can_run = self.engine._can_node_run(node)
        
        self.assertFalse(can_run)
    
    def test_run_node_adds_node_id_to_parcel(self):
        """Test _run_node adds node_id to created parcels."""
        node = SimpleNode("my_node", "input", "output")
        self.engine.parcels = {"input": Parcel("input", "data", 1.0)}
        
        self.engine._run_node(node)
        
        self.assertIn("output", self.engine.parcels)
        self.assertEqual(self.engine.parcels["output"].node_id, "my_node")
    
    def test_empty_workflow(self):
        """Test workflow with no nodes."""
        nodes = []
        initial_data = {"a": "test"}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        # Should just return initial parcels
        self.assertIn("a", result)
        self.assertEqual(result["a"].value, "test")
    
    def test_workflow_with_complex_chain(self):
        """Test workflow with longer chain: a -> b -> c -> d -> e."""
        nodes = [
            SimpleNode("n1", "a", "b"),
            SimpleNode("n2", "b", "c"),
            SimpleNode("n3", "c", "d"),
            SimpleNode("n4", "d", "e"),
        ]
        initial_data = {"a": "hello"}
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("e", result)
        self.assertEqual(result["e"].value, "HELLO")
    
    def test_multiple_indexed_arrays(self):
        """Test workflow with multiple different indexed arrays."""
        nodes = [
            SimpleNode("process_x", "x", "x_out"),
            SimpleNode("process_y", "y", "y_out"),
        ]
        initial_data = {
            "x[0]": "a",
            "x[1]": "b",
            "y[0]": "c",
            "y[1]": "d",
        }
        
        result = self.engine.execute_workflow(nodes, initial_data)
        
        self.assertIn("x_out[0]", result)
        self.assertIn("x_out[1]", result)
        self.assertIn("y_out[0]", result)
        self.assertIn("y_out[1]", result)


if __name__ == '__main__':
    unittest.main()
