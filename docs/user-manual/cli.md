# CLI Usage Guide

This document provides a reference for all available Command Line Interface (CLI) commands in the `td` application. 
`td` should be available in your terminal once you `pip install -e .` the current library.

## Area Commands

Commands for managing areas. Areas are high-level organizational units.

### `td ac` (area-create)

Create a new area in the database.

```
td ac <area_name> [--description <area_description>]
```

**Arguments:**   
- `name`: Name of the area. Multiple areas can be created by providing comma-separated names.
- `description`: Optional description for the area.

**Returns:**
The ID of the created area.

!!! tip
    You can create multiple areas at once (albeit with no-description or common description for all of them) using a comma-separated name, i.e, 

    ```bash
    td ac area1,area2,area3 --description="some common description"
    ```
---

### `td al` (area-list)

List all areas in the database with optional pagination.

```bash
td al [--skip <number>] [--limit <number>]
```

**Arguments:**
- `skip`: Number of records to skip (default: 0).
- `limit`: Maximum number of records to return (default: 100).

**Returns:**
Prints the area information to the console.

---

### `td ad` (area delete)
Delete an area from the database by its name.

```bash
td ad <area_name>
```

**Arguments:**
*   `area`: Name of the area to delete. Multiple areas can be deleted by providing comma-separated names.

**Returns:**
Prints a confirmation message or error to the console.

!!! tip
    Just like task creation, you can delete multiple tasks using comma separation

    ```bash
    td ad area1,area2,area3
    ```

---

## Project Commands

Commands for managing projects. Projects belong to areas and group related tasks.

### `td pc` (project-create)

Create a new project in the database. You can associate it with an existing area by name or ID. If the specified area doesn't exist and you provide a name, it can be auto-created.

```bash
td pc <project_name> [--description <project_description>] [--area <area_name>] [--area-id <area_id>]
```

**Arguments:**
- `name`: Name of the project. Multiple projects can be created by providing comma-separated names (they will share other specified arguments like description and area).
- `description`: Optional description for the project.
- `area`: Name of the area to associate with the project. If not found, and `area_id` is not provided, a new area with this name will be created. Defaults to "default".
- `area_id`: ID of the area to associate with the project. Takes precedence over `area` name if both are provided.

**Returns:**
The ID of the created project. Prints a confirmation message to the console.

!!! tip
    Create multiple projects under the same area quickly:
    ```bash
    td pc "Project Alpha,Project Beta,Project Gamma" --area "Q2 Planning" --description "Key projects for Q2"
    ```
    If "Q2 Planning" area doesn't exist, it will be created.

---

### `td pl` (project-list)

List all projects in the database with optional pagination.

```bash
td pl [--skip <number>] [--limit <number>]
```

**Arguments:**
- `skip`: Number of records to skip (default: 0).
- `limit`: Maximum number of records to return (default: 100).

**Returns:**
Prints the project information (name, description, area name) to the console. If no projects are found, a message is displayed.

---

### `td pd` (project-delete)

Delete a project from the database by its name.

```bash
td pd <project_name>
```

**Arguments:**
- `project`: Name of the project to delete. Multiple projects can be deleted by providing comma-separated names.

**Returns:**
Prints a confirmation message with the ID of the deleted project or an error to the console.

!!! tip
    Clean up multiple old projects at once:
    ```bash
    td pd "Old Project X,Archived Initiative Y"
    ```

---

## Task Commands

Commands for managing tasks. Tasks belong to projects and represent individual to-do items.

### `td tc` (task-create)

Create a new task in the database. Tasks are associated with projects. If the specified project doesn't exist, it can be auto-created (optionally under a specified new or existing area).

```bash
td tc <task_title> [--description <task_description>] [--status <0_or_1>] [--project <project_name>] [--project-id <project_id>] [--area <area_name>] [--area-id <area_id>]
```

**Arguments:**
- `title`: Title of the task. Multiple tasks can be created by providing comma-separated titles (they will share other specified arguments).
- `description`: Optional description for the task.
- `status`: Task status (0 = pending, 1 = done). Default is 0 (pending).
- `project`: Name of the project to associate with the task. If not found and `project_id` is not provided, a new project with this name will be created. Defaults to "default".
- `project_id`: ID of the project to associate with the task. Takes precedence over `project` name.
- `area`: Name of the area to associate with an auto-created project (if `project` name is new and `project_id` is not given).
- `area_id`: ID of the area to associate with an auto-created project. Takes precedence over `area` name for auto-created projects.

**Returns:**
Prints a confirmation message with the ID of the created task to the console.

!!! tip
    Quickly add several tasks to a new or existing project:
    ```bash
    td tc "Design homepage,Develop API endpoints,Write tests" --project "Website Launch" --area "Marketing Q3"
    ```
    If "Website Launch" project or "Marketing Q3" area don't exist, they will be created.

---

### `td tl` (task-list)

List all tasks in the database with optional pagination and filtering.

```bash
td tl [--skip <number>] [--limit <number>] [--pending-only <true_or_false>] [--as-hierarchy <true_or_false>]
```

**Arguments:**
- `skip`: Number of records to skip (default: 0).
- `limit`: Maximum number of records to return (default: 100).
- `pending_only`: If `True` (default), only show tasks with status 0 (pending). Set to `False` to see all tasks.
- `as_hierarchy`: If `True` (default), group tasks by area and project. Set to `False` for a flat list.

**Returns:**
Prints the task information to the console. The format depends on `as_hierarchy`. If no tasks are found, a message is displayed.

!!! example "Viewing all tasks in a flat list"
    ```bash
    td tl --pending-only False --as-hierarchy False
    ```

---

### `td td` (task-delete)

Delete a task from the database by its ID.

```bash
td td <task_id>
```

**Arguments:**
- `task_id`: ID of the task to delete. Multiple tasks can be deleted by providing comma-separated IDs. Task ID must be an integer.

**Returns:**
Prints a confirmation message or error to the console.

!!! tip
    Remove multiple completed or irrelevant tasks:
    ```bash
    td td 101,105,112
    ```

---

### `td tt` (task-toggle)

Toggle the status of a task (pending to done, or done to pending) by its ID.

```bash
td tt <task_id>
```

**Arguments:**
- `task_id`: ID of the task to toggle. Multiple tasks can be toggled by providing comma-separated IDs. Task ID must be an integer.

**Returns:**
Prints a confirmation message indicating the new status or an error to the console.

!!! tip
    Mark several tasks as done in one go:
    ```bash
    td tt 23,24,27
    ```
