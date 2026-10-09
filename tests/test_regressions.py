"""Independent regressions for input handling and deleted graph extremities."""
import gzip
from types import SimpleNamespace

import networkx as nx
import pytest

from .context import debruijn


@pytest.mark.parametrize("text", [
    "@r\nACG\n+\n", "r\nACG\n+\nIII\n",
    "@r\nACG\ninvalid\nIII\n", "@r\nACG\n+\nII\n",
])
def test_invalid_fastq_is_rejected(tmp_path, text):
    path = tmp_path / "reads.fq"
    path.write_text(text)
    with pytest.raises(ValueError, match="FASTQ"):
        list(debruijn.read_fastq(path))


def test_gzip_fastq_and_short_reads(tmp_path):
    path = tmp_path / "reads.fq.gz"
    with gzip.open(path, "wt") as handle:
        handle.write("@r\r\nACG\r\n+\r\nIII\r\n")
    assert list(debruijn.read_fastq(path)) == ["ACG"]
    assert list(debruijn.cut_kmer("ACG", 4)) == []
    with pytest.raises(ValueError, match="at least 2"):
        list(debruijn.cut_kmer("ACG", 1))


def test_two_entry_merges_do_not_reuse_deleted_sources():
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([
        ("AA", "AC", 10), ("TA", "AC", 1), ("AC", "CG", 10),
        ("GG", "GC", 10), ("TG", "GC", 1), ("GC", "CT", 10),
    ])
    graph = debruijn.solve_entry_tips(graph, debruijn.get_starting_nodes(graph))
    assert "TA" not in graph and "TG" not in graph
    assert set(debruijn.get_starting_nodes(graph)) == {"AA", "GG"}


def test_two_out_forks_do_not_reuse_deleted_sinks():
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([
        ("AA", "AC", 10), ("AC", "CG", 10), ("AC", "CT", 1),
        ("GG", "GC", 10), ("GC", "CA", 10), ("GC", "CC", 1),
    ])
    graph = debruijn.solve_out_tips(graph, debruijn.get_sink_nodes(graph))
    assert "CT" not in graph and "CC" not in graph
    assert set(debruijn.get_sink_nodes(graph)) == {"CG", "CA"}


def test_main_recomputes_extremities_before_contig_export(tmp_path, monkeypatch):
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([
        ("AA", "AC", 10), ("TA", "AC", 1), ("AC", "CG", 10),
        ("CG", "GT", 10), ("CG", "GA", 1),
    ])
    output = tmp_path / "contigs.fasta"
    args = SimpleNamespace(fastq_file=None, kmer_size=3,
                           output_file=output, graphimg_file=None)
    monkeypatch.setattr(debruijn, "get_arguments", lambda: args)
    monkeypatch.setattr(debruijn, "build_kmer_dict", lambda *_: {})
    monkeypatch.setattr(debruijn, "build_graph", lambda _: graph)
    debruijn.main()
    assert output.read_text() == ">contig_0 len=5\nAACGT\n"


def test_bubble_candidate_is_not_replaced_by_an_unrelated_later_node():
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([
        ("AA", "AC", 10), ("AC", "CG", 10),
        ("AA", "AT", 1), ("AT", "CG", 1),
        ("CG", "GT", 10), ("GT", "TT", 10),
    ])
    simplified = debruijn.simplify_bubbles(graph)
    assert "AT" not in simplified and "TT" in simplified
    assert nx.has_path(simplified, "AA", "TT")


def test_path_weight_does_not_include_shortcut_edges():
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([("A", "B", 10), ("B", "C", 10),
                                   ("A", "C", 100)])
    assert debruijn.path_average_weight(graph, ["A", "B", "C"]) == 10
    assert debruijn.select_best_path(graph, [["A", "C"]], [2], [100]) is graph
