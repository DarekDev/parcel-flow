"""
Workflow Engine - The heart of the Matrix execution system.

This engine implements the core paradigm: nodes run when data becomes available.
No static execution order, no complex orchestration - just reactive data flow.
"""

from typing import Dict, List, Any
from parcel import Parcel
from base_node import BaseNode
import time


class WorkflowEngine:
    """Executes workflows using the parcel-based reactive paradigm."""
    
    def __init__(self):
        self.parcels: Dict[str, Parcel] = {}
        self.execution_log: List[str] = []
    
    def execute_workflow(self, nodes: List[BaseNode], initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow with the given nodes and initial data.
        
        The execution model:
        1. Start with initial parcels
        2. Loop: find nodes that can run, run them, add their outputs
        3. Repeat until no more nodes can run
        4. Return final parcels
        """
        # Initialize parcel queue with input data
        self.parcels = {}
        self.execution_log = []
        
        for name, value in initial_data.items():
            self.parcels[name] = Parcel(name=name, value=value, timestamp=time.time())
        
        self._log(f"🚀 Starting workflow with {len(nodes)} nodes")
        self._log(f"📦 Initial parcels: {list(self.parcels.keys())}")
        
        # Main execution loop
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            self._log(f"\n--- Iteration {iteration} ---")
            
            nodes_ran = 0
            
            # Check each node to see if it can run
            for node in nodes:
                if self._can_node_run(node):
                    self._run_node(node)
                    nodes_ran += 1
            
            # If no nodes ran, we're done
            if nodes_ran == 0:
                self._log("✅ No more nodes can run - workflow complete")
                break
        
        if iteration >= max_iterations:
            self._log("⚠️  Workflow stopped - max iterations reached")
        
        return self.parcels
    
    def _can_node_run(self, node: BaseNode) -> bool:
        """Check if a node can run and hasn't already run."""
        if not node.can_run(self.parcels):
            return False
        
        # Check if node has already produced its outputs
        has_outputs = any(output in self.parcels for output in node.outputs)
        if has_outputs:
            return False
        
        return True
    
    def _run_node(self, node: BaseNode):
        """Run a single node and add its outputs to the parcel queue."""
        self._log(f"🔄 Running {node}")
        
        # Get the parcels this node needs
        required_parcels = node.get_required_parcels(self.parcels)
        self._log(f"   📥 Input parcels: {list(required_parcels.keys())}")
        
        # Run the node
        outputs = node.run_safe(self.parcels)
        
        # Add outputs to parcel queue
        for output_name, output_value in outputs.items():
            parcel = Parcel(
                name=output_name,
                value=output_value,
                timestamp=time.time(),
                node_id=node.node_id
            )
            self.parcels[output_name] = parcel
            self._log(f"   📤 Created parcel: {parcel}")
    
    def _log(self, message: str):
        """Add a message to the execution log."""
        self.execution_log.append(message)
        print(message)
    
    def get_execution_log(self) -> List[str]:
        """Get the complete execution log."""
        return self.execution_log
    
    def print_parcels(self):
        """Print all current parcels in a nice format."""
        print("\n📦 Current Parcels:")
        for name, parcel in self.parcels.items():
            print(f"  {name}: {parcel.value}")
        print()
