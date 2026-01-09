---
title: 'ParcelFlow: A Minimalist, Reactive Workflow Engine for Teaching Orchestration Concepts'
tags:
  - Python
  - workflow orchestration
  - educational tool
  - data-driven execution
  - scatter-gather pattern
authors:
  - name: Dariusz Młodnicki
    orcid: 0009-0001-5634-393X
    affiliation: 1
affiliations:
 - name: Technology Department, Key Search AG, Switzerland
   index: 1
date: 4 November 2024
bibliography: paper.bib
---

# Summary

ParcelFlow is a **minimalist reference implementation** of a data-driven workflow engine, designed specifically as an educational resource for teaching orchestration concepts. Unlike production engines that prioritize scale and fault tolerance, ParcelFlow prioritizes **readability and conceptual clarity**. The entire core engine is implemented in under 600 lines of plain Python, allowing students to read, understand, and modify the internal logic of a workflow scheduler in a single lab session.

The software demonstrates core orchestration patterns—specifically **data-driven execution** (where tasks run automatically when inputs are available) and **implicit scatter/gather** (automatic array processing)—without the complexity of infrastructure setup or heavy frameworks.

# Statement of Need

## The Educational Gap

Teaching workflow orchestration and distributed computing concepts presents a specific challenge:
1.  **Production tools are too complex**: Systems like Apache Airflow \citep{airflow} or Prefect \citep{prefect} require significant infrastructure (databases, message queues), complex configuration, and steep learning curves. Students spend more time debugging environments than learning concepts.
2.  **Toy examples are too abstract**: Pseudocode or simple scripts fail to demonstrate the real challenges of state management, dependency resolution, and execution semantics in a graph.

Educators need a **"middle ground" tool**: a functioning, executable workflow engine that is simple enough to be studied as a "white box" but complex enough to exhibit real orchestration behaviors (DAG resolution, parallelism, error propagation).

## A "Glass Box" for Orchestration

ParcelFlow fills this gap by providing a **transparent implementation** of standard workflow patterns. It serves as a laboratory bench where students can:
1.  **Observe** how a scheduler traverses a dependency graph (by logging internal engine state).
2.  **Experiment** with execution semantics (e.g., "What happens if I change the matching logic from exact-match to regex?").
3.  **Implement** missing features as effective learning exercises (e.g., "Add a retry mechanism to the base node").

The novelty of ParcelFlow lies not in a new computational paradigm, but in its **pedagogical design**: stripping away all non-essential production features (persistence, distributed workers, authentication) to expose the core logic of reactive orchestration in its simplest functional form.

# Learning Objectives

ParcelFlow is designed to support a "Systems & Architecture" module where students:
1.  **Differentiate** between Control-Flow (scripted) and Data-Flow (reactive) execution models.
2.  **Implement** the "Scatter/Gather" pattern, understanding how single-item logic scales to arrays without explicit loops.
3.  **Debug** dependency graphs, identifying cycles and "dead" branches where data is never produced.
4.  **Critique** scheduler designs, comparing the trade-offs of eager vs. lazy execution.

# Comparison with Existing Tools

| Feature | Apache Airflow / Prefect | Common Workflow Language (CWL) | **ParcelFlow** |
| :--- | :--- | :--- | :--- |
| **Primary Goal** | Production Reliability | Interoperability/Reproducibility | **Education & Prototyping** |
| **Setup Time** | Hours (DB, Queue, Worker) | Minutes (Runner installation) | **Seconds (Zero dependencies)** |
| **Codebase Size** | >100,000 LOC | N/A (Specification) | **~550 LOC** |
| **Execution Model** | Explicit DAG Objects | Explicit/Implicit DAG | **Emergent (Data-Driven)** |
| **Student Role** | User (writes DAGs) | User (writes YAML) | **Architect (modifies Engine)** |

In a classroom setting, Airflow teaches students *how to use a specific tool*. ParcelFlow teaches students *how workflow engines work*.

# Pedagogical Design Features

## 1. Zero-Dependency "One File" Architecture
The core logic resides entirely in standard Python. This ensures that the barrier to entry is zero: any student with Python installed can clone and run the engine. There are no "black boxes" hidden in third-party libraries.

## 2. Emergent Graph Construction
Instead of declaring a graph object (like `dag = DAG()`), students define nodes with requirements:
```python
# Student defines what data is NEEDED, not what node runs PREVIOUSLY
class ProcessNode(BaseNode):
    def __init__(self):
        super().__init__(requires=["raw_data"], outputs=["clean_data"])
```
The engine resolves the graph at runtime. This forces students to think in terms of **data availability**, a critical concept in distributed systems and functional reactive programming.

## 3. The "Scatter" Pattern as a primitive
ParcelFlow implements array processing via pattern matching (`user` matches `user[0]`, `user[1]`, etc.). This provides a concrete implementation of the "Map" or "Scatter" operation found in MapReduce and scientific workflows, demystifying how big data systems parallelize work.

## 4. Strict "Zip" Semantics for Multi-Array Inputs
To avoid ambiguity when a node requires multiple arrays (e.g., `A` and `B`), the engine implements a strict **Zip/Intersection strategy**. The node executes `min(len(A), len(B))` times, matching `A[i]` with `B[i]`. This provides a deterministic behavior suitable for classroom demonstration, avoiding the complexity of Cartesian products often found in more advanced systems.

# Educational usage

The repository includes a **Jupyter Notebook Laboratory** (`education/`) that guides students through:
1.  **Concept Walkthrough**: Interactive visualization of how data tokens ("parcels") trigger node execution.
2.  **Lab Exercises**: Structural challenges where students must fix broken schedulers or implement custom node logic to pass unit tests.

# Limitations

As an educational reference implementation:
*   **Sequential Execution**: By default, the Python implementation runs locally and sequentially (even conceptually parallel tasks) to ensure logs are readable and deterministic for students.
*   **In-Memory State**: State is lost if the process crashes, simplifying the code (no database code cluttering the scheduler logic).
*   **Performance**: While efficient for small batches (10-100 items), it is not optimized for massive scale.

# Acknowledgements

We acknowledge the feedback from early student testers who helped refine the API to be more intuitive for complete beginners.

# References
