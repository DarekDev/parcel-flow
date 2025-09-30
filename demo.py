#!/usr/bin/env python3
"""
Matrix Minimal Example - Complete Demonstration

This script runs all example workflows to demonstrate the parcel-based execution paradigm.
Perfect for showing the principles clearly and concisely.
"""

from main import run_workflow


def main():
    """Run all workflows to demonstrate the paradigm."""
    
    print("🎯 MATRIX MINIMAL EXAMPLE - PARCEL-BASED EXECUTION PARADIGM")
    print("=" * 80)
    print()
    print("This demonstration shows how reactive data flow enables natural parallelism")
    print("without complex orchestration. Nodes run when data becomes available!")
    print()
    
    workflows = [
        ("simple", "Basic Linear Chain"),
        ("parallel", "Parallel Processing"), 
        ("array", "Array Spreading (Key Demo)")
    ]
    
    for i, (workflow_name, description) in enumerate(workflows, 1):
        print(f"\n{'='*20} WORKFLOW {i}: {description.upper()} {'='*20}")
        run_workflow(workflow_name, verbose=False)
        
        if i < len(workflows):
            print("\n" + "="*80)
            try:
                input("Press Enter to continue to next workflow...")
            except EOFError:
                print("Continuing automatically...")
    
    print("\n" + "="*80)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("="*80)
    print()
    print("Key Takeaways:")
    print("• Nodes are reactive - they run when data is available")
    print("• No static connections or predefined execution order")
    print("• Array spreading creates natural parallelism")
    print("• No explicit loops needed for parallel processing")
    print("• Clean, simple, and scalable architecture")
    print()


if __name__ == "__main__":
    main()
