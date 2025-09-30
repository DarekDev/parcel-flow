#!/usr/bin/env python3
"""
Matrix Minimal Example - Command Line Interface

A didactic demonstration of the parcel-based execution paradigm.
Shows how reactive data flow enables natural parallelism without complex orchestration.
"""

import sys
import argparse
from typing import List
from workflow_engine import WorkflowEngine
from workflows import (
    create_simple_workflow, create_parallel_workflow, create_array_workflow,
    get_workflow_data, get_workflow_description, list_workflows
)


def run_workflow(workflow_name: str, verbose: bool = False):
    """Run a specific workflow and display the results."""
    
    print("=" * 60)
    print(f"🎯 Running Workflow: {workflow_name.upper()}")
    print("=" * 60)
    
    # Get workflow description
    description = get_workflow_description(workflow_name)
    print(description)
    
    # Create workflow nodes
    if workflow_name == "simple":
        nodes = create_simple_workflow()
    elif workflow_name == "parallel":
        nodes = create_parallel_workflow()
    elif workflow_name == "array":
        nodes = create_array_workflow()
    else:
        print(f"❌ Unknown workflow: {workflow_name}")
        return
    
    # Get sample data
    initial_data = get_workflow_data(workflow_name)
    
    print(f"📊 Initial Data: {initial_data}")
    print(f"🔧 Nodes: {[str(node) for node in nodes]}")
    print()
    
    # Create and run workflow engine
    engine = WorkflowEngine()
    final_parcels = engine.execute_workflow(nodes, initial_data)
    
    # Display results
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS")
    print("=" * 60)
    
    if "response" in final_parcels:
        response = final_parcels["response"].value
        print(f"✅ Response: {response}")
    else:
        print("❌ No response generated")
    
    if verbose:
        print("\n📦 All Parcels:")
        for name, parcel in final_parcels.items():
            print(f"  {name}: {parcel.value}")
    
    print(f"\n📈 Execution completed in {len(engine.get_execution_log())} steps")


def list_available_workflows():
    """List all available workflows with descriptions."""
    print("🎯 Available Workflows:")
    print("=" * 40)
    
    for workflow_name in list_workflows():
        description = get_workflow_description(workflow_name)
        print(f"\n{workflow_name.upper()}:")
        print(description)


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description="Matrix Minimal Example - Parcel-based execution paradigm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py simple          # Run simple linear workflow
  python main.py parallel        # Run parallel processing workflow  
  python main.py array           # Run array spreading workflow
  python main.py --list          # List available workflows
  python main.py array --verbose # Run with detailed output
        """
    )
    
    parser.add_argument(
        "workflow",
        nargs="?",
        choices=list_workflows() + ["all"],
        help="Workflow to run (or 'all' to run all workflows)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available workflows"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed execution information"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_workflows()
        return
    
    if not args.workflow:
        print("❌ Please specify a workflow to run or use --list to see available workflows")
        print("Use --help for more information")
        return
    
    if args.workflow == "all":
        for workflow_name in list_workflows():
            run_workflow(workflow_name, args.verbose)
            print("\n" + "=" * 80 + "\n")
    else:
        run_workflow(args.workflow, args.verbose)


if __name__ == "__main__":
    main()
