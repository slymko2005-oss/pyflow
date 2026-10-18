import pytest
from pyflow.models import Task, Workflow
from pyflow.graph import topological_order, execution_layers

def dummy_fn(inputs, params):
    return None

def test_empty_graph():
    wf = Workflow()
    assert topological_order(wf) == []
    assert execution_layers(wf) == []

def test_single_node():
    wf = Workflow()
    wf.add_task(Task(name="A", function=dummy_fn))
    assert topological_order(wf) == ["A"]
    assert execution_layers(wf) == [["A"]]

def test_chain():
    wf = Workflow()
    wf.add_task(Task(name="A", function=dummy_fn))
    wf.add_task(Task(name="B", function=dummy_fn, dependencies=frozenset(["A"])))
    wf.add_task(Task(name="C", function=dummy_fn, dependencies=frozenset(["B"])))
    assert topological_order(wf) == ["A", "B", "C"]
    assert execution_layers(wf) == [["A"], ["B"], ["C"]]

def test_execution_layers_spec_example():
    wf = Workflow()
    wf.add_task(Task(name="extract", function=dummy_fn))
    wf.add_task(Task(name="clean_a", function=dummy_fn, dependencies=frozenset(["extract"])))
    wf.add_task(Task(name="clean_b", function=dummy_fn, dependencies=frozenset(["extract"])))
    wf.add_task(Task(name="report", function=dummy_fn, dependencies=frozenset(["clean_a", "clean_b"])))

    layers = execution_layers(wf)
    assert layers == [["extract"], ["clean_a", "clean_b"], ["report"]]

def test_determinism():
    wf = Workflow()
    wf.add_task(Task(name="B", function=dummy_fn))
    wf.add_task(Task(name="A", function=dummy_fn))
    assert topological_order(wf) == ["A", "B"]
