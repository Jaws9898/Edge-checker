import argparse
import json
import sys

from .checker import EdgeChecker


def parse_edges_string(edges_str: str):
    edges = []
    for pair in edges_str.split():
        parts = pair.split(",")
        if len(parts) == 2:
            edges.append((parts[0].strip(), parts[1].strip()))
        elif len(parts) == 3:
            edges.append((parts[0].strip(), parts[1].strip(), float(parts[2].strip())))
        else:
            print(f"Warning: skipping malformed edge '{pair}'", file=sys.stderr)
    return edges


def main():
    parser = argparse.ArgumentParser(
        description="Check edges in a graph for validity."
    )
    parser.add_argument("--file", help="JSON file describing the graph")
    parser.add_argument("--edges", help="Edges as 'src,dst' pairs separated by spaces")
    parser.add_argument(
        "--directed", action="store_true", default=True, help="Treat graph as directed"
    )
    parser.add_argument(
        "--undirected", action="store_true", help="Treat graph as undirected"
    )
    parser.add_argument(
        "--allow-self-loops", action="store_true", help="Allow self-loop edges"
    )
    args = parser.parse_args()

    directed = not args.undirected

    if args.file:
        with open(args.file) as f:
            data = json.load(f)
        checker = EdgeChecker.from_dict(data)
    elif args.edges:
        edges = parse_edges_string(args.edges)
        checker = EdgeChecker.from_edge_list(
            edges, directed=directed, allow_self_loops=args.allow_self_loops
        )
    else:
        parser.print_help()
        sys.exit(1)

    result = checker.check()
    print(result.summary())
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
