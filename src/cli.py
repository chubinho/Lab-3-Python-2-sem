from pathlib import Path
from typing import Optional
import typer
import logging

from src.sources.file_source import FileSource
from src.sources.generator_source import GeneratorConfig, GeneratorSource
from src.sources.api_mock_source import APIMockSource
from src.consumer import TaskConsumer
from src.task_queue import TaskQueue, TaskQueueIterator
from src.logger import set_logger


logger = set_logger(logging.INFO)


app = typer.Typer(help="Платформа обработки задач")

@app.command()
def process(count: int = typer.Option(10, "--count", "-n", help="Сколько задач сгенерировать"), status: Optional[str] = typer.Option(None, "--status", help= "Фильтр по статусу"), priority: Optional[int] = typer.Option(None, "--priority", help="Мин приоритет")):
    consumer = TaskConsumer()
    source = GeneratorSource(GeneratorConfig(count=count))
    queue = TaskQueue()
    tasks = consumer.accept_tasks(source)
    for t in tasks: 
        queue + t
    typer.echo(f"Загружено в очередь {len(queue)} задач")
    result = queue
    if status:
        result = queue.filter_by_status(status)
    if priority:
        result = [t for t in result if t.priority >= priority]
    typer.echo(f"Результат фильтрации:")
    for task in result:
        typer.echo(f" Задача {task.id}, {task.priority},  {task.status}")    
@app.command()
def file(path: Path = typer.Argument(..., help="Путь к JSON-файлу")):
    """
    Получение задачи из файла
    """
    logger.info(f"Запуск команды file: path={path}")
    consumer = TaskConsumer()
    try:
        logger.debug(f"Создание FileSource для {path}")
        source = FileSource(path)
        tasks = consumer.accept_tasks(source)
        logger.info(f"FileSource: получено {len(tasks)} задач")
        typer.echo(f"FileSource: {len(tasks)} задач")
        for task in tasks:
            typer.echo(f" - {task.id}: {task.payload}")

    except FileNotFoundError as e:
        logger.error(f"Файл с путем - {path} не найден - {e}")
        typer.echo(f"Ошибка: Файл {e} не найден")
        raise typer.Exit(1)
    except TypeError as e:
        logger.error(f"Нарушение контракта - {e}")
        typer.echo(f"Нарушение контракта - {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        typer.echo(f"Ошибка: {e}")
        raise typer.Exit(1)


@app.command()
def generate(
        count: int = typer.Option(5, "--count", "-n", help="Кол-во задач"),
        prefix: str = typer.Option("task_", "--prefix", "-p", help="Префикс")):
    """
    Генерация задачи
    """
    consumer = TaskConsumer()
    logger.info(f"Запуск команды generate: count={count}, prefix={prefix}")
    try:
        logger.debug(
            f"Создание GeneratorConfig(count={count}, prefix={prefix})")
        config = GeneratorConfig(count=count, prefix=prefix)
        source = GeneratorSource(config)
        tasks = consumer.accept_tasks(source)
        logger.info(f"GeneratorSource: {len(tasks)} задач")
        typer.echo(f"GeneratorSource: {len(tasks)} задач")
        for task in tasks:
            typer.echo(f"  - {task.id}: {task.payload}")
    except ValueError as e:
        logger.error(f"Некорректные параметры: {e}")
        typer.echo(f"Ошибка: {e}")
        raise typer.Exit(1)
    except TypeError as e:
        logger.error(f"Нарушение контракта - {e}")
        typer.echo(f"Нарушение контракта - {e}")
        typer.Exit(1)
    except Exception as e:
        logger.error(f"Ошибка в generate - {e}")
        typer.echo(f"Ошибка: {e}")
        raise typer.Exit(1)


@app.command()
def api():
    """Получить задачи из API-заглушки."""
    consumer = TaskConsumer()
    logger.info("Запуск команды api")
    try:
        logger.debug("Cоздание APIMockSource")
        source = APIMockSource()
        tasks = consumer.accept_tasks(source)
        logger.info(f"APIMockSource: получено {len(tasks)} задач")
        typer.echo(f"APIMockSource: {len(tasks)} задач")
        for task in tasks:
            typer.echo(f"  - {task.id}: {task.payload}")
    except TypeError as e:
        logger.error(f"Нарушение контракта: {e}")
        typer.echo(f"Нарушение контракта: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Ошиибка в api: {e}")
        typer.echo(f"Ошибка: {e}")
        raise typer.Exit(1)


@app.command()
def all(
    file: Path = typer.Option("messages.json", "--file",
                              "-f", help="Путь к JSON-файлу"),
    count: int = typer.Option(
        3, "--count", "-n", help="Количество задач для генератора"),
):
    """Получить задачи из всех источников."""
    consumer = TaskConsumer()
    logger.info(f"Запуск команды all: file={file}, count={count}")
    try:
        logger.debug("Создание списка источников")
        sources = [
            FileSource(file),
            GeneratorSource(GeneratorConfig(count=count)),
            APIMockSource(),
        ]
        logger.info(f"Получение задач из {len(sources)} источников")
        all_tasks = consumer.accept_tasks_from_multiple_sources(sources)
        logger.info(f"Всего получено {len(all_tasks)} задач")
        typer.echo(f" Всего: {len(all_tasks)} задач из 3 источников")
        return 0
    except Exception as e:
        logger.exception(f"Ошибка в all: {e}")
        typer.echo(f"Ошибка: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
