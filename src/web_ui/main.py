from fasthtml.common import *
from todo_tracker.tasks.manager import TaskManager, Task

@patch
def __ft__(self: Task):
    info = f'{self.title} - {self.description}' if self.description else self.title
    return Li(P(info))

task_manager = TaskManager()

app,rt = fast_app()

def Tasks():
    tasks = task_manager.list_tasks()
    return Ul(
        *[task for task in tasks],
    )

@rt('/')
def get():
    return Titled("Hello", Div("Tasks", Tasks()))

serve()
