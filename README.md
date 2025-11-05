# ParcelFlow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A **reference implementation** of a data-driven workflow execution engine. ParcelFlow demonstrates automatic array processing through pattern matching in a minimal, understandable codebase (547 LOC core).

**This is working, executable software designed for teaching and research**, not a production workflow orchestrator.

## Overview

ParcelFlow implements a **data-driven execution model** where:

- **Parcels** are immutable data units that flow through the system
- **Nodes** declare required data and execute when that data becomes available
- **Execution order emerges** from data dependencies, not predefined graphs
- **Array processing is automatic** through pattern matching—no explicit loops needed

This minimal implementation (547 LOC core) is designed for:
- **Teaching** - Understanding workflow execution by reading complete, working code
- **Research** - Experimenting with execution models using a modifiable baseline
- **Prototyping** - Testing workflow logic with real data before committing to production systems

**This is a reference implementation, not production infrastructure.** For production deployment, see the TypeScript version notes below.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/DarekDev/parcel-flow.git
cd parcel-flow

# No installation needed for reference implementation - pure Python 3.8+, no dependencies!

# Run example workflows
python main.py array    # Array spreading demo (recommended first run)
python main.py simple   # Linear chain
python main.py parallel # Parallel processing

# List all available workflows
python main.py --list

# Run with detailed execution logs
python main.py array --verbose
```

## Key Example: Array Spreading

The defining feature of ParcelFlow is **automatic array processing**:

```python
# Define nodes
nodes = [
    RequestNode("request"),
    ArraySpreadNode("spread", "request_data", "user"),
    ProcessItemNode("process", "user", "processed"),
    CollectNode("collect", "processed", "result", "user_meta"),
    ResponseNode("response", "result")
]

# Initial data with an array
initial_data = {"request_data": ["alice", "bob", "charlie"]}

# Execute
engine = WorkflowEngine()
result = engine.execute_workflow(nodes, initial_data)
```

**What happens:**
1. `ArraySpreadNode` creates indexed parcels: `user[0]`, `user[1]`, `user[2]`
2. `ProcessItemNode` (which declares `requires=["user"]`) automatically runs **3 times**—once per index
3. Each execution produces `processed[0]`, `processed[1]`, `processed[2]`
4. `CollectNode` reassembles results into an array
5. No explicit loops in any node code!

## Creating Custom Nodes

```python
from base_node import BaseNode

class MyProcessNode(BaseNode):
    def __init__(self):
        super().__init__(
            requires=["input_data"],  # What data this node needs
            outputs=["output_data"]   # What data this node produces
        )
    
    def run(self, parcels, index=None):
        # Get input data
        data = parcels["input_data"].value
        
        # Process it (your business logic here)
        result = data.upper()
        
        # Return output
        return {"output_data": result}
```

For array processing, the same node works with indexed data:

```python
def run(self, parcels, index):
    # When index is provided, get indexed parcel
    data = parcels[f"input_data[{index}]"].value
    result = data.upper()
    return {f"output_data[{index}]": result}
```

## Architecture

The system consists of four core components:

### 1. Parcel (`parcel.py`, 29 LOC)
Immutable data units with name, value, and timestamp. Indexed parcels enable array processing.

### 2. Base Node (`base_node.py`, 64 LOC)
Abstract base class for all workflow nodes. Nodes declare requirements and outputs.

### 3. Workflow Engine (`workflow_engine.py`, 210 LOC)
Reactive execution loop that:
- Checks which nodes can run based on available data
- Discovers indexed parcels matching generic requirements
- Executes nodes (potentially multiple times for arrays)
- Collects outputs and repeats until completion

### 4. Example Nodes (`nodes.py`, 244 LOC)
Concrete implementations demonstrating various patterns:
- `RequestNode` - Creates initial data
- `ValidateNode` - Validates data
- `TransformNode` - Transforms data
- `ArraySpreadNode` - Converts arrays to indexed parcels
- `ProcessItemNode` - Processes individual array items
- `CollectNode` - Reassembles indexed parcels into arrays
- `ResponseNode` - Creates final response

**Total: 547 lines of core code**

## Use Cases

ParcelFlow is designed for:

- **Teaching workflow concepts** - Entire system understandable in hours, not weeks
- **Rapid prototyping** - No infrastructure, no dependencies, only Python
- **SME workflows** - 10-100 item batches with dynamic data structures
- **API orchestration** - Processing API responses with variable structures
- **Research** - Experimenting with workflow execution models

**Not designed for:**
- Massive-scale distributed processing (thousands of nodes)
- Complex control flow (conditional branching, loops)
- Production systems requiring fault tolerance and monitoring (see TypeScript version)

## Examples

### Linear Chain
```
request → validate → transform → response
```
Demonstrates sequential data dependencies.

### Parallel Processing
```
request → [validate, log] → transform → response
```
Both `validate` and `log` run simultaneously when `request_data` is available.

### Array Spreading
```
request → array-spread → [process-item × N] → collect → response
```
`ProcessItemNode` runs N times automatically—no loops in code!

## Comparison with Other Systems

ParcelFlow occupies a specific niche in the workflow ecosystem:

### When to Use ParcelFlow

**Good fit:**
- Teaching workflow concepts (entire engine is 547 LOC—readable in one sitting)
- Rapid prototyping with 10-100 item arrays
- Research into workflow execution models (zero dependencies = easy to modify)
- Dynamic data structures unknown at design time
- Learning reactive programming patterns

**Not a good fit:**
- Production systems requiring monitoring, fault tolerance, distributed execution
- Workflows with thousands of concurrent tasks
- Complex control flow (nested conditionals, arbitrary loops)
- Workflows requiring external service integrations (use Airflow/Prefect)

### Comparison Table

| Aspect | ParcelFlow | Airflow | Nextflow | CWL |
|--------|-----------|---------|----------|-----|
| **Core Strength** | Simplicity & teaching | Production scale | Scientific HPC | Reproducibility |
| **Execution Model** | Data-driven | Explicit DAG | Dataflow | DAG + scatter |
| **Array Processing** | Pattern matching | Dynamic tasks | Channel ops | Scatter directive |
| **Reference Impl. LOC** | 547 | N/A (10K+) | N/A (20K+) | Specification |
| **External Dependencies** | None (Python) | Many | Many | Varies |
| **Typical Use Case** | Teaching, 10-100 items | Production, 1000s tasks | HPC pipelines | Science workflows |

**Note:** "None" for dependencies refers to the reference Python implementation only. The production TypeScript version requires Node.js, npm, and database infrastructure.

## Production Deployment

A production TypeScript implementation is deployed at Key Search AG (currently undergoing formal case study evaluation), handling 50-200 workflows daily. It adds:
- Async/await concurrent execution
- Supabase persistence
- React visual editor
- API webhooks

The TypeScript version maintains the same core semantics while adding production features. Case study results and source code publication are planned for 2025.

## Testing

```bash
# Run tests
python run_tests.py

# Run benchmarks
python benchmark_workflow.py
```

## Documentation

- **[Research Paper](research-paper/parcelflow-paper.tex)** - Formal description and evaluation

## Limitations

- **Single-threaded Python** - Reference implementation only, not for massive scale
- **In-memory state** - All parcels stored in memory during execution
- **Limited control flow** - No native conditional branching or arbitrary loops
- **Flat arrays only** - Nested structures require custom handling

See the [Limitations section](research-paper/parcelflow-paper.tex) in the paper for details.

## Contributing

Contributions welcome! Key priorities:
- Maintain simplicity and readability
- Add comprehensive tests
- Improve documentation
- Create additional example workflows

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Citation

If you use ParcelFlow in research, please cite:

```bibtex
@article{mlodnicki2024parcelflow,
  title={ParcelFlow: A Data-Driven Workflow Execution Engine with Declarative Array Processing},
  author={Młodnicki, Dariusz},
  journal={[Journal Name - pending publication]},
  year={2024},
  url={https://github.com/DarekDev/parcel-flow}
}
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contact

- **Author:** Dariusz Młodnicki
- **Email:** darek@mlodnicki.com.pl
- **Organization:** Key Search AG
- **Issues:** [GitHub Issues](https://github.com/DarekDev/parcel-flow/issues)

## Acknowledgements

Thanks to early adopters who provided feedback and validated the production deployment.
