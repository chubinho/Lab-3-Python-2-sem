from typing import Iterable, Iterator, Optional
from src.task import Task


class TaskQueue:
    """Коллекция для хранения и ленивой фильтрации задач"""

    def __init__(self, tasks: Optional[list['Task']] = None) -> None:
        self._tasks = tasks if tasks is not None else []

    def __len__(self) -> int:
        return len(self._tasks)

    def __add__(self, task: 'Task') -> None:
        self._tasks.append(task)

    def __iter__(self) -> 'TaskQueueIterator':
        return TaskQueueIterator(self._tasks)

    def filter_by_status(self, status: str) -> Iterator['Task']:
        for task in self._tasks:
            if task.status == status:
                yield task

    def filter_by_priority(self, min_priority: int) -> Iterator['Task']:
        for task in self._tasks:
            if task.priority >= min_priority:
                yield task


class TaskQueueIterator:
    """Итератор для объода задач"""

    def __init__(self, tasks: list['Task']) -> None:
        self._tasks = tasks
        self._cursor = 0

    def __next__(self) -> 'Task':
        if self._cursor >= len(self._tasks):
            raise StopIteration("Длина массива закончилась")
        task = self._tasks[self._cursor]
        self._cursor += 1
        return task

    def __iter__(self) -> 'TaskQueueIterator':
        return self
