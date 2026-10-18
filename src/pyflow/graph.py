from typing import List
from pyflow.models import Workflow, WorkflowValidationError

def topological_order(workflow: Workflow) -> List[str]:
    workflow.validate()
    tasks = workflow.tasks

    in_degree = {name: 0 for name in tasks}
    graph = {name: [] for name in tasks}

    for name, task in tasks.items():
        for dep in task.dependencies:
            graph[dep].append(name)
            in_degree[name] += 1

    ready = [name for name, degree in in_degree.items() if degree == 0]
    ready.sort()

    result = []
    while ready:
        node = ready.pop(0)
        result.append(node)

        for neighbor in sorted(graph[node]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                ready.append(neighbor)
                ready.sort()

    return result


def execution_layers(workflow: Workflow) -> List[List[str]]:
    workflow.validate()
    tasks = workflow.tasks

    in_degree = {name: 0 for name in tasks}
    graph = {name: [] for name in tasks}

    for name, task in tasks.items():
        for dep in task.dependencies:
            graph[dep].append(name)
            in_degree[name] += 1

    current_layer = [name for name, degree in in_degree.items() if degree == 0]
    current_layer.sort()

    layers = []
    while current_layer:
        layers.append(current_layer)
        next_layer = []

        for node in current_layer:
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_layer.append(neighbor)

        next_layer.sort()
        current_layer = next_layer

    return layers
