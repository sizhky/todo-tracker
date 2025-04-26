# Task Management Commands

The task management system provides a set of CLI commands to manage your todos. All tasks are stored in `~/.todos/tasks.csv`.

## Available Commands

All task commands are available under the `todo-tracker task` namespace. Here are the available commands:

### Adding Tasks

```bash
# Add a task with just a title
todo-tracker task add "Buy groceries"

# Add a task with title and description
todo-tracker task add "Buy groceries" "Need milk, eggs, and bread"
```

### Listing Tasks

```bash
# List all tasks
todo-tracker task list
```

This will show all tasks with their:
- ID
- Title
- Status
- Description (if provided)

Example output:
```
[1] Buy groceries - pending
    Need milk, eggs, and bread
[2] Call mom - completed
```

### Updating Tasks

```bash
# Update task title
todo-tracker task update 1 --title "Buy more groceries"

# Update task description
todo-tracker task update 1 --description "Need milk, eggs, bread, and cheese"

# Update task status
todo-tracker task update 1 --status "in-progress"

# Update multiple fields at once
todo-tracker task update 1 --title "Buy groceries" --status "in-progress"
```

### Marking Tasks as Complete

```bash
# Mark a task as completed
todo-tracker task finish 1
```

### Deleting Tasks

```bash
# Delete a task by ID
todo-tracker task delete 1
```

## Task States

Tasks can have the following states:
- `pending` (default)
- `in-progress`
- `completed`

## Task Storage

Tasks are stored in `~/.todos/tasks.csv` with the following fields:
- `id`: Unique identifier for the task
- `title`: Task title (required)
- `description`: Task description (optional)
- `status`: Task status (pending/in-progress/completed)
- `created_at`: Timestamp when the task was created
- `updated_at`: Timestamp when the task was last updated
