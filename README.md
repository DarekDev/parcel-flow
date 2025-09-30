# ParcelFlow - Minimal Example

A didactic demonstration of **ParcelFlow**, a parcel-based reactive workflow execution paradigm that enables natural parallelism without complex orchestration.

## 🎯 Core Concept

Instead of static node connections and predefined execution order, this system uses **reactive data flow**:

- **Parcels** = data with names that flow through the system
- **Nodes** = functions that run when their required data becomes available  
- **Engine** = loop that runs nodes when data is available
- **No static loops** - parallelism emerges naturally from data availability

## 🚀 Quick Start

```bash
# Run all example workflows
python main.py all

# Run specific workflows
python main.py simple    # Linear chain
python main.py parallel  # Parallel processing
python main.py array     # Array spreading (key demo)

# List available workflows
python main.py --list

# Verbose output
python main.py array --verbose
```

## 📚 Example Workflows

### 1. Simple Linear Chain
```
request → validate → transform → response
```
**Demonstrates:** Basic parcel flow and node dependencies

### 2. Parallel Processing  
```
request → [validate, log] → transform → response
```
**Demonstrates:** Multiple nodes running independently when data is available

### 3. Array Spreading (The Key Demo)
```
request → array-spread → [process-item] → collect → response
```
**Demonstrates:** The core paradigm - array spreading creates parallel work

## 🔧 Architecture

### Core Components

- **`parcel.py`** - Fundamental data unit
- **`base_node.py`** - Abstract base class for all nodes
- **`workflow_engine.py`** - Execution engine
- **`nodes.py`** - Example node implementations
- **`workflows.py`** - Workflow definitions
- **`main.py`** - Command-line interface

### Key Insight

The **ArraySpreadingNode** takes an array and creates indexed parcels:
```
Input: ["alice", "bob", "charlie"]
Output: user[0], user[1], user[2]
```

Then **ProcessItemNode** runs **multiple times** - once for each parcel - without any explicit loops or coordination. This is the essence of reactive data flow!

## 🎓 Educational Value

This example clearly shows:

1. **Data-driven execution** - nodes run when data is available
2. **Natural parallelism** - no complex orchestration needed
3. **Reactive programming** - no static control flow
4. **Scalable processing** - arrays become parallel work automatically

Perfect for understanding the paradigm before implementing in larger systems!

## 📖 About

This minimal implementation (~500 lines of Python) demonstrates the core concepts of ParcelFlow:
- Reactive, data-driven execution
- Natural parallelism through array spreading
- No static connections between nodes

For more information, see our research paper (citation coming soon).

## 📝 License

MIT License - feel free to use this code for learning, research, or commercial projects.

## 🤝 Contributing

Contributions welcome! This is an educational example, so clarity and simplicity are priorities.
