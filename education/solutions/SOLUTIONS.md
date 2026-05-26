# Worked Solutions

Instructor reference. These are the intended answers to the notebook exercises.
Keep this file away from students until after they attempt the work.

All solutions have been checked against the test cells in the notebooks.

## Module 3, Exercise 1 — SplitterNode

```python
class SplitterNode(BaseNode):
    def __init__(self):
        super().__init__('splitter', requires=['sentence'], outputs=['words'])

    def run(self, parcels, index=None):
        sentence = parcels['sentence'].value
        return {'words': sentence.split(' ')}
```

*Discussion:* the node becomes ready as soon as a `sentence` parcel exists. It is
written for a single sentence; the engine would run it once per index if `sentence`
were itself spread into `sentence[0]`, `sentence[1]`, ...

## Module 3, Exercise 2 — fixing the deadlock

`BadNode` requires `step_one`, but `StartNode` produces `step1`. Change the requires
list to match the parcel that is actually produced:

```python
class BadNode(BaseNode):
    def __init__(self):
        super().__init__('bad', requires=['step1'], outputs=['final'])  # was ['step_one']
    def run(self, parcels, index=None):
        return {'final': 'success'}
```

*Discussion:* a data-flow engine does not raise an error for a missing dependency —
the node simply never becomes ready, so the work silently never happens. ParcelFlow
surfaces this with its end-of-run `DEADLOCK: ...` report, which names the parcel the
node was waiting for.

## Module 3, Exercise 3 (capstone) — concurrent per-item processing

```python
from concurrent.futures import ThreadPoolExecutor

def process_concurrently(items):
    with ThreadPoolExecutor(max_workers=len(items)) as executor:
        return list(executor.map(slow_process, items))
```

*Discussion:* `executor.map` preserves input order, so the result equals the
sequential list. The speedup is possible because each per-item call is independent —
no item's result depends on another's. That independence is the property that makes
concurrency safe here, and it is exactly the structure the scatter step produces.
The engine itself remains sequential; this exercise parallelizes the *work*, not the
engine.

## Module 2 — DoublerNode

```python
class DoublerNode(BaseNode):
    def __init__(self):
        super().__init__('doubler', requires=['num'], outputs=['doubled'])

    def run(self, parcels, index=None):
        value = parcels[f'num[{index}]'].value
        return {f'doubled[{index}]': value * 2}
```

*Discussion:* the node reads only its own index and writes only its own index. The
engine runs it once per matched index. The student should notice there is no loop in
the node — the repetition comes from the engine seeing `num[0]`, `num[1]`, `num[2]`.
