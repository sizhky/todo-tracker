# Project Readiness Document

This document outlines the necessary code modifications to implement the requested features from the "brainstorm" project. It provides a detailed analysis of required changes and potential implementations.

## Table of Contents
1. [Active Projects and Areas](#1-active-projects-and-areas)
2. [Add Subtasks for a Task](#2-add-subtasks-for-a-task)
3. [Redis DB Migration](#3-redis-db-migration)
3. [Redis DB Migration](#3-redis-db-migration)

## 1. Active Projects and Areas

**Task Description:** Have a provision to archive projects and areas as done and show only active ones that are currently happening. This should be a derived field where no task should be zero (i.e., there is at least one pending task).

### Required Changes

#### 1.1. Data Model Modifications

1. **Area Model:**
   - Add an `is_active` virtual property to the `Area` class that determines if an area is active based on its projects.
   - Modify `AreaRead` schema to include this virtual property.

```python
# src/td/models/area.py
class Area(SQLModel, table=True):
    # Existing fields...
    
    @property
    def is_active(self) -> bool:
        """Determine if area is active based on having at least one active project."""
        return any(project.is_active for project in self.projects)

class AreaRead(SQLModel):
    # Existing fields...
    is_active: bool = True
```

2. **Project Model:**
   - Add an `is_active` virtual property to the `Project` class that determines if a project is active based on its tasks.
   - Modify `ProjectRead` schema to include this virtual property.

```python
# src/td/models/project.py
class Project(SQLModel, table=True):
    # Existing fields...
    
    @property
    def is_active(self) -> bool:
        """Determine if project is active based on having at least one pending task."""
        return any(not task.status for task in self.tasks)  # False = pending

class ProjectRead(SQLModel):
    # Existing fields...
    is_active: bool = True
```

#### 1.2. CRUD Operations Modifications

1. **Project CRUD:**
   - Update `get_all_projects_from_db` function to optionally filter for active projects only.

```python
# src/td/crud/project.py
def get_all_projects_from_db(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = False
) -> List[Project]:
    """
    Retrieve all projects from the database with optional pagination and filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, returns only projects with at least one pending task
    """
    # The base query
    statement = select(Project).offset(skip).limit(limit)
    
    if active_only:
        # We need to join with tasks to filter by task status
        statement = (
            select(Project)
            .join(Task, isouter=True)
            .group_by(Project.id)
            .having(
                # Either has at least one pending task or no tasks at all
                or_(
                    func.bool_or(Task.status == False).is_(True),
                    func.count(Task.id) == 0
                )
            )
            .offset(skip)
            .limit(limit)
        )
    
    return db.exec(statement).all()
```

2. **Area CRUD:**
   - Update `get_all_areas_from_db` function to optionally filter for active areas only.

```python
# src/td/crud/area.py
def get_all_areas_from_db(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = False
) -> List[Area]:
    """
    Retrieve all areas from the database with optional pagination and filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, returns only areas with at least one active project
    """
    # The base query
    statement = select(Area).offset(skip).limit(limit)
    
    if active_only:
        # This is complex as we need to check if any project has pending tasks
        # A simpler approach would be to fetch all areas and then filter in Python
        # But for efficiency, we can use a subquery
        active_projects = (
            select(Project.area_id)
            .join(Task, isouter=True)
            .where(Task.status == False)
            .group_by(Project.area_id)
        )
        
        statement = (
            select(Area)
            .where(Area.id.in_(active_projects))
            .offset(skip)
            .limit(limit)
        )
    
    return db.exec(statement).all()
```

#### 1.3. CLI Interface Modifications

1. **Project CLI:**
   - Update `list_projects` command to accept an `active_only` parameter.

```python
# src/td/cli/project.py

@cli.command(name="pl")
def list_projects(
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = Option(False, "--active-only", "-a", help="List only active projects")
):
    """
    List all projects in the database with optional pagination.
    
    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        active_only: If True, only show projects with at least one pending task.
    """
    with session_scope() as session:
        projects = get_all_projects_from_db(session, skip=skip, limit=limit, active_only=active_only)
        # Existing code continues...
```

2. **Area CLI:**
   - Similarly update `list_areas` command to accept an `active_only` parameter.

```python
# src/td/cli/area.py

@cli.command(name="al")
def list_areas(
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = Option(False, "--active-only", "-a", help="List only active areas")
):
    """List all areas in the database with optional pagination."""
    with session_scope() as session:
        areas = get_all_areas_from_db(session, skip=skip, limit=limit, active_only=active_only)
        # Existing code continues...
```

### Implementation Strategy

1. Start by modifying the data models to add the `is_active` virtual properties.
2. Update the CRUD operations to support filtering by active status.
3. Modify the CLI commands to expose the active-only filtering option.
4. Update API endpoints to support filtering by active status.
5. Write tests to verify the functionality.
6. Update documentation.

## 2. Add Subtasks for a Task

**Task Description:** Allow tasks to have subtasks, creating a hierarchical task structure.

### Required Changes

#### 2.1. Data Model Modifications

1. **Task Model:**
   - Add a `parent_id` field to enable a hierarchical structure.
   - Add a `subtasks` relationship to allow easy access to child tasks.
   - Update virtual properties to consider subtask status.

```python
# src/td/models/task.py
class TaskBase(SQLModel):
    # Existing fields...
    parent_id: Optional[int] = Field(default=None, foreign_key="task.id", index=True)

class Task(TaskBase, table=True):
    # Existing fields...
    parent: Optional["Task"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "Task.id", 
            "primaryjoin": "Task.parent_id == Task.id"
        }
    )
    subtasks: List["Task"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete", "backref": "parent"}
    )
    
    @property
    def is_complete(self) -> bool:
        """Task is complete if its status is True and all subtasks are complete."""
        return self.status and all(subtask.is_complete for subtask in self.subtasks)
    
    @property
    def has_pending_subtasks(self) -> bool:
        """Check if task has any pending subtasks."""
        return any(not subtask.is_complete for subtask in self.subtasks)

class TaskRead(TaskBase):
    # Existing fields...
    parent_id: Optional[int] = None
    subtasks: List["TaskRead"] = []
    has_subtasks: bool = False
    pending_subtasks_count: int = 0
```

#### 2.2. CRUD Operations Modifications

1. **Task CRUD:**
   - Update the `create_task_in_db` function to support creating subtasks.
   - Update the `get_task_by_id` function to optionally include subtasks.
   - Update `get_all_tasks_from_db` to support hierarchical querying.

```python
# src/td/crud/task.py
def create_task_in_db(db: Session, task: TaskCreate) -> Task:
    """
    Create a new task in the database.
    
    Args:
        db: Database session
        task: Task details including optional parent_id for subtasks
    """
    db_task = Task.model_validate(task)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task_by_id(db: Session, task_id: int, include_subtasks: bool = False) -> Optional[Task]:
    """
    Get a specific task by ID with optional subtasks loading.
    
    Args:
        db: Database session
        task_id: ID of the task to retrieve
        include_subtasks: If True, eagerly load subtasks
    """
    query = select(Task).where(Task.id == task_id)
    
    if include_subtasks:
        query = query.options(joinedload(Task.subtasks))
        
    return db.exec(query).first()

def get_all_tasks_from_db(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    pending_only: bool = False,
    as_hierarchy: bool = False,
    root_level_only: bool = False,
) -> List[TaskRead]:
    """
    Retrieve all tasks from the database with optional pagination and filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        pending_only: If True, only return pending tasks
        as_hierarchy: If True, include relationships for hierarchical display
        root_level_only: If True, only return top-level tasks (no parent)
    """
    query_options = []
    if as_hierarchy:
        query_options.append(joinedload(Task.project).joinedload(Project.area))
        query_options.append(joinedload(Task.subtasks))

    statement = select(Task).options(*query_options).offset(skip).limit(limit)

    if pending_only:
        statement = statement.where(Task.status == False)  # noqa

    if root_level_only:
        statement = statement.where(Task.parent_id == None)  # noqa

    db_tasks = db.exec(statement).all()
    
    # Process tasks as before with time calculation
    tasks_with_time = []
    for db_task in db_tasks:
        total_time = calculate_total_time_for_task(db, db_task.id)
        task_read = TaskRead.model_validate(db_task)
        task_read.total_time_seconds = total_time
        
        # Add subtasks info for the task
        if hasattr(db_task, 'subtasks'):
            task_read.has_subtasks = len(db_task.subtasks) > 0
            task_read.pending_subtasks_count = len([s for s in db_task.subtasks if not s.status])
            
        tasks_with_time.append(task_read)

    return tasks_with_time
```

#### 2.3. CLI Interface Modifications

1. **Task CLI:**
   - Update the `create_task` command to support specifying a parent task.
   - Add options to list tasks with their subtasks or only root-level tasks.

```python
# src/td/cli/task.py
@cli.command(name="tc")
def create_task(
    title: str,
    project: Annotated[
        str | None,
        Option(
            "-p",
            help="Name of the project to associate with the task",
            autocompletion=__list_projects,
        ),
    ] = None,
    # Other existing parameters...
    parent_id: Annotated[
        int | None,
        Option(
            "--parent-id", 
            "-pid",
            help="ID of the parent task if this is a subtask",
        ),
    ] = None,
):
    """
    Create a new task in the database.
    
    Args:
        title: Title of the task. Multiple tasks can be created by providing comma-separated titles.
        # Other existing args...
        parent_id: ID of the parent task if this task is a subtask.
    """
    # Existing code...
    with session_scope() as session:
        task = {
            "title": title,
            "description": description,
            "status": status,
            "project_id": project_id,
            "parent_id": parent_id,  # Add parent_id to task creation
        }
        created_task = create_task_in_db(session, task)
        # Rest of the existing code...

@cli.command(name="tl")
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    pending_only: bool = True,
    as_hierarchy: bool = True,
    root_only: bool = Option(False, "--root-only", help="Show only root-level tasks (no parent)"),
    with_subtasks: bool = Option(False, "--with-subtasks", help="Show tasks with their subtasks"),
):
    """
    List all tasks in the database with optional pagination and filtering.
    
    Args:
        # Existing args...
        root_only: If True, only show top-level tasks with no parent.
        with_subtasks: If True, include subtask information in the display.
    """
    with session_scope() as session:
        tasks = get_all_tasks_from_db(
            session,
            skip=skip,
            limit=limit,
            pending_only=pending_only,
            as_hierarchy=as_hierarchy,
            root_level_only=root_only,
        )
        # Existing code for processing and displaying tasks...
        # Add special handling for displaying subtasks in hierarchical format
```

### Implementation Strategy

1. Update the `Task` model first to add the `parent_id` field and `subtasks` relationship.
2. Run database migrations to add the new foreign key field.
3. Update CRUD operations to handle the new hierarchical structure.
4. Update the CLI commands to support working with subtasks.
5. Update API endpoints to support the subtask functionality.
6. Write tests to verify the functionality, especially subtask creation and retrieval.
7. Update documentation.

### Potential Challenges

1. **Database Migration:** Adding a new foreign key with a self-reference will require careful migration planning to avoid breaking existing data.
2. **Recursive Calculations:** Handling properties that depend on subtasks (like completion status or total time) may require recursive calculations, which need to be optimized.
3. **UI Considerations:** Displaying a hierarchical task structure in various UIs (CLI, Web, etc.) will require additional display logic.
4. **Task Lifecycle Management:** When completing a parent task, decide on the policy for subtasks (e.g., should they be automatically completed?).

## 3. Redis DB Migration

**Task Description:** Evaluate and implement Redis as a database backend for improved performance.

### Required Changes

#### 3.1. Infrastructure Setup

1. **Redis Installation:**
   - Add Redis as a dependency in the project.
   - Setup Redis instance (local development and production).

```bash
# Add to requirements.in
redis>=5.0.0
rejson>=0.5.6  # For JSON support in Redis
```

2. **Connection Management:**
   - Create a new module for Redis connection management.

```python
# src/td/core/redis_db.py
import redis
from rejson import Client
from typing import Optional
from .settings import get_settings

_redis_client: Optional[Client] = None

def get_redis_client() -> Client:
    """
    Get a Redis client instance with JSON support.
    Creates a singleton client instance for the application.
    """
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = Client(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True,
        )
    return _redis_client

def close_redis_connection():
    """Close the Redis connection."""
    global _redis_client
    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
```

3. **Settings Updates:**
   - Add Redis-specific settings to the application.

```python
# src/td/core/settings.py
class Settings:
    # Existing settings...
    
    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # Toggle to use Redis or SQLite
    use_redis: bool = False
```

#### 3.2. Data Model Modifications

1. **Redis Schema Design:**
   - Define key naming conventions and data structures for Redis.

```python
# src/td/models/redis_schema.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

# Key prefixes
AREA_PREFIX = "area:"
PROJECT_PREFIX = "project:"
TASK_PREFIX = "task:"
TIME_ENTRY_PREFIX = "time_entry:"

# Index names
AREA_IDX = "idx:areas"
PROJECT_IDX = "idx:projects"
TASK_IDX = "idx:tasks"
PENDING_TASK_IDX = "idx:pending_tasks"
TIME_ENTRY_IDX = "idx:time_entries"

# Relationship indices
AREA_PROJECTS_IDX = "idx:area:{area_id}:projects"
PROJECT_TASKS_IDX = "idx:project:{project_id}:tasks"
TASK_SUBTASKS_IDX = "idx:task:{task_id}:subtasks"
TASK_TIME_ENTRIES_IDX = "idx:task:{task_id}:time_entries"

def area_key(area_id: int) -> str:
    """Generate Redis key for an area."""
    return f"{AREA_PREFIX}{area_id}"

def project_key(project_id: int) -> str:
    """Generate Redis key for a project."""
    return f"{PROJECT_PREFIX}{project_id}"

def task_key(task_id: int) -> str:
    """Generate Redis key for a task."""
    return f"{TASK_PREFIX}{task_id}"

def time_entry_key(time_entry_id: int) -> str:
    """Generate Redis key for a time entry."""
    return f"{TIME_ENTRY_PREFIX}{time_entry_id}"
```

2. **Model Adaptations:**
   - Create Redis-compatible serialization/deserialization for models.

```python
# src/td/models/task.py
# Add Redis serialization methods to existing models

class Task(TaskBase, table=True):
    # Existing SQLModel definition...
    
    def to_redis_dict(self) -> dict:
        """Convert Task to Redis-compatible dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "project_id": self.project_id,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_redis_dict(cls, data: dict) -> "Task":
        """Create Task instance from Redis data."""
        # Convert string dates back to datetime objects
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)
```

#### 3.3. CRUD Operations Modifications

1. **Redis CRUD Implementations:**
   - Create parallel Redis implementations for CRUD operations.

```python
# src/td/crud/redis/task.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from rejson import Client
from ...models.task import Task, TaskCreate, TaskRead
from ...models.redis_schema import task_key, TASK_IDX, PROJECT_TASKS_IDX, TASK_SUBTASKS_IDX
from ...core.redis_db import get_redis_client

def create_task_in_redis(task_data: Dict[str, Any]) -> Task:
    """
    Create a new task in Redis.
    
    Args:
        task_data: Task data dictionary
    """
    redis_client = get_redis_client()
    
    # Generate ID (use Redis to auto-increment)
    task_id = redis_client.incr("task:id:counter")
    
    # Create task with ID
    task_data["id"] = task_id
    task_data["created_at"] = datetime.now(timezone.utc)
    task_data["updated_at"] = datetime.now(timezone.utc)
    
    # Create Task instance
    task = Task(**task_data)
    
    # Save to Redis
    redis_client.jsonset(task_key(task_id), '.', task.to_redis_dict())
    
    # Add to indices
    redis_client.sadd(TASK_IDX, task_id)
    
    # Add to project index if project_id is set
    if task.project_id:
        redis_client.sadd(PROJECT_TASKS_IDX.format(project_id=task.project_id), task_id)
    
    # Add to parent task index if parent_id is set
    if task.parent_id:
        redis_client.sadd(TASK_SUBTASKS_IDX.format(task_id=task.parent_id), task_id)
    
    return task

def get_task_by_id_from_redis(task_id: int) -> Optional[Task]:
    """
    Get a specific task by ID from Redis.
    
    Args:
        task_id: ID of the task to retrieve
    """
    redis_client = get_redis_client()
    
    # Check if task exists
    task_data = redis_client.jsonget(task_key(task_id), '.')
    if not task_data:
        return None
    
    return Task.from_redis_dict(task_data)

def get_all_tasks_from_redis(
    skip: int = 0,
    limit: int = 100,
    pending_only: bool = False,
    root_level_only: bool = False,
) -> List[Task]:
    """
    Retrieve all tasks from Redis with optional pagination and filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        pending_only: If True, only return pending tasks
        root_level_only: If True, only return top-level tasks (no parent)
    """
    redis_client = get_redis_client()
    
    # Get all task IDs (sorted by creation time would be ideal)
    if pending_only:
        # This would be better with a separate index for pending tasks
        # For demo purposes, we'll fetch all and filter
        task_ids = list(redis_client.smembers(TASK_IDX))
    else:
        task_ids = list(redis_client.smembers(TASK_IDX))
    
    # Apply pagination
    paginated_ids = task_ids[skip:skip+limit]
    
    # Fetch tasks
    tasks = []
    for task_id in paginated_ids:
        task_data = redis_client.jsonget(task_key(task_id), '.')
        if task_data:
            task = Task.from_redis_dict(task_data)
            
            # Apply filters
            if pending_only and task.status:
                continue
                
            if root_level_only and task.parent_id is not None:
                continue
                
            tasks.append(task)
    
    return tasks
```

2. **Data Migration Script:**
   - Create a script to migrate data from SQLite to Redis.

```python
# src/td/utils/migrate_to_redis.py
from typing import List
from sqlmodel import Session, select
from ..core.db import get_db
from ..core.redis_db import get_redis_client
from ..models.area import Area
from ..models.project import Project
from ..models.task import Task
from ..models.time_entry import TimeEntry
from ..models.redis_schema import (
    area_key, project_key, task_key, time_entry_key,
    AREA_IDX, PROJECT_IDX, TASK_IDX, TIME_ENTRY_IDX,
    AREA_PROJECTS_IDX, PROJECT_TASKS_IDX, TASK_SUBTASKS_IDX, TASK_TIME_ENTRIES_IDX
)

def migrate_areas(db: Session):
    """Migrate areas from SQLite to Redis."""
    redis_client = get_redis_client()
    areas = db.exec(select(Area)).all()
    
    # Reset counter
    redis_client.set("area:id:counter", 0)
    
    for area in areas:
        # Increment counter to current ID
        if area.id > int(redis_client.get("area:id:counter") or 0):
            redis_client.set("area:id:counter", area.id)
        
        # Save area
        redis_client.jsonset(area_key(area.id), '.', area.to_redis_dict())
        redis_client.sadd(AREA_IDX, area.id)

def migrate_projects(db: Session):
    """Migrate projects from SQLite to Redis."""
    redis_client = get_redis_client()
    projects = db.exec(select(Project)).all()
    
    # Reset counter
    redis_client.set("project:id:counter", 0)
    
    for project in projects:
        # Increment counter to current ID
        if project.id > int(redis_client.get("project:id:counter") or 0):
            redis_client.set("project:id:counter", project.id)
        
        # Save project
        redis_client.jsonset(project_key(project.id), '.', project.to_redis_dict())
        redis_client.sadd(PROJECT_IDX, project.id)
        
        # Add to area index
        if project.area_id:
            redis_client.sadd(AREA_PROJECTS_IDX.format(area_id=project.area_id), project.id)

def migrate_tasks(db: Session):
    """Migrate tasks from SQLite to Redis."""
    redis_client = get_redis_client()
    tasks = db.exec(select(Task)).all()
    
    # Reset counter
    redis_client.set("task:id:counter", 0)
    
    for task in tasks:
        # Increment counter to current ID
        if task.id > int(redis_client.get("task:id:counter") or 0):
            redis_client.set("task:id:counter", task.id)
        
        # Save task
        redis_client.jsonset(task_key(task.id), '.', task.to_redis_dict())
        redis_client.sadd(TASK_IDX, task.id)
        
        # Add to project index
        if task.project_id:
            redis_client.sadd(PROJECT_TASKS_IDX.format(project_id=task.project_id), task.id)
        
        # Add to parent task index
        if task.parent_id:
            redis_client.sadd(TASK_SUBTASKS_IDX.format(task_id=task.parent_id), task.id)

def migrate_time_entries(db: Session):
    """Migrate time entries from SQLite to Redis."""
    redis_client = get_redis_client()
    time_entries = db.exec(select(TimeEntry)).all()
    
    # Reset counter
    redis_client.set("time_entry:id:counter", 0)
    
    for time_entry in time_entries:
        # Increment counter to current ID
        if time_entry.id > int(redis_client.get("time_entry:id:counter") or 0):
            redis_client.set("time_entry:id:counter", time_entry.id)
        
        # Save time entry
        redis_client.jsonset(time_entry_key(time_entry.id), '.', time_entry.to_redis_dict())
        redis_client.sadd(TIME_ENTRY_IDX, time_entry.id)
        
        # Add to task index
        if time_entry.task_id:
            redis_client.sadd(TASK_TIME_ENTRIES_IDX.format(task_id=time_entry.task_id), time_entry.id)

def migrate_all_data():
    """Migrate all data from SQLite to Redis."""
    with get_db() as db:
        # Order matters due to foreign key relationships
        migrate_areas(db)
        migrate_projects(db)
        migrate_tasks(db)
        migrate_time_entries(db)
```

#### 3.4. API/CLI Layer Modifications

1. **Database Backend Toggle:**
   - Create a database factory that can switch between SQLite and Redis.

```python
# src/td/core/db_factory.py
from typing import Callable, Dict, Any, Union, Optional, List
from functools import wraps
from sqlmodel import Session
from rejson import Client
from .settings import get_settings
from .db import get_db
from .redis_db import get_redis_client

def get_db_backend():
    """
    Return the appropriate database backend based on settings.
    
    Returns:
        Either a SQLite session or Redis client.
    """
    settings = get_settings()
    if settings.use_redis:
        return get_redis_client()
    else:
        return get_db()

def with_db_backend(crud_func_sqlite, crud_func_redis):
    """
    Decorator factory to switch between SQLite and Redis CRUD functions.
    
    Args:
        crud_func_sqlite: CRUD function implementation for SQLite
        crud_func_redis: CRUD function implementation for Redis
    
    Returns:
        A function that calls the appropriate CRUD function based on settings.
    """
    @wraps(crud_func_sqlite)
    def wrapper(*args, **kwargs):
        settings = get_settings()
        if settings.use_redis:
            return crud_func_redis(*args, **kwargs)
        else:
            return crud_func_sqlite(*args, **kwargs)
    return wrapper
```

2. **CRUD Function Mapping:**
   - Add mapping between SQLite and Redis CRUD functions.

```python
# src/td/crud/task.py
from .redis.task import (
    create_task_in_redis,
    get_task_by_id_from_redis,
    get_all_tasks_from_redis,
)
from ..core.db_factory import with_db_backend

# Create unified CRUD functions that work with both backends
create_task = with_db_backend(
    crud_func_sqlite=create_task_in_db,
    crud_func_redis=create_task_in_redis
)

get_task_by_id = with_db_backend(
    crud_func_sqlite=get_task_by_id,
    crud_func_redis=get_task_by_id_from_redis
)

get_all_tasks = with_db_backend(
    crud_func_sqlite=get_all_tasks_from_db,
    crud_func_redis=get_all_tasks_from_redis
)
```

3. **CLI Commands:**
   - Add commands to switch between database backends.

```python
# src/td/cli/db.py
@cli.command(name="use-redis")
def use_redis(enabled: bool = True):
    """
    Toggle using Redis as the database backend.
    
    Args:
        enabled: If True, use Redis; if False, use SQLite.
    """
    settings = get_settings()
    settings.use_redis = enabled
    save_settings(settings)
    
    db_type = "Redis" if enabled else "SQLite"
    echo(f"Database backend set to {db_type}")

@cli.command(name="migrate-to-redis")
def migrate_to_redis():
    """Migrate all data from SQLite to Redis."""
    from ..utils.migrate_to_redis import migrate_all_data
    
    echo("Starting migration from SQLite to Redis...")
    migrate_all_data()
    echo("Migration completed successfully.")
```

### Implementation Strategy

1. **Infrastructure Setup:**
   - Install Redis and required packages.
   - Create Redis connection management.
   - Update application settings.

2. **Schema Design:**
   - Define key naming conventions.
   - Create serialization/deserialization methods.

3. **Parallel Implementation:**
   - Create Redis CRUD operations alongside existing SQLite operations.
   - Create a database factory for switching between backends.

4. **Data Migration:**
   - Develop a migration script from SQLite to Redis.
   - Test data integrity after migration.

5. **Integration:**
   - Modify API/CLI to work with both backends.
   - Add a toggle to switch between backends.

6. **Performance Benchmarking:**
   - Compare performance between SQLite and Redis implementations.
   - Fine-tune Redis configuration for optimal performance.

### Potential Challenges

1. **Complex Queries:** Redis is not a relational database, so complex joins and filters need to be implemented differently.

2. **Transaction Support:** Ensuring atomicity and consistency without traditional SQL transactions.

3. **Data Integrity:** Maintaining referential integrity without native foreign key constraints.

4. **Caching vs. Persistence:** Balancing Redis as a cache vs. persistent storage, including appropriate persistence settings.

5. **Schema Evolution:** Managing schema changes in a schema-less database.

### Performance Considerations

1. **Redis Configuration:**
   - Proper memory allocation and persistence settings.
   - Key expiration policies if needed.

2. **Indexing Strategy:**
   - Efficient index design for common query patterns.
   - Secondary indices for filtered queries.

3. **Data Access Patterns:**
   - Optimize data structures based on access patterns (SET, HASH, ZSET, etc.).
   - Consider denormalization for performance.

4. **Batch Operations:**
   - Use Redis pipelines for batched operations.
   - Reduce round trips to the server.
