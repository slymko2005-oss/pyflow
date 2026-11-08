import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from pyflow.models import Workflow
from pyflow.graph import topological_order

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class TaskExecutionError(Exception):
    """Wyjątek podnoszony, gdy zadanie zakończy się błędem wykonania."""
    def __init__(self, task_name: str, original_exception: Exception):
        super().__init__(f"Zadanie '{task_name}' zakończyło się błędem: {original_exception}")
        self.task_name = task_name
        self.original_exception = original_exception

@dataclass
class RunResult:
    outputs: Dict[str, Any] = field(default_factory=dict)
    task_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    succeeded: bool = True

def run(workflow: Workflow) -> RunResult:
    """Uruchamia workflow w sposób synchroniczny zgodnie z porządkiem topologicznym."""
    workflow.validate()
    execution_order = topological_order(workflow)
    
    outputs: Dict[str, Any] = {}
    task_states: Dict[str, Dict[str, Any]] = {}
    
    for task_name in workflow.tasks:
        task_states[task_name] = {
            "status": TaskStatus.PENDING,
            "time": 0.0
        }
        
    failed_tasks = set()
    skipped_tasks = set()
    workflow_succeeded = True

    for task_name in execution_order:
        task = workflow.tasks[task_name]
        
        has_invalid_dependency = any(dep in failed_tasks or dep in skipped_tasks for dep in task.dependencies)
        
        if has_invalid_dependency:
            task_states[task_name] = {
                "status": TaskStatus.SKIPPED,
                "time": 0.0
            }
            skipped_tasks.add(task_name)
            continue
            
        inputs = {dep: outputs[dep] for dep in task.dependencies}
        
        task_states[task_name]["status"] = TaskStatus.RUNNING
        start_time = time.perf_counter()
        
        try:
            result = task.function(inputs, task.params)
            elapsed = time.perf_counter() - start_time
            
            outputs[task_name] = result
            task_states[task_name] = {
                "status": TaskStatus.SUCCEEDED,
                "time": elapsed,
                "output": result
            }
        except Exception as exc:
            elapsed = time.perf_counter() - start_time
            task_states[task_name] = {
                "status": TaskStatus.FAILED,
                "time": elapsed,
                "error": exc
            }
            failed_tasks.add(task_name)
            workflow_succeeded = False
            
            raise TaskExecutionError(task_name, exc) from exc

    return RunResult(
        outputs=outputs,
        task_states=task_states,
        succeeded=workflow_succeeded
    )

