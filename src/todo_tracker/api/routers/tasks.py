from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from todo_tracker.api.schemas.task import Task, TaskCreate, TaskUpdate
from todo_tracker.tasks import cli as task_cli
import sys
import io

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/add", status_code=status.HTTP_201_CREATED)
def add(title: str, description: Optional[str] = None):
    task_cli.add(title, description)
    # Fetch the latest task as confirmation
    tasks_json = task_cli.list(as_json=True)
    if tasks_json and tasks_json.get('tasks'):
        created_task = tasks_json['tasks'][-1]
        return {"task": created_task}
    return {"error": "Task could not be created"}

@router.get("/list")
def list():
    output = task_cli.list(as_json=True)
    return output

@router.put("/update")
def update(task_id: int, title: Optional[str] = None, description: Optional[str] = None, status_: Optional[str] = None):
    output = task_cli.update(task_id, title, description, status_, as_json=True)
    if output and output.get('error'):
        raise HTTPException(status_code=404, detail=output['error'])
    return output

@router.post("/finish")
def finish(task_id: int):
    output = task_cli.finish(task_id, as_json=True)
    if output and output.get('error'):
        raise HTTPException(status_code=404, detail=output['error'])
    return output

@router.delete("/delete", status_code=status.HTTP_200_OK)
def delete(task_id: int):
    output = task_cli.delete(task_id, as_json=True)
    if output and output.get('error'):
        raise HTTPException(status_code=404, detail=output['error'])
    return output
