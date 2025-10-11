"""
Example Nodes - Demonstrating the parcel-based execution paradigm.

Each node shows a different aspect of the reactive data flow system.
"""

from typing import Dict, Any
from base_node import BaseNode
from parcel import Parcel


class RequestNode(BaseNode):
    """Creates initial parcels from input data."""
    
    def __init__(self, node_id: str = "request"):
        super().__init__(node_id, requires=[], outputs=["request_data"])
    
    def run(self, parcels: Dict[str, Parcel], index: int = None) -> Dict[str, Any]:
        # This node doesn't require any input parcels
        # It just passes through the request data
        return {"request_data": "Initial request received"}


class ValidateNode(BaseNode):
    """Validates data and adds validation results."""
    
    def __init__(self, node_id: str = "validate"):
        super().__init__(node_id, requires=["request_data"], outputs=["validation_result"])
    
    def run(self, parcels: Dict[str, Parcel], index: int = None) -> Dict[str, Any]:
        request_data = parcels["request_data"].value
        is_valid = len(str(request_data)) > 0
        
        return {
            "validation_result": {
                "valid": is_valid,
                "message": "Data is valid" if is_valid else "Data is invalid",
                "timestamp": parcels["request_data"].timestamp
            }
        }


class TransformNode(BaseNode):
    """Transforms data by applying some operation."""
    
    def __init__(self, node_id: str = "transform", operation: str = "uppercase"):
        super().__init__(node_id, requires=["validation_result"], outputs=["transformed_data"])
        self.operation = operation
    
    def run(self, parcels: Dict[str, Parcel], index: int = None) -> Dict[str, Any]:
        validation = parcels["validation_result"].value
        
        if not validation["valid"]:
            return {"transformed_data": "Invalid data - no transformation applied"}
        
        # Simple transformation based on operation
        if self.operation == "uppercase":
            result = str(validation["message"]).upper()
        elif self.operation == "add_prefix":
            result = f"PROCESSED: {validation['message']}"
        else:
            result = validation["message"]
        
        return {"transformed_data": result}


class LogNode(BaseNode):
    """Logs data for debugging - runs in parallel with other nodes."""
    
    def __init__(self, node_id: str = "log"):
        super().__init__(node_id, requires=["request_data"], outputs=["log_entry"])
    
    def run(self, parcels: Dict[str, Parcel], index: int = None) -> Dict[str, Any]:
        request_data = parcels["request_data"].value
        
        return {
            "log_entry": {
                "message": f"Request processed: {request_data}",
                "level": "INFO",
                "timestamp": parcels["request_data"].timestamp
            }
        }


class ArraySpreadNode(BaseNode):
    """
    The key node for demonstrating parallelism!
    
    Takes an array and spreads it into indexed parcels.
    This creates parallel work - other nodes can process each item independently.
    """
    
    def __init__(self, node_id: str = "array_spread", input_parcel: str = "users", output_prefix: str = "user"):
        super().__init__(node_id, requires=[input_parcel], outputs=[f"{output_prefix}_meta"])
        self.input_parcel = input_parcel
        self.output_prefix = output_prefix
    
    def run(self, parcels: Dict[str, Parcel], index: int = None) -> Dict[str, Any]:
        input_data = parcels[self.input_parcel].value
        
        if not isinstance(input_data, list):
            raise ValueError(f"Input parcel '{self.input_parcel}' must be a list")
        
        # Create indexed parcels for each array item
        # This is where the magic happens - we create multiple parcels
        # that other nodes can process in parallel
        result = {}
        for i, item in enumerate(input_data):
            parcel_name = f"{self.output_prefix}[{i}]"
            result[parcel_name] = item
        
        # Add metadata about the array
        result[f"{self.output_prefix}_meta"] = {
            "length": len(input_data),
            "items": input_data,
            "output_prefix": self.output_prefix
        }
        
        return result


class ProcessItemNode(BaseNode):
    """
    Processes individual array items.
    
    This node will run multiple times - once for each item in the array!
    The engine calls this node once per index automatically.
    
    Key insight: Node just declares requires=["user"] (no index!).
    The engine sees "user[0]", "user[1]", etc. and runs this node for each.
    """
    
    def __init__(self, node_id: str = "process_item", input_prefix: str = "user", output_prefix: str = "processed"):
        # Note: We just declare the prefix, not specific indices!
        super().__init__(node_id, requires=[input_prefix], outputs=[output_prefix])
        self.input_prefix = input_prefix
        self.output_prefix = output_prefix
    
    def run(self, parcels: Dict[str, Parcel], index: int = None) -> Dict[str, Any]:
        """
        Process a single array item.
        
        The engine passes the index, so we know which item to process.
        """
        if index is None:
            raise ValueError("ProcessItemNode requires an index to run")
        
        # Get the specific indexed parcel
        parcel_name = f"{self.input_prefix}[{index}]"
        if parcel_name not in parcels:
            raise ValueError(f"Expected parcel '{parcel_name}' not found")
        
        # Process the item
        item_value = parcels[parcel_name].value
        processed_value = self._process_item(item_value)
        
        # Return with indexed output name
        output_name = f"{self.output_prefix}[{index}]"
        return {output_name: processed_value}
    
    def _process_item(self, item: Any) -> Any:
        """Process a single item - can be overridden for different processing logic."""
        if isinstance(item, str):
            return f"PROCESSED: {item.upper()}"
        else:
            return f"PROCESSED: {item}"


class CollectNode(BaseNode):
    """
    Collects processed items back into a single array.
    
    Key insight: Requires the metadata parcel to know how many items to expect.
    Only runs when ALL indexed parcels are available.
    """
    
    def __init__(self, node_id: str = "collect", input_prefix: str = "processed", 
                 output_name: str = "result", meta_parcel: str = "user_meta"):
        # Require the metadata to know array length
        super().__init__(node_id, requires=[meta_parcel], outputs=[output_name])
        self.input_prefix = input_prefix
        self.output_name = output_name
        self.meta_parcel = meta_parcel
    
    def can_run(self, parcels: Dict[str, Parcel]) -> bool:
        """
        Override to check if all indexed items are available.
        
        We need the metadata to know the expected count, and all indexed parcels must exist.
        """
        # First check base requirements (metadata)
        if not super().can_run(parcels):
            return False
        
        # Get metadata to know how many items to expect
        meta_parcel_name = self.requires[0]  # Should be "user_meta" or similar
        if meta_parcel_name not in parcels:
            return False
        
        metadata = parcels[meta_parcel_name].value
        expected_length = metadata.get("length", 0)
        
        # Check if all indexed parcels exist
        for i in range(expected_length):
            indexed_name = f"{self.input_prefix}[{i}]"
            if indexed_name not in parcels:
                return False
        
        return True
    
    def run(self, parcels: Dict[str, Parcel], index: int = None) -> Dict[str, Any]:
        """Collect all indexed parcels into a single array."""
        # Get metadata to know array length
        meta_parcel_name = self.requires[0]
        metadata = parcels[meta_parcel_name].value
        expected_length = metadata.get("length", 0)
        
        # Collect all indexed parcels in order
        result = []
        for i in range(expected_length):
            indexed_name = f"{self.input_prefix}[{i}]"
            if indexed_name in parcels:
                result.append(parcels[indexed_name].value)
        
        return {self.output_name: result}


class ResponseNode(BaseNode):
    """Creates the final response."""
    
    def __init__(self, node_id: str = "response", input_parcel: str = "result"):
        super().__init__(node_id, requires=[input_parcel], outputs=["response"])
        self.input_parcel = input_parcel
    
    def run(self, parcels: Dict[str, Parcel], index: int = None) -> Dict[str, Any]:
        data = parcels[self.input_parcel].value
        
        return {
            "response": {
                "status": "success",
                "data": data,
                "timestamp": parcels[self.input_parcel].timestamp
            }
        }
