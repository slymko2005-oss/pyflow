import pytest
from pyflow import Task, Workflow, run, TaskStatus, TaskExecutionError

def test_successful_workflow():
    def task_a(inputs, params):
        return params["value"] * 2

    def task_b(inputs, params):
        return inputs["a"] + 10

    wf = Workflow()
    wf.add_task(Task(name="a", function=task_a, params={"value": 5}))
    wf.add_task(Task(name="b", function=task_b, dependencies=frozenset(["a"])))

    result = run(wf)
    assert result.succeeded is True
    assert result.outputs["a"] == 10
    assert result.outputs["b"] == 20
    assert result.task_states["a"]["status"] == TaskStatus.SUCCEEDED
    assert result.task_states["b"]["status"] == TaskStatus.SUCCEEDED

def test_task_failure_and_skip():
    def failing_task(inputs, params):
        raise ValueError("Błąd krytyczny")

    def dependent_task(inputs, params):
        return 42

    wf = Workflow()
    wf.add_task(Task(name="fail", function=failing_task))
    wf.add_task(Task(name="next", function=dependent_task, dependencies=frozenset(["fail"])))

    with pytest.raises(TaskExecutionError) as exc_info:
        run(wf)
    
    assert exc_info.value.task_name == "fail"
    assert isinstance(exc_info.value.original_exception, ValueError)

