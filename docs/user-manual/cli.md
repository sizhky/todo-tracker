# CLI Usage Guide

This document provides a reference for all available Command Line Interface (CLI) commands in the `td` application. 
`td` should be available in your terminal once you `pip install -e .` the current library.

## DB Commands

Commands for swapping/switching active task database.

### `td db.a` (database-active)

Print the path active sqlite database
```bash
$ td db.a
Active database link: '/Users/yeshwanth/.todo/active.db'
 -> Points to: '/Users/yeshwanth/.todo/tracker.db'
```

### `td db.l` (database-list)

List the available databases
```bash
$ td db.l
Available databases in '/Users/yeshwanth/.todo':
- default.db
- onboard.db
- tracker.db (active)
- yolo.db

The active database link 'active.db' currently points to 'tracker.db'.
```

### `td db.set` (database-set)

Set a specific database as current active
```bash
$ td db.set yolo
Success! Active database link 'active.db' now points to 'yolo.db'.
The application will use '/Users/yeshwanth/.todo/yolo.db' for all subsequent operations.
Using existing database file '/Users/yeshwanth/.todo/yolo.db'.


$ td db.set yolox
Success! Active database link 'active.db' now points to 'yolox.db'.
The application will use '/Users/yeshwanth/.todo/yolox.db' for all subsequent operations.
Creating tables in new database '/Users/yeshwanth/.todo/yolox.db'...
```

!!! fun-fact
    if you want to use multiple dbs at once across different teminal sessions, set the variable `TD_DB` 
    to a new name such as `active2` and set your second db in that session as active
    the second db will have a new softlink called `active2.db` in the `~/.todo` folder and this pointer
    is used as the active db for the terminal session

### `td db.rm` (database-remove)

```bash
$ td db.rm yolox
```

!!! fun-fact
    Autocompletion for `db.set` and `db.rm` work by listing the files at `~/.todo/*.db`

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

    Also, autocomplete is available here

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

    Also autocomplete is available here

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

    -p: project (with autocompletion)
    -a: area (with autocompletion)
    -d: description

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
Prints the task information to the console. The format depends on `as_hierarchy`. If `as_hierarchy` is true, tasks are grouped by area and project, and each task will show its ID, title, description (if any), and total time spent (`task_time`). If no tasks are found, a message is displayed.

!!! example "Default task list output (hierarchical, pending only)"
    ```bash
    $ td tl 
    # or simply 'td'
                                                 title description  id  task_time
    area     project                                                             
    home     gym                     Buy running shoes              18        0.0
             gym                    Get gym membership              19        0.0
             gym                       Join yoga class              20        0.0
             home                      Clean the house              21        0.0
             home                      Organize garage              22        0.0
             home                           Do laundry              23        0.0
    office   clients                 Meet with clients              15        0.0
             clients             Prepare presentations              16        0.0
             clients             Send follow-up emails              17        0.0
             desk                        Organize desk              12        0.0
             desk                        Arrange files              13        0.0
             desk                      Set up computer              14        0.0
             intro      Schedule introductory meetings               8        0.0
             intro        Prepare onboarding documents               9        0.0
             intro            Set up new user accounts              10        0.0
             intro             Review company policies              11        0.0
             supplies                         Buy pens               1     3600.0
             supplies              Order printer paper               2     3600.0
             supplies                Purchase staplers               3     3600.0
    outdoor  outdoor                     Go for a walk              24        0.0
             outdoor                       Plan a hike              25        0.0
             outdoor                      Visit a park              26        0.0
    personal food                          Cook dinner              30        0.0
             food                        Prepare lunch              31        0.0
             food                       Make breakfast              32        0.0
             groceries                        Buy milk                4   3600.0
             groceries                        Get eggs                5        0.0
             groceries                  Purchase bread                6        0.0
             groceries                     Find cheese                7        0.0
             groceries                   Buy groceries              27        0.0
             groceries                      Plan meals              28        0.0
             groceries                 Organize pantry              29        0.0
    ```

!!! example "Viewing all tasks in a flat list"
    ```bash
    td tl --pending-only False --as-hierarchy False
    ```

!!! example "Example Output for `td tl` (hierarchy view)"
    ```                                      title description  id  task_time
    area     project                             
    home     gym                     Buy running shoes              18        0.0
             gym                    Get gym membership              19        0.0
             gym                       Join yoga class              20        0.0
             home                      Clean the house              21        0.0
             home                      Organize garage              22        0.0
             home                           Do laundry              23        0.0
    office   clients                 Meet with clients              15        0.0
             clients             Prepare presentations              16        0.0
             clients             Send follow-up emails              17        0.0
             desk                        Organize desk              12        0.0
             desk                        Arrange files              13        0.0
             desk                      Set up computer              14        0.0
             intro      Schedule introductory meetings               8        0.0
             intro        Prepare onboarding documents               9        0.0
             intro            Set up new user accounts              10        0.0
             intro             Review company policies              11        0.0
             supplies                         Buy pens               1     3600.0
             supplies              Order printer paper               2     3600.0
             supplies                Purchase staplers               3     3600.0
    outdoor  outdoor                     Go for a walk              24        0.0
             outdoor                       Plan a hike              25        0.0
             outdoor                      Visit a park              26        0.0
    personal food                          Cook dinner              30        0.0
             food                        Prepare lunch              31        0.0
             food                       Make breakfast              32        0.0
             groceries                        Buy milk               4     3600.0
             groceries                        Get eggs               5        0.0
             groceries                  Purchase bread               6        0.0
             groceries                     Find cheese               7        0.0
             groceries                   Buy groceries              27        0.0
             groceries                      Plan meals              28        0.0
             groceries                 Organize pantry              29        0.0
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

### `td tto` (task-toggle)

Toggle the status of a task (pending to done, or done to pending) by its ID.

```bash
td tto <task_id>
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

## Task Time Tracking commands

These commands allow you to track the time spent on individual tasks.

### `td trstart <task_id>` (task-track-start)

Starts the time tracker for a specific task. If another task is currently being tracked, its timer will be stopped automatically, and the new task's timer will start.

```bash
td trstart <task_id>
```

**Arguments:**
- `task_id`: The ID of the task to start tracking.

**Returns:**
Prints a confirmation message indicating which task has started tracking. If another task was stopped, it also prints how long that task was tracked in the last session.

**Example:**
```bash
$ td trstart 15
Started tracking task 15.

$ td trstart 10
Stopped tracking task 15 after 0h5m12s.
Started tracking task 10.
```

---

### `td trstop [task_id]` (task-track-stop)

Stops the time tracker. 
- If a `task_id` is provided, it stops the timer for that specific task (if it's active).
- If no `task_id` is provided, it stops any currently active timer.

```bash
td trstop [task_id]
```

**Arguments:**
- `task_id` (optional): The ID of the task to stop tracking.

**Returns:**
Prints a confirmation message. If a timer was stopped, it includes the duration of the tracking session. If no timer was active or the specified task was not being tracked, it will indicate that.

**Example:**
```bash
# Stop tracking task 10
$ td trstop 10
Stopped tracking task 10 after 1h20m15s.

# Stop any active timer
$ td trstop
Stopped tracking task 12 after 0h30m00s.

# No timer active
$ td trstop
No active time entry to stop.
```

---

### `td trl <task_id>` (task-track-list)

Lists all recorded time entries for a specific task. This includes start time, end time (if stopped), and duration for each session.

```bash
td trl <task_id>
```

**Arguments:**
- `task_id`: The ID of the task for which to list time entries.

**Returns:**
Prints a list of time entries for the task, or a message if no entries are found.
Each entry shows: `ID, Task ID, Start Time, End Time, Duration (seconds)`.

**Example:**
```bash
$ td trl 10
Time entries for Task ID 10:
ID  Task ID  Start Time           End Time             Duration (s)
--  -------  -------------------  -------------------  --------------
1   10       2025-05-10 10:00:00  2025-05-10 11:20:15  4815.0
2   10       2025-05-11 09:30:00  None                 None (Active)
```
If a time entry is still active, `End Time` and `Duration` will be `None`.

---

### `td trt [task_id]` (task-track-toggle)

Toggles the time tracker for a task.
- If a `task_id` is provided:
    - If the specified task is currently being tracked, its timer will be stopped.
    - If the specified task is not being tracked, its timer will be started. If another task is currently active, that task's timer will be stopped first.
- If no `task_id` is provided:
    - If any task is currently being tracked, its timer will be stopped.
    - If no task is being tracked, it will inform the user that a `task_id` is needed to start tracking.


```bash
td trt [task_id]
```

**Arguments:**
- `task_id` (optional): The ID of the task to toggle.

**Returns:**
Prints a confirmation message indicating whether the task's timer has started or stopped. If a timer is stopped (either the specified one or a previously active one), it also returns how long the session was.

**Example:**
```bash
# Start tracking task 10 (assuming no other task is active)
$ td trt 10
Started tracking task 10.

# Stop tracking task 10 (which was active)
$ td trt 10
Stopped tracking task 10 after 0h45m30s.

# Start tracking task 12 (task 10 was active and will be stopped)
$ td trt 12
Stopped tracking task 10 after 1h20m15s.
Started tracking task 12.

# Stop any active timer (task 12 was active)
$ td trt
Stopped tracking task 12 after 0h10m05s.

# No timer active, and no task_id provided
$ td trt
No active time entry to stop. Provide a task ID to start tracking.
```

