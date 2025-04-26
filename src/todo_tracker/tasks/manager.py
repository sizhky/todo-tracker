import pandas as pd
from torch_snippets import P
from typing import List, Optional
from datetime import datetime

from .models import Task

class TaskManager:
    def __init__(self):
        self.todos_dir = P.home() / '.todos'
        self.todos_file = self.todos_dir / 'tasks.csv'
        self._ensure_todos_dir()
        
    def _load_df(self) -> pd.DataFrame:
        """Load the tasks DataFrame"""
        df = pd.read_csv(self.todos_file)
        # change nas in description column to blank string
        df['description'] = df['description'].fillna('')
        return df
    
    def _save_df(self, df: pd.DataFrame) -> None:
        """Save the tasks DataFrame"""
        df.to_csv(self.todos_file, index=False)

    def _ensure_todos_dir(self):
        """Ensure the todos directory and file exist"""
        self.todos_dir.mkdir(exist_ok=True)
        if not self.todos_file.exists():
            # Create empty DataFrame with columns
            df = pd.DataFrame(columns=['id', 'title', 'description', 'status', 'created_at', 'updated_at'])
            self._save_df(df)

    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        """Create a new task"""
        df = self._load_df()
        
        # Generate new task ID
        task_id = 1 if len(df) == 0 else df['id'].max() + 1
        
        # Create task using Pydantic model
        task = Task(id=task_id, title=title, description=description)
        
        # Convert to dict for DataFrame and save
        task_dict = task.model_dump()
        task_dict['created_at'] = task.created_at.isoformat()
        task_dict['updated_at'] = task.updated_at.isoformat()
        
        df = pd.concat([df, pd.DataFrame([task_dict])], ignore_index=True)
        self._save_df(df)
        
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a single task by ID"""
        df = self._load_df()
        task_row = df[df['id'] == task_id]
        if len(task_row) == 0:
            return None
        return Task.model_validate(task_row.to_dict('records')[0])

    def update_task(self, task_id: int, **updates) -> Optional[Task]:
        """Update a task by ID with the given field updates"""
        df = self._load_df()
        task_idx = df[df['id'] == task_id].index
        
        if len(task_idx) == 0:
            return None
            
        # Get existing task and update it
        task_dict = df.loc[task_idx[0]].to_dict()
        task_dict.update(updates)
        task_dict['updated_at'] = datetime.now().isoformat()
        
        # Validate updates through Pydantic
        updated_task = Task.model_validate(task_dict)
        
        # Update DataFrame
        for key, value in updated_task.model_dump().items():
            df.loc[task_idx[0], key] = value
            
        self._save_df(df)
        return updated_task

    def finish_task(self, task_id: int) -> Optional[Task]:
        """Mark a task as completed"""
        return self.update_task(task_id, status='completed')

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID"""
        df = self._load_df()
        task_idx = df[df['id'] == task_id].index
        
        if len(task_idx) == 0:
            return False
            
        df = df.drop(task_idx)
        self._save_df(df)
        return True

    def list_tasks(self) -> List[Task]:
        """List all tasks"""
        df = self._load_df()
        return [Task.model_validate(row) for row in df.to_dict('records')]
