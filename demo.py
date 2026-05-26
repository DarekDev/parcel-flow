#!/usr/bin/env python3
"""
ParcelFlow: run every example workflow in sequence.

A quick way to see all three example workflows back to back.
"""

from main import run_workflow


def main():
    """Run all workflows in order."""

    print("PARCELFLOW - DATA-DRIVEN EXECUTION")
    print("=" * 80)
    print()
    print("Each node runs when the data it requires becomes available, so the")
    print("execution order emerges from data dependencies rather than wiring.")
    print()

    workflows = [
        ("simple", "Simple Linear Chain"),
        ("independent", "Independent Branches"),
        ("array", "Array Spreading (Scatter/Gather)")
    ]

    for i, (workflow_name, description) in enumerate(workflows, 1):
        print(f"\n{'='*20} WORKFLOW {i}: {description.upper()} {'='*20}")
        run_workflow(workflow_name, verbose=False)

        if i < len(workflows):
            print("\n" + "=" * 80)
            try:
                input("Press Enter to continue to the next workflow...")
            except EOFError:
                print("Continuing automatically...")

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Takeaways:")
    print("- Nodes run when their required parcels are available.")
    print("- There is no static execution order or wiring between nodes.")
    print("- Array spreading runs per-item work without an explicit loop.")
    print("- Execution is sequential and deterministic by design.")
    print()


if __name__ == "__main__":
    main()
