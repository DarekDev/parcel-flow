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
                    did_run = self._run_node(node)
                    if did_run:
                        nodes_ran += 1
            
            # If no nodes ran, we're done
            if nodes_ran == 0:
                self._log("✅ No more nodes can run - workflow complete")
                break
        
        if iteration >= max_iterations:
            self._log("⚠️  Workflow stopped - max iterations reached")
        
        return self.parcels
    
    def _can_node_run(self, node: BaseNode) -> bool:
        """
        Check if a node can run and hasn't already run.
        
        A node can run if:
        1. All required parcels exist (either exact match or indexed versions)
        2. It hasn't already produced non-indexed outputs
        """
        # Check if all required parcels are available (exact or indexed)
        for required in node.requires:
            # Check for exact match
            if required in self.parcels:
                continue
            
            # Check for indexed versions
            has_indexed = any(
                name.startswith(f"{required}[") and name.endswith("]")
                for name in self.parcels.keys()
            )
            
            if not has_indexed:
                return False
        
        # Check if node has already produced its outputs (for non-indexed outputs)
        # For indexed outputs, we check per-index later
        has_non_indexed_outputs = any(
            output in self.parcels 
            for output in node.outputs 
            if '[' not in output
        )
        if has_non_indexed_outputs:
            return False
        
        return True
    
    def _run_node(self, node: BaseNode) -> bool:
        """
        Run a single node and add its outputs to the parcel queue.
        
        Returns:
            True if the node actually ran and produced outputs, False otherwise
        """
        # Check for indexed parcels that match node requirements
        indexed_matches = self._get_indexed_matches(node.requires, self.parcels)
        
        did_produce_outputs = False
        
        if indexed_matches:
            # Run node once for each index
            for index in indexed_matches:
                # Check if this index already produced outputs
                has_produced_for_index = any(
                    f"{output}[{index}]" in self.parcels 
                    for output in node.outputs
                )
                if has_produced_for_index:
                    continue
                
                self._log(f"🔄 Running {node} for index [{index}]")
                
                # Run the node with specific index
                outputs = node.run_safe(self.parcels, index)
                
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
                    did_produce_outputs = True
        else:
            # Run normally (no indexing)
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
                did_produce_outputs = True
        
        return did_produce_outputs
    
    def _log(self, message: str):
        """Add a message to the execution log."""
        self.execution_log.append(message)
        print(message)
    
    def get_execution_log(self) -> List[str]:
        """Get the complete execution log."""
        return self.execution_log
    
    def _get_indexed_matches(self, requires: List[str], parcels: Dict[str, Parcel]) -> List[int]:
        """
        Find indexed parcels that match the required parcel names.
        
        Example: If node requires ["user"] and parcels contain "user[0]", "user[1]", "user[2]",
        this returns [0, 1, 2].
        """
        # Strict Zip (Intersection) Strategy
        # We only run for an index if ALL required inputs define that index.
        # This acts like python's zip(), stopping at the shortest array.
        
        common_indices = None
        
        for required in requires:
            # Skip if the exact parcel exists (not indexed) - it's a broadcast/constant
            if required in parcels:
                continue
            
            # Find all indices available for this specific requirement
            current_requirement_indices = set()
            prefix = f"{required}["
            
            for parcel_name in parcels.keys():
                if parcel_name.startswith(prefix) and parcel_name.endswith("]"):
                    try:
                        index = int(parcel_name[len(prefix):-1])
                        current_requirement_indices.add(index)
                    except ValueError:
                        continue
            
            # Intersection: The index must exist for ALL indexed requirements
            if common_indices is None:
                common_indices = current_requirement_indices
            else:
                common_indices.intersection_update(current_requirement_indices)
        
        if common_indices is None:
            return []
            
        return sorted(list(common_indices))
    
    def print_parcels(self):
        """Print all current parcels in a nice format."""
        print("\n📦 Current Parcels:")
        for name, parcel in self.parcels.items():
            print(f"  {name}: {parcel.value}")
        print()
