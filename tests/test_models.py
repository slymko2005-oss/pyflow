import pytest
from pyflow.models import Task, Workflow, WorkflowValidationError

def dummy_fn(inputs, params):
    return None

def test_task_creation_valid():
    task = Task(name="t1", function=dummy_fn, dependencies=frozenset(["dep"]), params={"a": 1})
    assert task.name == "t1"
    assert "dep" in task.dependencies

def test_task_empty_name():
    with pytest.raises(ValueError):
        Task(name="", function=dummy_fn)

def test_task_self_dependency():
    with pytest.raises(ValueError):
        Task(name="t1", function=dummy_fn, dependencies=frozenset(["t1"]))

def test_workflow_duplicate_task():
    wf = Workflow()
    t1 = Task(name="t1", function=dummy_fn)
    wf.add_task(t1)
    with pytest.raises(ValueError):
        wf.add_task(t1)

def test_workflow_missing_dependency():
    wf = Workflow()
    t1 = Task(name="t1", function=dummy_fn, dependencies=frozenset(["missing"]))
    wf.add_task(t1)
    with pytest.raises(WorkflowValidationError):
        wf.validate()

def test_workflow_cycle_detection():
    wf = Workflow()
    t1 = Task(name="t1", function=dummy_fn, dependencies=frozenset(["t2"]))
    t2 = Task(name="t2", function=dummy_fn, dependencies=frozenset(["t1"]))
    wf.add_task(t1)
    wf.add_task(t2)
    with pytest.raises(WorkflowValidationError):
        wf.validate()
