"""
Workflow engine: the core of ParcelFlow's execution model.

Nodes run when the data they require becomes available. There is no static
execution order and no separate orchestration layer -- the schedule emerges
from data dependencies at runtime.

Execution is sequential and single-threaded by design, so the logs read in a
deterministic order. Nodes that have no dependency on each other are still run
one after another within a pass; see the capstone exercise for how to execute
independent ready nodes concurrently.
"""

from typing import Dict, List, Any
from parcel import Parcel
from base_node import BaseNode
import time


class WorkflowEngine:
    """Executes workflows using the parcel-based, data-driven model."""

    def __init__(self):
        self.parcels: Dict[str, Parcel] = {}
        self.execution_log: List[str] = []
        self.unrun_nodes: List[BaseNode] = []

    def execute_workflow(self, nodes: List[BaseNode], initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow given its nodes and initial data.

        The model:
        1. Seed the parcel store with the initial data.
        2. Each pass, run every node whose required parcels are now available.
        3. Stop when a pass runs no nodes.
        4. Report any nodes that never ran (unmet dependencies), then return
           the final parcels.
        """
        self.parcels = {}
        self.execution_log = []
        self.unrun_nodes = []
        nodes_that_ran = set()

        for name, value in initial_data.items():
            self.parcels[name] = Parcel(name=name, value=value, timestamp=time.time())

        self._log(f"Starting workflow with {len(nodes)} node(s)")
        self._log(f"Initial parcels: {list(self.parcels.keys())}")

        max_iterations = 100  # safety bound; a deadlock is reported separately below
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            self._log(f"--- Pass {iteration} ---")

            nodes_ran = 0
            for node in nodes:
                if self._can_node_run(node):
                    if self._run_node(node):
                        nodes_ran += 1
                        nodes_that_ran.add(id(node))

            if nodes_ran == 0:
                self._log("No more nodes can run - workflow complete")
                break

        if iteration >= max_iterations:
            self._log("WARNING: workflow stopped - maximum passes reached")

        self._report_unrun_nodes(nodes, nodes_that_ran)

        return self.parcels

    def _report_unrun_nodes(self, nodes: List[BaseNode], nodes_that_ran: set):
        """
        Identify nodes that never ran and explain why.

        A node that never ran is waiting on a required parcel that no node ever
        produced. This is how a deadlock (or a typo in a `requires` name) shows
        up in a data-driven engine: not as a crash, but as work that quietly
        never happens. Surfacing it is what lets a student diagnose it.
        """
        self.unrun_nodes = [node for node in nodes if id(node) not in nodes_that_ran]
        for node in self.unrun_nodes:
            missing = self._missing_requirements(node)
            if missing:
                self._log(
                    f"DEADLOCK: {node} never ran - waiting for parcel(s) "
                    f"{missing} that no node produced"
                )

    def _missing_requirements(self, node: BaseNode) -> List[str]:
        """Return the required parcel names that are absent (exact or indexed)."""
        missing = []
        for required in node.requires:
            if required in self.parcels:
                continue
            has_indexed = any(
                name.startswith(f"{required}[") and name.endswith("]")
                for name in self.parcels.keys()
            )
            if not has_indexed:
                missing.append(required)
        return missing

    def _can_node_run(self, node: BaseNode) -> bool:
        """
        Check whether a node can run and has not already run.

        A node can run if all required parcels exist (exact match or indexed
        versions) and it has not already produced its non-indexed outputs.
        """
        if self._missing_requirements(node):
            return False

        # A node that has already produced its (non-indexed) outputs should not
        # run again. Indexed outputs are checked per-index in _run_node.
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
        Run a node and store its outputs as parcels.

        Returns True if the node produced any output, False otherwise.
        """
        indexed_matches = self._get_indexed_matches(node.requires, self.parcels)

        did_produce_outputs = False

        if indexed_matches:
            # Run the node once per matched index (the scatter step).
            for index in indexed_matches:
                has_produced_for_index = any(
                    f"{output}[{index}]" in self.parcels
                    for output in node.outputs
                )
                if has_produced_for_index:
                    continue

                self._log(f"[run] {node} for index [{index}]")
                outputs = node.run_safe(self.parcels, index)
                for output_name, output_value in outputs.items():
                    parcel = Parcel(
                        name=output_name,
                        value=output_value,
                        timestamp=time.time(),
                        node_id=node.node_id
                    )
                    self.parcels[output_name] = parcel
                    self._log(f"  -> produced parcel: {parcel}")
                    did_produce_outputs = True
        else:
            self._log(f"[run] {node}")
            required_parcels = node.get_required_parcels(self.parcels)
            self._log(f"  <- input parcels: {list(required_parcels.keys())}")

            outputs = node.run_safe(self.parcels)
            for output_name, output_value in outputs.items():
                parcel = Parcel(
                    name=output_name,
                    value=output_value,
                    timestamp=time.time(),
                    node_id=node.node_id
                )
                self.parcels[output_name] = parcel
                self._log(f"  -> produced parcel: {parcel}")
                did_produce_outputs = True

        return did_produce_outputs

    def _log(self, message: str):
        """Record a log line and echo it to stdout."""
        self.execution_log.append(message)
        print(message)

    def get_execution_log(self) -> List[str]:
        """Return the complete execution log."""
        return self.execution_log

    def _get_indexed_matches(self, requires: List[str], parcels: Dict[str, Parcel]) -> List[int]:
        """
        Find the indices shared by every indexed requirement.

        Example: if a node requires ["user"] and the store holds "user[0]",
        "user[1]", "user[2]", this returns [0, 1, 2].

        When a node requires multiple arrays, the engine uses a strict zip
        (intersection) strategy: it only runs for an index that exists for ALL
        indexed requirements, like Python's zip() stopping at the shortest list.
        An exact (non-indexed) requirement is treated as a broadcast constant.
        """
        common_indices = None

        for required in requires:
            if required in parcels:
                # Exact match: a broadcast constant, contributes no index set.
                continue

            current_requirement_indices = set()
            prefix = f"{required}["
            for parcel_name in parcels.keys():
                if parcel_name.startswith(prefix) and parcel_name.endswith("]"):
                    try:
                        index = int(parcel_name[len(prefix):-1])
                        current_requirement_indices.add(index)
                    except ValueError:
                        continue

            if common_indices is None:
                common_indices = current_requirement_indices
            else:
                common_indices.intersection_update(current_requirement_indices)

        if common_indices is None:
            return []

        return sorted(list(common_indices))

    def print_parcels(self):
        """Print all current parcels in a readable format."""
        print("\nCurrent parcels:")
        for name, parcel in self.parcels.items():
            print(f"  {name}: {parcel.value}")
        print()
