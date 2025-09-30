"""
Parcel - The fundamental data unit in the Matrix execution system.

A Parcel represents a piece of data that flows through the workflow.
Nodes consume parcels and produce new parcels, creating a reactive data flow.
"""

from dataclasses import dataclass
from typing import Any, Optional
import time


@dataclass
class Parcel:
    """A parcel of data flowing through the workflow."""
    name: str
    value: Any
    timestamp: float
    node_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def __str__(self):
        return f"Parcel({self.name}={self.value})"
    
    def __repr__(self):
        return f"Parcel(name='{self.name}', value={self.value!r}, timestamp={self.timestamp:.3f})"
