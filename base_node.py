"""
Base Node - Abstract base class for all workflow nodes.

The core principle: Nodes are reactive - they run when their required data becomes available.
No static connections, no predefined execution order. Just data-driven execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import time
from parcel import Parcel


class BaseNode(ABC):
    """Abstract base class for all workflow nodes."""
    
    def __init__(self, node_id: str, requires: List[str], outputs: List[str]):
        self.node_id = node_id
        self.requires = requires  # List of parcel names this node needs
        self.outputs = outputs    # List of parcel names this node produces
    
    def can_run(self, parcels: Dict[str, Parcel]) -> bool:
        """
        Check if this node can run based on available parcels.
        
        The key insight: A node runs when ALL its required parcels are available.
        No complex conditions, no static dependencies - just data availability.
        """
        return all(required in parcels for required in self.requires)
    
    def get_required_parcels(self, parcels: Dict[str, Parcel]) -> Dict[str, Parcel]:
        """Get the parcels this node needs to run."""
        return {name: parcels[name] for name in self.requires if name in parcels}
    
    @abstractmethod
    def run(self, parcels: Dict[str, Parcel], index: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute this node's logic.
        
        Args:
            parcels: All available parcels (node will use only what it needs)
            index: Optional index for array processing (e.g., process item 0, 1, 2...)
            
        Returns:
            Dictionary mapping output parcel names to their values
        """
        pass
    
    def run_safe(self, parcels: Dict[str, Parcel], index: Optional[int] = None) -> Dict[str, Any]:
        """Run the node with error handling."""
        try:
            return self.run(parcels, index)
        except Exception as e:
            return {f"error_{self.node_id}": {
                "error": str(e),
                "node_id": self.node_id,
                "timestamp": time.time()
            }}
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.node_id})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.node_id}', requires={self.requires}, outputs={self.outputs})"
