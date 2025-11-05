#!/usr/bin/env python3
"""
Benchmark script for measuring ParcelFlow performance vs baseline Python.

This script measures:
1. Execution time (milliseconds)
2. Memory usage (MB)

For varying array sizes to populate Table 2 in the paper.
"""

import time
import tracemalloc
import sys
from workflow_engine import WorkflowEngine
from nodes import (
    RequestNode, ArraySpreadNode, ProcessItemNode, 
    CollectNode, ResponseNode
)


def create_test_workflow():
    """Create the array processing workflow for testing"""
    return [
        RequestNode("request"),
        ArraySpreadNode("array_spread", "request_data", "user"),
        ProcessItemNode("process_item", "user", "processed"),
        CollectNode("collect", "processed", "result", "user_meta"),
        ResponseNode("response", "result")
    ]


def benchmark_parcelflow(array_size, verbose=False):
    """
    Benchmark ParcelFlow with given array size.
    
    Args:
        array_size: Number of items in the test array
        verbose: If True, suppress engine output
        
    Returns:
        tuple: (elapsed_ms, memory_mb)
    """
    # Create workflow
    nodes = create_test_workflow()
    
    # Create test data
    initial_data = {"request_data": [f"user_{i}" for i in range(array_size)]}
    
    # Suppress print output if not verbose
    if not verbose:
        sys.stdout = open('/dev/null', 'w')
    
    # Start memory tracking
    tracemalloc.start()
    
    # Time execution
    start = time.perf_counter()
    engine = WorkflowEngine()
    result = engine.execute_workflow(nodes, initial_data)
    end = time.perf_counter()
    
    # Get memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Restore stdout
    if not verbose:
        sys.stdout = sys.__stdout__
    
    elapsed_ms = (end - start) * 1000
    memory_mb = peak / (1024 * 1024)
    
    return elapsed_ms, memory_mb


def benchmark_baseline(array_size):
    """
    Benchmark pure Python with explicit loops (baseline).
    
    Simulates equivalent processing without ParcelFlow overhead.
    
    Args:
        array_size: Number of items to process
        
    Returns:
        tuple: (elapsed_ms, memory_mb)
    """
    data = [f"user_{i}" for i in range(array_size)]
    
    tracemalloc.start()
    start = time.perf_counter()
    
    # Simulate equivalent processing
    # This mimics what ProcessItemNode does
    results = []
    for item in data:
        processed = f"PROCESSED: {item.upper()}"
        results.append(processed)
    
    # Create response (mimics ResponseNode)
    response = {
        "status": "success",
        "data": results,
        "timestamp": time.time()
    }
    
    end = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    elapsed_ms = (end - start) * 1000
    memory_mb = peak / (1024 * 1024)
    
    return elapsed_ms, memory_mb


def run_benchmarks(sizes, runs=5):
    """
    Run benchmarks for multiple array sizes with multiple runs for averaging.
    
    Args:
        sizes: List of array sizes to test
        runs: Number of runs per size for averaging
        
    Returns:
        dict: Results for each size
    """
    results = {}
    
    print(f"\nRunning benchmarks with {runs} runs per size...\n")
    
    for size in sizes:
        print(f"Testing array size {size}...", end=" ", flush=True)
        
        pf_times = []
        pf_mems = []
        bl_times = []
        bl_mems = []
        
        for run in range(runs):
            # ParcelFlow benchmark
            pf_time, pf_mem = benchmark_parcelflow(size, verbose=False)
            pf_times.append(pf_time)
            pf_mems.append(pf_mem)
            
            # Baseline benchmark
            bl_time, bl_mem = benchmark_baseline(size)
            bl_times.append(bl_time)
            bl_mems.append(bl_mem)
        
        # Calculate averages
        results[size] = {
            'pf_time': sum(pf_times) / len(pf_times),
            'pf_mem': sum(pf_mems) / len(pf_mems),
            'bl_time': sum(bl_times) / len(bl_times),
            'bl_mem': sum(bl_mems) / len(bl_mems),
            'overhead_pct': ((sum(pf_times) / len(pf_times)) / (sum(bl_times) / len(bl_times)) - 1) * 100
        }
        
        print("Done!")
    
    return results


def print_results(results):
    """Print results in a formatted table"""
    print("\n" + "=" * 90)
    print("BENCHMARK RESULTS")
    print("=" * 90)
    print(f"{'Array Size':<12} | {'ParcelFlow (ms)':<16} | {'Baseline (ms)':<14} | {'Memory (MB)':<12} | {'Overhead':<10}")
    print("-" * 90)
    
    for size, data in sorted(results.items()):
        print(f"{size:<12} | {data['pf_time']:>14.2f} | {data['bl_time']:>12.2f} | {data['pf_mem']:>10.2f} | {data['overhead_pct']:>7.1f}%")
    
    print("=" * 90)
    print("\nNOTE: Memory column shows ParcelFlow peak memory usage.")
    print("      Overhead shows ParcelFlow execution time vs baseline.")


def print_latex_table(results):
    """Print results formatted for LaTeX table"""
    print("\n" + "=" * 70)
    print("LATEX TABLE FORMAT (copy into paper):")
    print("=" * 70)
    print()
    
    for size, data in sorted(results.items()):
        print(f"{size} items & {data['pf_time']:.1f} & {data['bl_time']:.1f} & {data['pf_mem']:.2f} \\\\")
    
    print()
    print("Copy the lines above into Table 2 in parcelflow-paper.tex")
    print("(Replace the [TODO] placeholders)")


def print_system_info():
    """Print system information for paper hardware specification"""
    import platform
    import os
    
    print("\n" + "=" * 70)
    print("SYSTEM INFORMATION (add to paper):")
    print("=" * 70)
    print(f"Python version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")
    
    # Try to get more detailed CPU info on macOS
    if platform.system() == "Darwin":
        try:
            import subprocess
            cpu_info = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
            print(f"CPU: {cpu_info}")
        except:
            pass
    
    print("\nUse this in the paper's performance section where it says:")
    print("[TODO: SPECIFY HARDWARE]")
    print("=" * 70)


def main():
    """Main benchmark execution"""
    print("ParcelFlow Performance Benchmark")
    print("=" * 70)
    
    # Test array sizes (matching what's in the paper)
    sizes = [10, 50, 100, 500]
    runs_per_size = 5
    
    print(f"\nConfiguration:")
    print(f"  Array sizes: {sizes}")
    print(f"  Runs per size: {runs_per_size}")
    
    # Print system info
    print_system_info()
    
    # Run benchmarks
    results = run_benchmarks(sizes, runs_per_size)
    
    # Print results
    print_results(results)
    print_latex_table(results)
    
    # Print next steps
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Copy the LaTeX table lines above into parcelflow-paper.tex")
    print("2. Search for '[TODO]' and replace with the system information")
    print("3. Update the hardware specification with your system details")
    print("4. Compile the paper to verify the table renders correctly")
    print("=" * 70)


if __name__ == "__main__":
    main()
