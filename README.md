# ParcelFlow: An Educational Workflow Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**ParcelFlow** is a small, readable implementation of a *data-driven* workflow
engine, written for teaching. In under 600 lines of dependency-free Python, students
can read, run, and modify the entire scheduler in a single lab session.

The one idea it teaches: an execution order can **emerge from data dependencies**
instead of being written down. Each node declares what data it `requires` and what
it `outputs`; a node runs when its required data exists; the schedule is a
consequence of the data, not a wiring diagram.

## Learning objectives

After the included material, students will be able to:

1. **Explain** the difference between control-flow (scripted) and data-flow
   (reactive) execution.
2. **Read** a scheduler loop and trace how nodes become ready from data alone.
3. **Implement** nodes that fit the model, and **diagnose** a data-flow *deadlock*
   (a node waiting on a parcel no node produces).
4. **Describe** the scatter/gather pattern and the strict zip semantics for multiple
   arrays.
5. **Distinguish** the *structure* of parallel work from its *execution*: the engine
   runs sequentially by design, while the per-item work it expresses is independent
   and therefore parallelizable (the capstone exercise).

## Teaching materials (`education/`)

- **[LECTURE_NOTES.md](education/LECTURE_NOTES.md)** — a self-contained lecture
  (~45 min read) covering the model, the engine loop, deadlock, and scatter/gather.
- **[01_concepts_walkthrough.ipynb](education/01_concepts_walkthrough.ipynb)** — a
  guided tour of the engine: Parcels, Nodes, the scheduler loop, implicit chaining.
- **[02_scatter_gather_lab.ipynb](education/02_scatter_gather_lab.ipynb)** — spreading
  a list into per-item work, gathering results, and zip semantics, with an exercise.
- **[03_student_lab.ipynb](education/03_student_lab.ipynb)** — hands-on exercises:
  1. Implement a `SplitterNode`.
  2. Diagnose and fix a deadlock.
  3. *(Capstone)* Make the independent per-item work run concurrently.
- **[INSTRUCTOR_GUIDE.md](education/INSTRUCTOR_GUIDE.md)** — session plan, objective
  mapping, common student difficulties, and an assessment rubric.
- **[solutions/SOLUTIONS.md](education/solutions/SOLUTIONS.md)** — worked answers
  (for instructors).

## Quick start

```bash
git clone https://github.com/DarekDev/parcel-flow.git
cd parcel-flow

# Run an example workflow
python main.py simple
python main.py array --verbose

# Run the engine's unit tests
python run_tests.py
```

### What the logs show

The engine prints each pass and the parcels it produces. For `python main.py simple`,
the core of the log is (abbreviated):

```text
Starting workflow with 4 node(s)
Initial parcels: ['request_data']
--- Pass 1 ---
[run] ValidateNode(validate)
  <- input parcels: ['request_data']
  -> produced parcel: Parcel(validation_result=...)
[run] TransformNode(transform)
  -> produced parcel: Parcel(transformed_data=DATA IS VALID)
[run] ResponseNode(response)
  -> produced parcel: Parcel(response=...)
--- Pass 2 ---
No more nodes can run - workflow complete
```

Each node ran as soon as the parcel it required appeared — no order was specified.
If a node requires a parcel that no node produces, the engine reports it at the end:

```text
DEADLOCK: BadNode(bad) never ran - waiting for parcel(s) ['step_one'] that no node produced
```

## Example workflows

- `simple` — a linear chain (`request -> validate -> transform -> response`).
- `independent` — two branches that depend only on the same input, so both become
  eligible in one pass.
- `array` — scatter/gather: a list is spread into indexed parcels, processed per
  item with no explicit loop, then collected back.

## Scope

ParcelFlow is a teaching model, not a production tool. Execution is sequential and
in-memory by design, so the logs are deterministic and readable. For production
orchestration see Apache Airflow, Prefect, or Nextflow; ParcelFlow exists to make
the underlying data-flow idea legible before you meet those systems.

## Contributing

Contributions that improve the teaching value are welcome: new exercises, additional
"broken workflow" scenarios for debugging practice, execution-graph visualisations,
or notebook translations.

## License

MIT License. Free for academic and commercial use.
