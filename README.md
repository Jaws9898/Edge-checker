# Edge-checker

A Python tool for checking and validating edges in graphs and networks. Edge-checker helps you detect invalid connections, cycles, duplicate edges, and other structural issues in directed and undirected graphs.

## Features

- Validate edges in directed and undirected graphs
- Detect duplicate edges
- Detect self-loops
- Check for cycles (in directed graphs)
- Validate edge weights
- Support for adjacency list and edge list inputs

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from edge_checker import EdgeChecker

# Create a checker for an undirected graph
checker = EdgeChecker(directed=False)

# Add edges
checker.add_edge(1, 2)
checker.add_edge(2, 3)
checker.add_edge(3, 1)

# Run checks
results = checker.check()
print(results)
```

### Command-line Interface

```bash
python -m edge_checker --file graph.json
python -m edge_checker --edges "1,2 2,3 3,1" --directed
```

## Input Formats

### JSON
```json
{
  "directed": false,
  "edges": [
    {"from": 1, "to": 2},
    {"from": 2, "to": 3}
  ]
}
```

### CSV
```
from,to
1,2
2,3
3,1
```

## Running Tests

```bash
pytest tests/
```

## License

MIT
