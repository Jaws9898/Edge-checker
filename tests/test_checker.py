import pytest
from edge_checker import EdgeChecker, Edge, CheckResult


class TestEdgeChecker:
    def test_valid_directed_graph(self):
        checker = EdgeChecker(directed=True)
        checker.add_edge(1, 2)
        checker.add_edge(2, 3)
        checker.add_edge(3, 4)
        result = checker.check()
        assert result.valid
        assert result.errors == []

    def test_valid_undirected_graph(self):
        checker = EdgeChecker(directed=False)
        checker.add_edge("A", "B")
        checker.add_edge("B", "C")
        result = checker.check()
        assert result.valid

    def test_self_loop_raises_error_by_default(self):
        checker = EdgeChecker()
        checker.add_edge(1, 1)
        result = checker.check()
        assert not result.valid
        assert any("self-loop" in e.lower() for e in result.errors)

    def test_self_loop_allowed_when_configured(self):
        checker = EdgeChecker(allow_self_loops=True)
        checker.add_edge(1, 1)
        result = checker.check()
        assert result.valid
        assert any("self-loop" in w.lower() for w in result.warnings)

    def test_duplicate_directed_edge(self):
        checker = EdgeChecker(directed=True)
        checker.add_edge(1, 2)
        checker.add_edge(1, 2)
        result = checker.check()
        assert not result.valid
        assert any("duplicate" in e.lower() for e in result.errors)

    def test_duplicate_undirected_edge_reverse(self):
        checker = EdgeChecker(directed=False)
        checker.add_edge(1, 2)
        checker.add_edge(2, 1)
        result = checker.check()
        assert not result.valid
        assert any("duplicate" in e.lower() for e in result.errors)

    def test_cycle_detected_as_warning(self):
        checker = EdgeChecker(directed=True)
        checker.add_edge(1, 2)
        checker.add_edge(2, 3)
        checker.add_edge(3, 1)
        result = checker.check()
        assert result.valid  # cycles are warnings, not errors
        assert any("cycle" in w.lower() for w in result.warnings)

    def test_no_cycle_in_dag(self):
        checker = EdgeChecker(directed=True)
        checker.add_edge(1, 2)
        checker.add_edge(1, 3)
        checker.add_edge(2, 4)
        checker.add_edge(3, 4)
        result = checker.check()
        assert result.valid
        assert not any("cycle" in w.lower() for w in result.warnings)

    def test_from_edge_list(self):
        checker = EdgeChecker.from_edge_list([(1, 2), (2, 3)], directed=True)
        assert len(checker.edges) == 2
        result = checker.check()
        assert result.valid

    def test_from_edge_list_with_weights(self):
        checker = EdgeChecker.from_edge_list([(1, 2, 0.5), (2, 3, 1.0)])
        edges = checker.edges
        assert edges[0].weight == 0.5
        assert edges[1].weight == 1.0

    def test_from_dict(self):
        data = {
            "directed": False,
            "edges": [
                {"from": "A", "to": "B"},
                {"from": "B", "to": "C"},
            ],
        }
        checker = EdgeChecker.from_dict(data)
        assert not checker.directed
        assert len(checker.edges) == 2
        result = checker.check()
        assert result.valid

    def test_from_dict_with_weights(self):
        data = {
            "directed": True,
            "edges": [{"from": 1, "to": 2, "weight": 3.5}],
        }
        checker = EdgeChecker.from_dict(data)
        assert checker.edges[0].weight == 3.5

    def test_add_edges_invalid_tuple(self):
        checker = EdgeChecker()
        with pytest.raises(ValueError):
            checker.add_edges([(1, 2, 3, 4)])

    def test_clear(self):
        checker = EdgeChecker()
        checker.add_edge(1, 2)
        checker.clear()
        assert checker.edges == []

    def test_check_result_bool(self):
        result = CheckResult(valid=True)
        assert bool(result) is True
        result = CheckResult(valid=False)
        assert bool(result) is False

    def test_check_result_summary_valid(self):
        result = CheckResult(valid=True)
        assert "VALID" in result.summary()

    def test_check_result_summary_with_errors(self):
        result = CheckResult(valid=False, errors=["Duplicate edge: 1 -> 2"])
        summary = result.summary()
        assert "INVALID" in summary
        assert "Duplicate edge" in summary


class TestEdgeModel:
    def test_edge_equality(self):
        e1 = Edge(1, 2)
        e2 = Edge(1, 2)
        e3 = Edge(2, 1)
        assert e1 == e2
        assert e1 != e3

    def test_edge_hashable(self):
        edges = {Edge(1, 2), Edge(1, 2), Edge(2, 3)}
        assert len(edges) == 2

    def test_edge_repr_with_weight(self):
        e = Edge(1, 2, weight=0.5)
        assert "weight=0.5" in repr(e)

    def test_edge_repr_without_weight(self):
        e = Edge(1, 2)
        assert "weight" not in repr(e)
