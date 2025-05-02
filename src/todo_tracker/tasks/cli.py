from typing import Optional
from typer import Typer

from .manager import TaskManager

cli = Typer()
task_manager = TaskManager()

@cli.command()
def add(title: str, description: Optional[str] = None):
    """Add a new task"""
    task = task_manager.create_task(title, description)
    print(f"Created task {task.id}: {task.title}")

@cli.command()
def list(from_mcp: bool = False):
    """List all tasks"""
    tasks = task_manager.list_tasks()
    if not tasks:
        print("No tasks found")
        return
    if from_mcp:
        json = {'tasks': [task.to_dict() for task in tasks]}
        return json
        
    for task in tasks:
        task.render()

@cli.command()
def update(task_id: int, title: Optional[str] = None, description: Optional[str] = None, status: Optional[str] = None):
    """Update a task"""
    updates = {}
    if title is not None:
        updates['title'] = title
    if description is not None:
        updates['description'] = description
    if status is not None:
        updates['status'] = status
        
    task = task_manager.update_task(task_id, **updates)
    if task:
        print(f"Updated task {task.id}")
        print(f"Title: {task.title}")
        print(f"Description: {task.description}")
        print(f"Status: {task.status}")
    else:
        print(f"Task {task_id} not found")

@cli.command()
def finish(task_id: int):
    """Mark a task as completed"""
    task = task_manager.finish_task(task_id)
    if task:
        print(f"Marked task {task.id} as completed")
        print(f"Title: {task.title}")
    else:
        print(f"Task {task_id} not found")

@cli.command()
def delete(task_id: int):
    """Delete a task"""
    if task_manager.delete_task(task_id):
        print(f"Deleted task {task_id}")
    else:
        print(f"Task {task_id} not found")
