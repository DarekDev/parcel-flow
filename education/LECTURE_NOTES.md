# Lecture Notes: Data-Driven Workflow Execution

These notes accompany the ParcelFlow notebooks. They are written to be read on
their own as a single lecture (roughly 45 minutes of reading, longer with the
notebooks) for a systems, distributed-computing, or software-architecture course.
They assume you are comfortable with Python classes and dictionaries, but assume
nothing about schedulers or workflow engines.

The goal is narrow and honest: to understand *one idea well* — how an execution
order can emerge from data dependencies instead of being written down in advance —
by reading and modifying a small engine that does exactly that and nothing else.

---

## 1. Two ways to decide what runs next

Every system that runs a sequence of steps has to answer one question: *what runs
next?* There are two broad answers.

**Control flow.** You write the order down. A script runs line by line; a function
calls another function; a DAG (directed acyclic graph) in a tool like Apache
Airflow lists tasks and the edges between them. The order is explicit and visible
in the source. This is how most code you have written works.

**Data flow.** You do not write the order down. Instead, each step declares what
data it *needs* and what data it *produces*. A step becomes runnable the moment all
the data it needs exists. The order is not written anywhere — it emerges at runtime
from which data is available. This is the model spreadsheets use (a cell
recalculates when its inputs change), and it is the model ParcelFlow uses.

The distinction matters because it changes *what you have to think about*. In
control flow, you are responsible for ordering; a bug looks like "I called these in
the wrong order." In data flow, ordering is not your job — but making sure the data
a step needs is actually produced *is* your job, and a bug looks like "this step is
waiting for data that nothing ever creates."

---

## 2. The two nouns: Parcel and Node

ParcelFlow has exactly two concepts.

A **Parcel** is a named piece of data: a name, a value, and a timestamp. That is
all. Parcels live in a single shared store (a dictionary) for the duration of a run.

A **Node** is a unit of work. A node does not know what runs before or after it. It
knows only two things:

- `requires`: the names of the parcels it needs as input.
- `outputs`: the names of the parcels it will produce.

That is the whole vocabulary. A node is "ready" when every name in its `requires`
list is present in the parcel store. When it runs, it adds its `outputs` to the
store, which may in turn make other nodes ready.

Notice what is *absent*: there is no edge, no arrow, no `node_a.then(node_b)`. A
node never names another node. The connection between two nodes exists only because
one produces a parcel name the other requires. This is sometimes called *implicit*
or *emergent* wiring, and it is the heart of the model.

---

## 3. The engine loop

The scheduler is deliberately tiny. In plain English:

```
seed the store with the initial data
repeat:
    for each node:
        if all of its required parcels exist (and it hasn't run yet):
            run it, and add its outputs to the store
    if no node ran during this pass:
        stop
```

Read the loop in `workflow_engine.py` alongside this — it is under a hundred lines
and matches the pseudocode closely.

Three things are worth pausing on:

1. **The loop is a fixed-point computation.** It keeps making passes until a pass
   changes nothing. "Nothing changed" is the signal that the workflow is done. This
   is the same shape as many real systems (build tools, reactive UIs, constraint
   solvers): keep applying rules until the state stops moving.

2. **Order within a pass is not meaningful.** If two nodes are both ready in the
   same pass, the engine runs them one after the other, but their order relative to
   each other does not matter — neither depends on the other's output. That
   *independence* is a real and useful property; see §5.

3. **A node runs once.** Once a node has produced its (non-indexed) outputs, it is
   no longer ready, so it will not run again. This is what makes the loop terminate
   for an ordinary workflow.

---

## 4. When nothing happens: deadlock and the cost of implicit wiring

The implicit-wiring model has a price, and it is important to teach it honestly
rather than hide it.

In control flow, if you forget a step, you usually get a loud error: an undefined
name, a failed call. In data flow, if a node requires a parcel that no node ever
produces, the node simply *never becomes ready*. There is no crash. The work just
quietly never happens.

Consider a node that declares `requires=["step_one"]` while the node upstream
actually produces a parcel named `step1`. The names do not match, so the downstream
node waits forever for a parcel that will never exist. This is the data-flow version
of a deadlock, and it is the single most common mistake students make with this
model.

ParcelFlow surfaces this instead of swallowing it. When the loop finishes, the
engine checks which nodes never ran and reports each one together with the parcel
names it was still waiting for:

```
DEADLOCK: SimpleNode(stuck) never ran - waiting for parcel(s) ['step_one'] that no node produced
```

This is a teaching decision worth making explicit: a good system for *learning*
should make its failure modes visible. The exercise in the student lab walks
through diagnosing exactly this situation. (A production engine would go further
and detect true cycles — A needs B, B needs A — before running at all; that is a
reasonable extension exercise.)

---

## 5. Scatter and gather: the structure of a map

The one pattern beyond simple chaining that ParcelFlow demonstrates is
**scatter/gather**, the shape underneath `map`/`reduce` and the array operations in
scientific workflow systems.

The idea: a node takes a list and "scatters" it into indexed parcels — `user[0]`,
`user[1]`, `user[2]`. A downstream node declares `requires=["user"]` with *no
index*. The engine notices the indexed parcels and runs that node once per index,
passing the index in. Finally a "gather" node collects `processed[0..n]` back into a
single list.

The pedagogically interesting part is that the per-item node contains **no loop**.
It is written as if it processes a single item. The repetition is supplied by the
engine. This is precisely the abstraction that `map` and data-parallel frameworks
provide: you write the per-element function, the framework handles the iteration.

**An honest caveat, and why it matters.** Each per-item run is *independent* — item
3 does not depend on item 1 — so this is the logical structure that real systems
parallelize across cores or machines. ParcelFlow itself does **not** parallelize: it
runs the items sequentially, in index order, so the logs stay readable and
deterministic. It teaches the *shape* of data-parallel work, not the mechanics of
parallel execution. Conflating "this has the structure of a parallel map" with "this
runs in parallel" is a common and consequential error; keeping them separate is part
of the lesson. Turning the independent runs into actual concurrency is the capstone
exercise.

When a node requires *two* arrays, the engine uses a strict zip: it runs only for
indices present in both, like Python's `zip()` stopping at the shorter list. This is
a deliberate, predictable choice over the alternative (a Cartesian product), and a
good prompt for a design discussion: when would you want zip semantics, and when
would you want the cross product?

One honest seam is worth pointing students to: the gather step (`CollectNode`)
cannot be expressed by `requires`/`outputs` alone, because "wait until *all* of
`processed[0..n]` exist" depends on a count it only learns at runtime. It therefore
overrides `can_run` to inspect the metadata parcel. This is the single place a node
reaches beyond the clean declarative contract — a good discussion point about where a
minimal model's abstraction stops fitting and why real engines need richer readiness
rules.

---

## 6. Where this sits relative to real systems

ParcelFlow is a teaching model, not a tool you would deploy. It helps to know what
it is a model *of*:

- **Production orchestrators** such as Apache Airflow and Prefect run real DAGs with
  persistence, retries, distributed workers, and scheduling. They prioritise
  reliability and operability, which is exactly the complexity ParcelFlow strips
  away.
- **Scientific workflow systems** such as Nextflow, Swift/T, Snakemake, and Pegasus
  run large dataflow graphs across HPC clusters, with sophisticated scatter/gather
  and provenance. ParcelFlow's array spreading is a one-room model of their core
  idea.
- **Specifications** such as the Common Workflow Language (CWL) describe workflows
  portably without prescribing an engine.
- **Streaming and reactive systems** such as Apache Beam and reactive libraries like
  RxJS share the "react when data arrives" intuition, applied to unbounded data.

The point of the toy is to make the *idea* in all of these legible in an afternoon,
so that when you later open Airflow or Nextflow, the data-flow concept is already
familiar and only the operational machinery is new.

---

## 7. What to take away

- An execution order can be *derived from data dependencies* rather than written
  down. Declare what each step needs and produces, and the schedule follows.
- This buys you decoupling (nodes never reference each other) at the cost of a new
  failure mode (work that silently never runs), which a good teaching engine should
  surface.
- Scatter/gather lets you express per-item work without a loop; its independence is
  what real systems parallelize, even when a teaching engine runs it sequentially.
- Toy engines are valuable precisely because they are small enough to read whole.
  The exercises ask you to modify this one, which is the fastest way to confirm you
  actually understand it.

Continue with the notebooks: `01_concepts_walkthrough` to see the loop run,
`02_scatter_gather_lab` for the array pattern, and `03_student_lab` to modify the
engine yourself.
