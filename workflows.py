"""
Example Workflows - Demonstrating the parcel-based execution paradigm.

These workflows show the progression from simple linear chains to complex
parallel processing using array spreading.
"""

from typing import List, Dict, Any
from base_node import BaseNode
from nodes import (
    RequestNode, ValidateNode, TransformNode, LogNode,
    ArraySpreadNode, ProcessItemNode, CollectNode, ResponseNode
)


def create_simple_workflow() -> List[BaseNode]:
    """
    Workflow 1: Simple Linear Chain
    
    request → validate → transform → response
    
    This demonstrates basic parcel flow and node dependencies.
    """
    return [
        RequestNode("request"),
        ValidateNode("validate"),
        TransformNode("transform"),
        ResponseNode("response", "transformed_data")
    ]


def create_parallel_workflow() -> List[BaseNode]:
    """
    Workflow 2: Parallel Processing
    
    request → [validate, log] → transform → response
    
    This shows how multiple nodes can run independently when data is available.
    Both validate and log nodes can run as soon as request_data is available.
    """
    return [
        RequestNode("request"),
        ValidateNode("validate"),
        LogNode("log"),
        TransformNode("transform"),
        ResponseNode("response", "transformed_data")
    ]


def create_array_workflow() -> List[BaseNode]:
    """
    Workflow 3: Array Spreading (The Key Demo)
    
    request → array-spread → [process-item] → collect → response
    
    This demonstrates the core paradigm - array spreading creates parallel work.
    The ProcessItemNode will run multiple times, once for each array item,
    without any explicit loops or coordination.
    """
    return [
        RequestNode("request"),
        ArraySpreadNode("array_spread", "request_data", "user"),
        ProcessItemNode("process_item", "user", "processed"),
        CollectNode("collect", "processed", "result", "user_meta"),
        ResponseNode("response", "result")
    ]


def get_workflow_data(workflow_name: str) -> Dict[str, Any]:
    """Get sample data for each workflow."""
    
    if workflow_name == "simple":
        return {"request_data": "Hello, World!"}
    
    elif workflow_name == "parallel":
        return {"request_data": "Parallel processing test"}
    
    elif workflow_name == "array":
        return {"request_data": ["alice", "bob", "charlie", "diana"]}
    
    else:
        raise ValueError(f"Unknown workflow: {workflow_name}")


def get_workflow_description(workflow_name: str) -> str:
    """Get a description of what each workflow demonstrates."""
    
    descriptions = {
        "simple": """
🔄 Simple Linear Chain
   Demonstrates basic parcel flow and node dependencies.
   Shows how nodes wait for their required data to become available.
        """,
        
        "parallel": """
⚡ Parallel Processing
   Shows how multiple nodes can run independently when data is available.
   Both validate and log nodes run as soon as request_data is available.
        """,
        
        "array": """
🚀 Array Spreading (The Key Demo)
   Demonstrates the core paradigm - array spreading creates parallel work.
   The ProcessItemNode runs multiple times, once for each array item,
   without any explicit loops or coordination.
   This is the essence of the reactive data flow system!
        """
    }
    
    return descriptions.get(workflow_name, "Unknown workflow")


def list_workflows() -> List[str]:
    """Get list of available workflows."""
    return ["simple", "parallel", "array"]
