"""
Tests for the BaseNode class.

Tests cover:
- Node initialization
- can_run() logic
- Required parcel checking
- Error handling in run_safe()
- Abstract method enforcement
"""

import unittest
from typing import Dict, Any
from base_node import BaseNode
from parcel import Parcel


class TestNode(BaseNode):
    """Concrete test node for testing BaseNode functionality."""
    
    def __init__(self, node_id: str = "test", requires=None, outputs=None):
        if requires is None:
            requires = ["input"]
        if outputs is None:
            outputs = ["output"]
        super().__init__(node_id, requires, outputs)
    
    def run(self, parcels: Dict[str, Parcel], index=None) -> Dict[str, Any]:
        """Simple test implementation."""
        if "input" in parcels:
            return {"output": parcels["input"].value.upper()}
        return {"output": "default"}


class FailingNode(BaseNode):
    """Test node that always raises an exception."""
    
    def __init__(self):
        super().__init__("failing", requires=["input"], outputs=["output"])
    
    def run(self, parcels: Dict[str, Parcel], index=None) -> Dict[str, Any]:
        raise ValueError("Test error")


class TestBaseNode(unittest.TestCase):
    """Test the BaseNode class."""
    
    def test_node_initialization(self):
        """Test node initialization."""
        node = TestNode("test1", requires=["a", "b"], outputs=["c"])
        
        self.assertEqual(node.node_id, "test1")
        self.assertEqual(node.requires, ["a", "b"])
        self.assertEqual(node.outputs, ["c"])
    
    def test_can_run_with_all_requirements(self):
        """Test can_run returns True when all requirements are met."""
        node = TestNode(requires=["a", "b"])
        parcels = {
            "a": Parcel("a", "value_a", 1.0),
            "b": Parcel("b", "value_b", 1.0),
            "c": Parcel("c", "value_c", 1.0),
        }
        
        self.assertTrue(node.can_run(parcels))
    
    def test_can_run_with_missing_requirements(self):
        """Test can_run returns False when requirements are missing."""
        node = TestNode(requires=["a", "b", "c"])
        parcels = {
            "a": Parcel("a", "value_a", 1.0),
            "b": Parcel("b", "value_b", 1.0),
        }
        
        self.assertFalse(node.can_run(parcels))
    
    def test_can_run_with_no_requirements(self):
        """Test can_run returns True when node has no requirements."""
        node = TestNode(requires=[])
        parcels = {}
        
        self.assertTrue(node.can_run(parcels))
    
    def test_can_run_with_empty_parcels(self):
        """Test can_run with empty parcel dict."""
        node = TestNode(requires=["a"])
        parcels = {}
        
        self.assertFalse(node.can_run(parcels))
    
    def test_get_required_parcels(self):
        """Test getting required parcels."""
        node = TestNode(requires=["a", "b"])
        parcels = {
            "a": Parcel("a", "value_a", 1.0),
            "b": Parcel("b", "value_b", 1.0),
            "c": Parcel("c", "value_c", 1.0),
        }
        
        required = node.get_required_parcels(parcels)
        
        self.assertEqual(len(required), 2)
        self.assertIn("a", required)
        self.assertIn("b", required)
        self.assertNotIn("c", required)
    
    def test_get_required_parcels_partial(self):
        """Test get_required_parcels with some missing parcels."""
        node = TestNode(requires=["a", "b", "c"])
        parcels = {
            "a": Parcel("a", "value_a", 1.0),
            "c": Parcel("c", "value_c", 1.0),
        }
        
        required = node.get_required_parcels(parcels)
        
        self.assertEqual(len(required), 2)
        self.assertIn("a", required)
        self.assertIn("c", required)
        self.assertNotIn("b", required)
    
    def test_run_basic(self):
        """Test basic run functionality."""
        node = TestNode(requires=["input"], outputs=["output"])
        parcels = {"input": Parcel("input", "hello", 1.0)}
        
        result = node.run(parcels)
        
        self.assertEqual(result["output"], "HELLO")
    
    def test_run_with_index(self):
        """Test run with index parameter."""
        node = TestNode()
        parcels = {"input": Parcel("input", "test", 1.0)}
        
        result = node.run(parcels, index=5)
        
        self.assertIsNotNone(result)
    
    def test_run_safe_success(self):
        """Test run_safe with successful execution."""
        node = TestNode()
        parcels = {"input": Parcel("input", "hello", 1.0)}
        
        result = node.run_safe(parcels)
        
        self.assertEqual(result["output"], "HELLO")
        self.assertNotIn("error", result)
    
    def test_run_safe_error_handling(self):
        """Test run_safe handles exceptions properly."""
        node = FailingNode()
        parcels = {"input": Parcel("input", "test", 1.0)}
        
        result = node.run_safe(parcels)
        
        self.assertIn("error_failing", result)
        error_info = result["error_failing"]
        self.assertIn("error", error_info)
        self.assertIn("Test error", error_info["error"])
        self.assertEqual(error_info["node_id"], "failing")
    
    def test_str_representation(self):
        """Test string representation."""
        node = TestNode("my_node")
        
        str_repr = str(node)
        
        self.assertIn("TestNode", str_repr)
        self.assertIn("my_node", str_repr)
    
    def test_repr_representation(self):
        """Test repr representation."""
        node = TestNode("my_node", requires=["a"], outputs=["b"])
        
        repr_str = repr(node)
        
        self.assertIn("TestNode", repr_str)
        self.assertIn("my_node", repr_str)
        self.assertIn("['a']", repr_str)
        self.assertIn("['b']", repr_str)
    
    def test_multiple_requirements(self):
        """Test node with multiple requirements."""
        node = TestNode(requires=["a", "b", "c", "d"], outputs=["result"])
        parcels = {
            "a": Parcel("a", 1, 1.0),
            "b": Parcel("b", 2, 1.0),
            "c": Parcel("c", 3, 1.0),
            "d": Parcel("d", 4, 1.0),
        }
        
        self.assertTrue(node.can_run(parcels))
    
    def test_multiple_outputs(self):
        """Test node with multiple outputs."""
        node = TestNode(
            requires=["input"],
            outputs=["output1", "output2", "output3"]
        )
        
        self.assertEqual(len(node.outputs), 3)


if __name__ == '__main__':
    unittest.main()
