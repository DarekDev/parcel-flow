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
date: 26 May 2026
bibliography: paper.bib
---

# Summary

ParcelFlow is a **minimalist reference implementation** of a data-driven workflow engine, designed specifically as an educational resource for teaching orchestration concepts. Unlike production engines that prioritize scale and fault tolerance, ParcelFlow prioritizes **readability and conceptual clarity**. The entire core engine is implemented in under 600 lines of plain Python, allowing students to read, understand, and modify the internal logic of a workflow scheduler in a single lab session.

The software demonstrates core orchestration patterns—specifically **data-driven execution** (where tasks run automatically when inputs are available) and **implicit scatter/gather** (automatic array processing)—without the complexity of infrastructure setup or heavy frameworks.

# Statement of Need

## The Educational Gap

Teaching workflow orchestration and distributed computing concepts presents a specific challenge:
1.  **Production tools are too complex**: Industry orchestrators like Apache Airflow [@airflow] and Prefect [@prefect] require significant infrastructure (databases, message queues), complex configuration, and steep learning curves, because they prioritise production reliability. Scientific workflow systems like Nextflow [@ditommaso2017nextflow], Swift/T [@wozniak2013swift], Snakemake [@koster2012snakemake], and Pegasus [@deelman2015pegasus] handle large parallel dataflow graphs effectively, but are designed for high-performance computing (HPC) environments. Both categories require infrastructure that obscures the underlying idea.
2.  **Toy examples are too abstract**: Pseudocode or simple scripts fail to demonstrate the real challenges of state management, dependency resolution, and execution semantics in a graph.

Educators need a **"middle ground" tool**: a functioning, executable workflow engine that is simple enough to be studied as a "white box" but complex enough to exhibit real orchestration behaviours (dependency resolution, deadlock, scatter/gather, error propagation).

## A "Glass Box" for Orchestration

ParcelFlow fills this gap by providing a **transparent implementation** of standard workflow patterns. It serves as a laboratory bench where students can:
1.  **Observe** how a scheduler traverses a dependency graph (by logging internal engine state).
2.  **Experiment** with execution semantics (e.g., "What happens if I change the matching logic from exact-match to regex?").
3.  **Implement** missing features as effective learning exercises (e.g., "Add a retry mechanism to the base node").

The novelty of ParcelFlow lies not in a new computational paradigm, but in its **pedagogical design**: stripping away all non-essential production features (persistence, distributed workers, authentication) to expose the core logic of reactive orchestration in its simplest functional form.

# Learning Objectives

ParcelFlow is designed to support a single lab or lecture within a systems,
distributed-computing, or software-architecture course, in which students:
1.  **Differentiate** between control-flow (scripted) and data-flow (reactive) execution models.
2.  **Implement** the scatter/gather pattern, understanding how single-item logic scales to arrays without explicit loops.
3.  **Diagnose** a data-flow deadlock: a "dead" branch where a node waits on a parcel that no node ever produces. (Detecting true cycles before execution is a natural extension exercise.)
4.  **Distinguish** the *structure* of parallel work from its *execution*, and **critique** scheduler trade-offs such as eager vs. lazy evaluation.

# Comparison with Existing Tools

| Feature | Apache Airflow [@airflow] / Prefect [@prefect] | Common Workflow Language (CWL) [@amstutz2016common] | **ParcelFlow** |
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
The engine resolves the graph at runtime. This forces students to think in terms of **data availability**, a concept central to distributed systems and to reactive programming, the model underlying streaming systems such as Apache Beam [@beam] and reactive libraries such as RxJS [@rxjs].

## 3. The "Scatter" Pattern as a primitive
ParcelFlow implements array processing via pattern matching (`user` matches `user[0]`, `user[1]`, etc.). This gives a concrete implementation of the "map" or "scatter" operation found in MapReduce and scientific workflows. Crucially, the per-item runs are *independent* — that independence is the logical structure such systems parallelise — but ParcelFlow itself executes them sequentially (see Limitations). The distinction between the parallel *structure* of the work and its sequential *execution* is made an explicit teaching point rather than glossed over.

## 4. Strict "Zip" Semantics for Multi-Array Inputs
To avoid ambiguity when a node requires multiple arrays (e.g., `A` and `B`), the engine implements a strict **Zip/Intersection strategy**. The node executes `min(len(A), len(B))` times, matching `A[i]` with `B[i]`. This provides a deterministic behavior suitable for classroom demonstration, avoiding the complexity of Cartesian products often found in more advanced systems.

# Educational usage

The `education/` folder contains the teaching material:
1.  **Lecture notes** (`LECTURE_NOTES.md`): a self-contained written lecture on the data-flow model, the engine loop, deadlock, and scatter/gather.
2.  **Concept walkthrough** (`01_concepts_walkthrough.ipynb`): a guided tour showing how parcels trigger node execution and how chaining emerges from data.
3.  **Scatter/gather lab** (`02_scatter_gather_lab.ipynb`): the array pattern and zip semantics, with an exercise.
4.  **Student lab** (`03_student_lab.ipynb`): exercises in which students implement a node, diagnose a deadlock, and (as a capstone) make the independent per-item work run concurrently. Each exercise has an assertion-based test cell.
5.  **Instructor guide** (`INSTRUCTOR_GUIDE.md`) and worked **solutions** (`solutions/`).

The engine itself ships with a unit-test suite (`python run_tests.py`) that instructors can run to confirm the engine behaves as described before class.

# Limitations

As an educational reference implementation:
*   **Sequential Execution**: By default, the Python implementation runs locally and sequentially (even conceptually parallel tasks) to ensure logs are readable and deterministic for students.
*   **In-Memory State**: State is lost if the process crashes, simplifying the code (no database code cluttering the scheduler logic).
*   **Performance**: While efficient for small batches (10-100 items), it is not optimized for massive scale.

# References
