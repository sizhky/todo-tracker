# Installation
This guide will walk you through the installation process for the `td` command-line application.

## Installation Steps

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/sizhky/todo-tracker
    cd todo-tracker
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    uv venv -p 3.13
    source .venv/bin/activate
    ```

3.  **Install the application**
    ```bash
    uv pip install -e .
    ```

After these steps, the `td` command should be available in your terminal. 

!!! fun-fact
    `td` is short for `todo`

You can verify this by running:
```
td --help
                                                                                              
Usage: td [OPTIONS] COMMAND [ARGS]...                                                                                                          
                                                                                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                                      │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                               │
│ --help                        Show this message and exit.                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ac        Create a new area in the database.                                                                                                 │
│ al        List all areas in the database with optional pagination.                                                                           │
│ ad        Delete an area from the database by its name.                                                                                      │
│ pc        Create a new project in the database.                                                                                              │
│ pl        List all projects in the database with optional pagination.                                                                        │
│ pd        Delete a project from the database by its name.                                                                                    │
│ tc        Create a new task in the database.                                                                                                 │
│ tl        List all tasks in the database with optional pagination.                                                                           │
│ td        Delete a task from the database by its id.                                                                                         │
│ tt        Toggle the status of a task in the database by its id.                                                                             │
│ onboard   Initialize the database with default areas, projects, and tasks.                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

You can use `td onboard` to create a quick list of areas, projects and tasks to play with cli/api/mcp

!!! fun-fact
    If you have tasks in your database - just `td` will list them down

```bash
$ td onboard
$ td
                                             title description  id
area     project                                                  
home     gym                     Buy running shoes              18
         gym                    Get gym membership              19
         gym                       Join yoga class              20
         home                      Clean the house              21
         home                      Organize garage              22
         home                           Do laundry              23
office   clients                 Meet with clients              15
         clients             Prepare presentations              16
         clients             Send follow-up emails              17
         desk                        Organize desk              12
         desk                        Arrange files              13
         desk                      Set up computer              14
         intro      Schedule introductory meetings               8
         intro        Prepare onboarding documents               9
         intro            Set up new user accounts              10
         intro             Review company policies              11
         supplies                         Buy pens               1
         supplies              Order printer paper               2
         supplies                Purchase staplers               3
outdoor  outdoor                     Go for a walk              24
         outdoor                       Plan a hike              25
         outdoor                      Visit a park              26
personal food                          Cook dinner              30
         food                        Prepare lunch              31
         food                       Make breakfast              32
         groceries                        Buy milk               4
         groceries                        Get eggs               5
         groceries                  Purchase bread               6
         groceries                     Find cheese               7
         groceries                   Buy groceries              27
         groceries                      Plan meals              28
         groceries                 Organize pantry              29
```