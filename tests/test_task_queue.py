import pytest
from src.task import Task
from src.task_queue import TaskQueue


@pytest.fixture
def sample_tasks():
    """
    Фикстура с набором задач, соответствующая __init__.
    Конструктор Task принимает (id: int, payload: dict).
    """
    return [
        Task(1, {"status": "new", "priority": 1, "description": "Task 1"}),
        Task(2, {"status": "done", "priority": 5, "description": "Task 2"}),
        Task(3, {"status": "new", "priority": 3, "description": "Task 3"})
    ]


def test_queue_length(sample_tasks):
    """Проверка метода __len__."""
    queue = TaskQueue(sample_tasks)
    assert len(queue) == 3


def test_iteration_protocol():
    """Проверка корректной работы StopIteration."""
    task = Task(1, {"status": "new", "priority": 1, "description": "Test"})
    queue = TaskQueue([task])
    it = iter(queue)
    next(it)
    with pytest.raises(StopIteration):
        next(it)


def test_repeatable_iteration(sample_tasks):
    """Проверка возможности повторного обхода"""
    queue = TaskQueue(sample_tasks)
    assert len(list(queue)) == len(list(queue)) == 3


def test_lazy_filter_status(sample_tasks):
    """Проверка ленивой фильтрации по статусу"""
    queue = TaskQueue(sample_tasks)
    new_tasks = list(queue.filter_by_status("new"))
    assert len(new_tasks) == 2
    for t in new_tasks:
        assert t.status == "new"


def test_lazy_filter_priority(sample_tasks):
    """Проверка фильтрации по приоритету"""
    queue = TaskQueue(sample_tasks)
    high_priority = list(queue.filter_by_priority(3))
    assert len(high_priority) == 2 


def test_generator_is_lazy(sample_tasks):
    """Проверка, что фильтр возвращает генератор (ленивость)"""
    queue = TaskQueue(sample_tasks)
    gen = queue.filter_by_status("new")
    assert hasattr(gen, "__next__")
    assert not isinstance(gen, list)
