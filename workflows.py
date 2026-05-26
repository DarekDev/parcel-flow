"""
Example workflows, from a simple linear chain to array spreading (scatter/gather).

These build up the data-driven model: the engine runs each node when its required
parcels are available, so execution order emerges from data rather than wiring.
"""

from typing import List, Dict, Any
from base_node import BaseNode
from nodes import (
    RequestNode, ValidateNode, TransformNode, LogNode,
    ArraySpreadNode, ProcessItemNode, CollectNode, ResponseNode
)


def create_simple_workflow() -> List[BaseNode]:
    """
    Workflow 1: simple linear chain.

    request -> validate -> transform -> response

    Demonstrates basic parcel flow and how each node waits for its dependency.
    """
    return [
        RequestNode("request"),
        ValidateNode("validate"),
        TransformNode("transform"),
        ResponseNode("response", "transformed_data")
    ]


def create_independent_workflow() -> List[BaseNode]:
    """
    Workflow 2: independent branches.

    request -> [validate, log] -> transform -> response

    Both validate and log depend only on request_data, so once it exists they are
    both eligible to run in the same pass. The engine runs them sequentially, but
    neither depends on the other -- this is where actual concurrency could be added
    (see the capstone exercise).
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
    Workflow 3: array spreading (scatter/gather).

    request -> array-spread -> [process-item per index] -> collect -> response

    ArraySpreadNode emits one indexed parcel per item; ProcessItemNode then runs
    once per index with no explicit loop in its own code. The per-item work is
    independent (the structure of a map), executed sequentially here.
    """
    return [
        RequestNode("request"),
        ArraySpreadNode("array_spread", "request_data", "user"),
        ProcessItemNode("process_item", "user", "processed"),
        CollectNode("collect", "processed", "result", "user_meta"),
        ResponseNode("response", "result")
    ]


def get_workflow_data(workflow_name: str) -> Dict[str, Any]:
    """Get sample input data for each workflow."""

    if workflow_name == "simple":
        return {"request_data": "Hello, World!"}

    elif workflow_name == "independent":
        return {"request_data": "Independent-branch test"}

    elif workflow_name == "array":
        return {"request_data": ["alice", "bob", "charlie", "diana"]}

    else:
        raise ValueError(f"Unknown workflow: {workflow_name}")


def get_workflow_description(workflow_name: str) -> str:
    """Get a short description of what each workflow demonstrates."""

    descriptions = {
        "simple": """
Simple linear chain.
   Basic parcel flow and node dependencies. Each node waits for the parcel
   produced by the previous one.
        """,

        "independent": """
Independent branches.
   validate and log both depend only on request_data, so both become eligible
   as soon as it exists. The engine runs them in one pass (sequentially).
        """,

        "array": """
Array spreading (scatter/gather).
   A list is spread into indexed parcels; the per-item node runs once per index
   with no explicit loop, then a collect node gathers the results back.
        """
    }

    return descriptions.get(workflow_name, "Unknown workflow")


def list_workflows() -> List[str]:
    """Return the list of available workflow names."""
    return ["simple", "independent", "array"]
