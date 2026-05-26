# Instructor Guide

This guide is for educators using ParcelFlow in a class, lab, or workshop. It maps
the material to learning objectives, suggests timing, and flags where students
typically get stuck.

## What this material is for

ParcelFlow is a single, readable engine (under 600 lines) for teaching **one idea**:
that an execution order can emerge from data dependencies rather than being written
down. It suits a 60–120 minute slot in a course on distributed systems, cloud
computing, software architecture, or programming paradigms — anywhere students will
later meet a real workflow tool (Airflow, Nextflow, Prefect) and benefit from
understanding the data-flow concept first.

It is deliberately *not* a survey of orchestration tools and not a production engine.
Scope it as "read and modify a tiny scheduler," not "learn workflow engineering."

## Prerequisites

- Comfortable with Python classes, inheritance, lists, and dicts (~1 prior session).
- For the capstone only: awareness of threads is helpful but not required; the
  exercise introduces `ThreadPoolExecutor` by example.
- No infrastructure. `git clone`, Python 3.8+, and (optionally) Jupyter. The
  notebooks import the engine via a relative path that works from the repo root or
  the `education/` folder.

## Suggested session plan (90 minutes)

| Time | Activity | Materials |
|---|---|---|
| 0–15 | Lecture: control flow vs data flow; the two nouns (Parcel, Node) | `LECTURE_NOTES.md` §1–2 |
| 15–35 | Walk the engine loop live; run Module 1 | `01_concepts_walkthrough.ipynb`, `workflow_engine.py` |
| 35–55 | Scatter/gather; run Module 2 demo cells | `02_scatter_gather_lab.ipynb`, `LECTURE_NOTES.md` §5 |
| 55–80 | Students do Module 3 Exercises 1–2 | `03_student_lab.ipynb` |
| 80–90 | Debrief deadlock; assign capstone as homework | `LECTURE_NOTES.md` §4 |

For a 60-minute version, drop Module 2 to a demo and assign it as reading. For a
two-session version, give the capstone (Exercise 3) its own slot and discuss the
structure-vs-execution distinction at length.

## Objectives mapped to activities

1. **Distinguish control-flow from data-flow execution.** — Lecture §1; observed
   directly when Module 1 runs nodes with partial vs full data.
2. **Read and explain the scheduler loop.** — Module 1 §2–3 alongside
   `workflow_engine.py`.
3. **Implement nodes that fit the model.** — Module 3 Exercise 1; Module 2 exercise.
4. **Diagnose a data-flow deadlock.** — Module 3 Exercise 2, using the engine's
   end-of-run deadlock report.
5. **Explain scatter/gather and zip semantics.** — Module 2.
6. **Separate the *structure* of parallel work from its *execution*.** — Module 3
   capstone (Exercise 3).

## Common student difficulties

- **"Why didn't my node run?"** Almost always a name mismatch between one node's
  `outputs` and another's `requires`. Point them at the `DEADLOCK: ...` line the
  engine prints at the end of a run — it names the missing parcel.
- **Confusing the index.** In per-item nodes, students read `parcels['user']`
  instead of `parcels[f'user[{index}]']`. Remind them the engine passes `index`.
- **Expecting parallelism.** Students often assume scatter/gather means the items
  run in parallel. Use this to teach the distinction explicitly (capstone). The
  engine is sequential; the *work* is parallelizable.
- **Editing the test cells.** Tell students the test cells are fixed and print
  `PASS`; their job is the cell above.

## Assessment

A lightweight rubric (each exercise is pass/fail on its test cell, plus a short
written answer):

- Exercise 1 (Splitter) — correctness. *Q: which node's output makes this node
  ready?*
- Exercise 2 (Deadlock) — correctness. *Q: in your own words, why does a data-flow
  engine not raise an error here?*
- Exercise 3 (Capstone) — correctness + speedup. *Q: why is it safe to run the
  per-item work concurrently? What property of the items guarantees it?*

Worked solutions are in `solutions/SOLUTIONS.md`. Keep that file away from students
until after the exercise.

## Running the automated checks

The repository ships a unit-test suite for the engine itself (not the exercises):

```
python run_tests.py
```

Use it to confirm the engine works in your environment before class.
