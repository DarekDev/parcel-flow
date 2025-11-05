"""
Tests for concrete node implementations.

Tests cover:
- RequestNode
- ValidateNode
- TransformNode
- LogNode
- ArraySpreadNode
- ProcessItemNode
- CollectNode
- ResponseNode
"""

import unittest
from typing import Dict, Any
from parcel import Parcel
from nodes import (
    RequestNode, ValidateNode, TransformNode, LogNode,
    ArraySpreadNode, ProcessItemNode, CollectNode, ResponseNode
)


class TestRequestNode(unittest.TestCase):
    """Test RequestNode."""
    
    def test_request_node_creation(self):
        """Test RequestNode initialization."""
        node = RequestNode()
        
        self.assertEqual(node.node_id, "request")
        self.assertEqual(node.requires, [])
        self.assertEqual(node.outputs, ["request_data"])
    
    def test_request_node_run(self):
        """Test RequestNode execution."""
        node = RequestNode()
        result = node.run({})
        
        self.assertIn("request_data", result)
        self.assertIsInstance(result["request_data"], str)


class TestValidateNode(unittest.TestCase):
    """Test ValidateNode."""
    
    def test_validate_node_creation(self):
        """Test ValidateNode initialization."""
        node = ValidateNode()
        
        self.assertEqual(node.requires, ["request_data"])
        self.assertEqual(node.outputs, ["validation_result"])
    
    def test_validate_with_valid_data(self):
        """Test validation with valid data."""
        node = ValidateNode()
        parcels = {"request_data": Parcel("request_data", "valid data", 1.0)}
        
        result = node.run(parcels)
        
        self.assertIn("validation_result", result)
        self.assertTrue(result["validation_result"]["valid"])
    
    def test_validate_with_empty_string(self):
        """Test validation with empty string."""
        node = ValidateNode()
        parcels = {"request_data": Parcel("request_data", "", 1.0)}
        
        result = node.run(parcels)
        
        self.assertFalse(result["validation_result"]["valid"])


class TestTransformNode(unittest.TestCase):
    """Test TransformNode."""
    
    def test_transform_node_creation(self):
        """Test TransformNode initialization."""
        node = TransformNode()
        
        self.assertEqual(node.requires, ["validation_result"])
        self.assertEqual(node.outputs, ["transformed_data"])
    
    def test_transform_uppercase(self):
        """Test uppercase transformation."""
        node = TransformNode(operation="uppercase")
        parcels = {
            "validation_result": Parcel("validation_result", {
                "valid": True,
                "message": "test message"
            }, 1.0)
        }
        
        result = node.run(parcels)
        
        self.assertEqual(result["transformed_data"], "TEST MESSAGE")
    
    def test_transform_add_prefix(self):
        """Test add_prefix transformation."""
        node = TransformNode(operation="add_prefix")
        parcels = {
            "validation_result": Parcel("validation_result", {
                "valid": True,
                "message": "test"
            }, 1.0)
        }
        
        result = node.run(parcels)
        
        self.assertEqual(result["transformed_data"], "PROCESSED: test")
    
    def test_transform_invalid_data(self):
        """Test transformation with invalid data."""
        node = TransformNode()
        parcels = {
            "validation_result": Parcel("validation_result", {
                "valid": False,
                "message": "error"
            }, 1.0)
        }
        
        result = node.run(parcels)
        
        self.assertIn("Invalid data", result["transformed_data"])


class TestLogNode(unittest.TestCase):
    """Test LogNode."""
    
    def test_log_node_creation(self):
        """Test LogNode initialization."""
        node = LogNode()
        
        self.assertEqual(node.requires, ["request_data"])
        self.assertEqual(node.outputs, ["log_entry"])
    
    def test_log_node_run(self):
        """Test LogNode execution."""
        node = LogNode()
        parcels = {"request_data": Parcel("request_data", "test data", 1.0)}
        
        result = node.run(parcels)
        
        self.assertIn("log_entry", result)
        self.assertIn("message", result["log_entry"])
        self.assertIn("level", result["log_entry"])
        self.assertEqual(result["log_entry"]["level"], "INFO")


class TestArraySpreadNode(unittest.TestCase):
    """Test ArraySpreadNode."""
    
    def test_array_spread_creation(self):
        """Test ArraySpreadNode initialization."""
        node = ArraySpreadNode()
        
        self.assertEqual(node.node_id, "array_spread")
    
    def test_array_spread_basic(self):
        """Test spreading an array into indexed parcels."""
        node = ArraySpreadNode("spread", "users", "user")
        parcels = {"users": Parcel("users", ["alice", "bob", "charlie"], 1.0)}
        
        result = node.run(parcels)
        
        self.assertIn("user[0]", result)
        self.assertIn("user[1]", result)
        self.assertIn("user[2]", result)
        self.assertIn("user_meta", result)
        
        self.assertEqual(result["user[0]"], "alice")
        self.assertEqual(result["user[1]"], "bob")
        self.assertEqual(result["user[2]"], "charlie")
        self.assertEqual(result["user_meta"]["length"], 3)
    
    def test_array_spread_empty_array(self):
        """Test spreading empty array."""
        node = ArraySpreadNode("spread", "items", "item")
        parcels = {"items": Parcel("items", [], 1.0)}
        
        result = node.run(parcels)
        
        self.assertIn("item_meta", result)
        self.assertEqual(result["item_meta"]["length"], 0)
    
    def test_array_spread_single_item(self):
        """Test spreading single-item array."""
        node = ArraySpreadNode("spread", "items", "item")
        parcels = {"items": Parcel("items", ["only_one"], 1.0)}
        
        result = node.run(parcels)
        
        self.assertIn("item[0]", result)
        self.assertEqual(result["item[0]"], "only_one")
        self.assertEqual(result["item_meta"]["length"], 1)
    
    def test_array_spread_non_list_raises_error(self):
        """Test that non-list input raises ValueError."""
        node = ArraySpreadNode("spread", "data", "item")
        parcels = {"data": Parcel("data", "not a list", 1.0)}
        
        with self.assertRaises(ValueError) as context:
            node.run(parcels)
        
        self.assertIn("must be a list", str(context.exception))


class TestProcessItemNode(unittest.TestCase):
    """Test ProcessItemNode."""
    
    def test_process_item_creation(self):
        """Test ProcessItemNode initialization."""
        node = ProcessItemNode()
        
        self.assertEqual(node.requires, ["user"])
        self.assertEqual(node.outputs, ["processed"])
    
    def test_process_item_with_index(self):
        """Test processing single item with index."""
        node = ProcessItemNode("process", "user", "processed")
        parcels = {"user[0]": Parcel("user[0]", "alice", 1.0)}
        
        result = node.run(parcels, index=0)
        
        self.assertIn("processed[0]", result)
        self.assertEqual(result["processed[0]"], "PROCESSED: ALICE")
    
    def test_process_item_multiple_indices(self):
        """Test processing items at different indices."""
        node = ProcessItemNode("process", "item", "output")
        
        parcels0 = {"item[0]": Parcel("item[0]", "first", 1.0)}
        result0 = node.run(parcels0, index=0)
        
        parcels5 = {"item[5]": Parcel("item[5]", "sixth", 1.0)}
        result5 = node.run(parcels5, index=5)
        
        self.assertIn("output[0]", result0)
        self.assertIn("output[5]", result5)
    
    def test_process_item_without_index_raises_error(self):
        """Test that running without index raises error."""
        node = ProcessItemNode()
        parcels = {"user[0]": Parcel("user[0]", "alice", 1.0)}
        
        with self.assertRaises(ValueError) as context:
            node.run(parcels, index=None)
        
        self.assertIn("requires an index", str(context.exception))
    
    def test_process_item_missing_parcel_raises_error(self):
        """Test that missing indexed parcel raises error."""
        node = ProcessItemNode("process", "user", "processed")
        parcels = {"user[1]": Parcel("user[1]", "bob", 1.0)}
        
        with self.assertRaises(ValueError) as context:
            node.run(parcels, index=0)  # Looking for user[0] but only [1] exists
        
        self.assertIn("not found", str(context.exception))
    
    def test_process_item_with_number(self):
        """Test processing numeric items."""
        node = ProcessItemNode("process", "num", "result")
        parcels = {"num[0]": Parcel("num[0]", 42, 1.0)}
        
        result = node.run(parcels, index=0)
        
        self.assertIn("result[0]", result)
        self.assertIn("42", result["result[0]"])


class TestCollectNode(unittest.TestCase):
    """Test CollectNode."""
    
    def test_collect_node_creation(self):
        """Test CollectNode initialization."""
        node = CollectNode()
        
        self.assertEqual(node.requires, ["user_meta"])
        self.assertEqual(node.outputs, ["result"])
    
    def test_collect_basic(self):
        """Test collecting indexed parcels into array."""
        node = CollectNode("collect", "processed", "result", "user_meta")
        parcels = {
            "user_meta": Parcel("user_meta", {"length": 3, "items": []}, 1.0),
            "processed[0]": Parcel("processed[0]", "ALICE", 1.0),
            "processed[1]": Parcel("processed[1]", "BOB", 1.0),
            "processed[2]": Parcel("processed[2]", "CHARLIE", 1.0),
        }
        
        result = node.run(parcels)
        
        self.assertIn("result", result)
        self.assertEqual(result["result"], ["ALICE", "BOB", "CHARLIE"])
    
    def test_collect_can_run_with_all_items(self):
        """Test can_run returns True when all items available."""
        node = CollectNode("collect", "item", "result", "meta")
        parcels = {
            "meta": Parcel("meta", {"length": 2}, 1.0),
            "item[0]": Parcel("item[0]", "a", 1.0),
            "item[1]": Parcel("item[1]", "b", 1.0),
        }
        
        self.assertTrue(node.can_run(parcels))
    
    def test_collect_can_run_with_missing_items(self):
        """Test can_run returns False when items are missing."""
        node = CollectNode("collect", "item", "result", "meta")
        parcels = {
            "meta": Parcel("meta", {"length": 3}, 1.0),
            "item[0]": Parcel("item[0]", "a", 1.0),
            # Missing item[1] and item[2]
        }
        
        self.assertFalse(node.can_run(parcels))
    
    def test_collect_empty_array(self):
        """Test collecting empty array."""
        node = CollectNode("collect", "item", "result", "meta")
        parcels = {
            "meta": Parcel("meta", {"length": 0}, 1.0),
        }
        
        result = node.run(parcels)
        
        self.assertEqual(result["result"], [])
    
    def test_collect_preserves_order(self):
        """Test that collection preserves index order."""
        node = CollectNode("collect", "num", "result", "meta")
        parcels = {
            "meta": Parcel("meta", {"length": 5}, 1.0),
            "num[0]": Parcel("num[0]", 10, 1.0),
            "num[1]": Parcel("num[1]", 20, 1.0),
            "num[2]": Parcel("num[2]", 30, 1.0),
            "num[3]": Parcel("num[3]", 40, 1.0),
            "num[4]": Parcel("num[4]", 50, 1.0),
        }
        
        result = node.run(parcels)
        
        self.assertEqual(result["result"], [10, 20, 30, 40, 50])


class TestResponseNode(unittest.TestCase):
    """Test ResponseNode."""
    
    def test_response_node_creation(self):
        """Test ResponseNode initialization."""
        node = ResponseNode()
        
        self.assertEqual(node.requires, ["result"])
        self.assertEqual(node.outputs, ["response"])
    
    def test_response_node_run(self):
        """Test ResponseNode execution."""
        node = ResponseNode("response", "data")
        parcels = {"data": Parcel("data", ["item1", "item2"], 1.0)}
        
        result = node.run(parcels)
        
        self.assertIn("response", result)
        self.assertEqual(result["response"]["status"], "success")
        self.assertEqual(result["response"]["data"], ["item1", "item2"])
        self.assertIn("timestamp", result["response"])
    
    def test_response_with_custom_input(self):
        """Test ResponseNode with custom input parcel."""
        node = ResponseNode("resp", "my_data")
        parcels = {"my_data": Parcel("my_data", "test", 2.0)}
        
        result = node.run(parcels)
        
        self.assertEqual(result["response"]["data"], "test")
        self.assertEqual(result["response"]["timestamp"], 2.0)


if __name__ == '__main__':
    unittest.main()
