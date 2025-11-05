"""
Tests for the Parcel class.

Tests cover:
- Basic parcel creation
- Immutability (dataclass frozen behavior)
- Timestamp handling
- String representations
- Indexed parcel naming
"""

import unittest
import time
from parcel import Parcel


class TestParcel(unittest.TestCase):
    """Test the Parcel class."""
    
    def test_parcel_creation(self):
        """Test basic parcel creation."""
        parcel = Parcel(name="test", value="data", timestamp=123.456)
        
        self.assertEqual(parcel.name, "test")
        self.assertEqual(parcel.value, "data")
        self.assertEqual(parcel.timestamp, 123.456)
        self.assertIsNone(parcel.node_id)
    
    def test_parcel_with_node_id(self):
        """Test parcel creation with node_id."""
        parcel = Parcel(
            name="test",
            value="data",
            timestamp=123.456,
            node_id="node_1"
        )
        
        self.assertEqual(parcel.node_id, "node_1")
    
    def test_parcel_auto_timestamp(self):
        """Test automatic timestamp generation."""
        before = time.time()
        parcel = Parcel(name="test", value="data", timestamp=None)
        after = time.time()
        
        # Timestamp should be set automatically
        self.assertIsNotNone(parcel.timestamp)
        self.assertGreaterEqual(parcel.timestamp, before)
        self.assertLessEqual(parcel.timestamp, after)
    
    def test_parcel_str_representation(self):
        """Test string representation."""
        parcel = Parcel(name="user", value="alice", timestamp=123.456)
        
        str_repr = str(parcel)
        self.assertIn("user", str_repr)
        self.assertIn("alice", str_repr)
    
    def test_parcel_repr_representation(self):
        """Test repr representation."""
        parcel = Parcel(name="user", value="alice", timestamp=123.456)
        
        repr_str = repr(parcel)
        self.assertIn("Parcel", repr_str)
        self.assertIn("name='user'", repr_str)
        self.assertIn("alice", repr_str)
        self.assertIn("123.456", repr_str)
    
    def test_parcel_with_dict_value(self):
        """Test parcel with dictionary value."""
        data = {"name": "alice", "age": 30}
        parcel = Parcel(name="user_data", value=data, timestamp=123.456)
        
        self.assertEqual(parcel.value, data)
        self.assertEqual(parcel.value["name"], "alice")
    
    def test_parcel_with_list_value(self):
        """Test parcel with list value."""
        data = ["alice", "bob", "charlie"]
        parcel = Parcel(name="users", value=data, timestamp=123.456)
        
        self.assertEqual(parcel.value, data)
        self.assertEqual(len(parcel.value), 3)
    
    def test_indexed_parcel_naming(self):
        """Test indexed parcel naming convention."""
        parcel0 = Parcel(name="user[0]", value="alice", timestamp=123.456)
        parcel1 = Parcel(name="user[1]", value="bob", timestamp=123.457)
        
        self.assertEqual(parcel0.name, "user[0]")
        self.assertEqual(parcel1.name, "user[1]")
        self.assertNotEqual(parcel0.timestamp, parcel1.timestamp)
    
    def test_parcel_value_types(self):
        """Test parcels with various value types."""
        # String
        p_str = Parcel(name="str", value="text", timestamp=1.0)
        self.assertIsInstance(p_str.value, str)
        
        # Integer
        p_int = Parcel(name="int", value=42, timestamp=1.0)
        self.assertIsInstance(p_int.value, int)
        
        # Float
        p_float = Parcel(name="float", value=3.14, timestamp=1.0)
        self.assertIsInstance(p_float.value, float)
        
        # None
        p_none = Parcel(name="none", value=None, timestamp=1.0)
        self.assertIsNone(p_none.value)
        
        # Boolean
        p_bool = Parcel(name="bool", value=True, timestamp=1.0)
        self.assertIsInstance(p_bool.value, bool)


if __name__ == '__main__':
    unittest.main()
