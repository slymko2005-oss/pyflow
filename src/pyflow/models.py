from dataclasses import dataclass, field
from typing import Callable, Mapping, Any, Set, Dict, Optional
import types

class WorkflowValidationError(Exception):
    pass

@dataclass(frozen=True)
class Task:
    name: str
    function: Callable[[Mapping[str, Any], Mapping[str, Any]], Any]
    dependencies: frozenset[str] = field(default_factory=frozenset)
    params: Mapping[str, Any] = field(default_factory=dict)
    description: Optional[str] = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Nazwa zadania nie może być pusta.")
        if self.name in self.dependencies:
            raise ValueError(f"Zadanie '{self.name}' nie może zależeć od samego siebie.")
        object.__setattr__(self, 'dependencies', frozenset(self.dependencies))
        object.__setattr__(self, 'params', types.MappingProxyType(dict(self.params)))

class Workflow:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    @property
    def tasks(self) -> Dict[str, Task]:
        return dict(self._tasks)

    def add_task(self, task: Task) -> None:
        if task.name in self._tasks:
            raise ValueError(f"Zadanie o nazwie '{task.name}' już istnieje w workflow.")
        self._tasks[task.name] = task

    def validate(self) -> None:
        for task in self._tasks.values():
            for dep in task.dependencies:
                if dep not in self._tasks:
                    raise WorkflowValidationError(
                        f"Zadanie '{task.name}' zależy od niezarejestrowanego zadania '{dep}'."
                    )
        visited = {}
        def dfs(node: str):
            visited[node] = 1
            task = self._tasks[node]
            for dep in sorted(task.dependencies):
                if visited.get(dep, 0) == 1:
                    raise WorkflowValidationError(f"Wykryto cykl z udziałem zadania '{dep}'.")
                if visited.get(dep, 0) == 0:
                    dfs(dep)
            visited[node] = 2

        for task_name in sorted(self._tasks.keys()):
            if visited.get(task_name, 0) == 0:
                dfs(task_name)
