# ParcelFlow: Educational Workflow Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Educational Resource](https://img.shields.io/badge/Status-Educational_Resource-green.svg)](https://github.com/DarekDev/parcel-flow)

**ParcelFlow** is a reference implementation of a data-driven workflow engine, designed for **teaching orchestration concepts**.

It allows students to study, modify, and experiment with the core logic of a workflow scheduler in under 600 lines of plain Python.

## 🎯 Learning Objectives

After completing the included laboratory modules, students will be able to:
1.  **Explain** the difference between Control-Flow (scripted) and Data-Flow (reactive) execution models.
2.  **Implement** the "Scatter/Gather" pattern (MapReduce logic) on local data arrays.
3.  **Debug** dependency graphs by identifying cyclic dependencies and missing data requirements.
4.  **Critique** the trade-offs between implicit (emergent) and explicit (DAG-defined) orchestration.

    > *Note: When a node requires multiple arrays (e.g., `user` and `location`), the engine applies a **Zip strategy** (matching index `i` to `i`), executing `min(len(inputs))` times.*

## 👨‍🏫 Instructor Guide

-   **Target Audience**: Undergraduate/Graduate Computer Science students in "Distributed Systems", "Cloud Computing", or "Software Architecture" courses.
-   **Prerequisites**: Basic Python proficiency (classes, inheritance, lists/dicts).
-   **Time Required**: ~90 minutes for the core "Concept Walkthrough" and "Scheduler Lab".
-   **Setup**: Zero dependencies. `git clone` and run.

## 📚 Course Modules

The `education/` folder contains Jupyter Notebooks that serve as self-paced labs:

### 1. [Concepts Walkthrough](education/01_concepts_walkthrough.ipynb)
A guided tour of the engine's internals.
-   *Topics*: Nodes, Parcels, The Scheduler Loop, Implicit Graphs.

### 2. [Student Lab](education/02_student_lab.ipynb)
Hands-on exercises.
-   *Exercise 1*: Implementing a "Filter Node" (Conditional Execution).
-   *Exercise 2*: Debugging a "Deadlock" workflow.
-   *Exercise 3*: Implementing a custom "Priority Scheduler".

## 🚀 Quick Start (CLI)

While the notebooks are the primary educational interface, you can also run the engine from the terminal to see it in action.

```bash
# Clone the repository
git clone https://github.com/DarekDev/parcel-flow.git
cd parcel-flow

# Run the array processing demo
python main.py array --verbose
```

### What you will see:
The logs demonstrate **Reactive Execution**:
```text
[ENGINE] Parcel 'request_data' produced.
[ENGINE] Node 'ArraySpreadNode' IS READY (Requirements met: ['request_data'])
[ENGINE] Executing 'text_splitter'...
[ENGINE] Produced indexed parcels: ['item[0]', 'item[1]', 'item[2]']
[ENGINE] Node 'ProcessItemNode' IS READY (Requirements met: ['item[0]'])
...
```
Notice how `ProcessItemNode` triggers automatically for *each* item, without a `for` loop in the code!

## 🤝 Contributing

This project is open-source educational material. We welcome:
-   New "Broken Workflow" scenarios for students to debug.
-   Visualizations tools for the execution graph.
-   Translations of the notebooks.

## 📄 License

MIT License. Free for use in academic and commercial settings.

---
*Note: This is an educational reference implementation. It runs sequentially in-memory for readability and is not intended for production scale.*
