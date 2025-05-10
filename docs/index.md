# Welcome to Todo Tracker Documentation

This is the main documentation for the Todo Tracker project.
Navigate through the sections to learn more about how interact with todo-tracker using CLI, API and MCP

Here's the high-level architecture of the library

```mermaid
graph TD
    A[(Core.db.SQLite)]
    B(Core.Settings)
    C(CRUD)
    A <--> C
    B --> C
    C <--> D(CLI)
    D <--> E(API) <--> G(WEB)
    D <--> F(MCP) <--> H(LLM)
```

And here's how todos are being stored in the database

```mermaid
erDiagram
    AREA {
        int id PK "Primary Key"
        string name "Unique name of the area"
        string description "Optional description"
        datetime created_at "Timestamp of creation"
        datetime updated_at "Timestamp of last update"
    }
    PROJECT {
        int id PK "Primary Key"
        string name "Unique name of the project"
        string description "Optional description"
        int area_id FK "Foreign Key to AREA"
        datetime created_at "Timestamp of creation"
        datetime updated_at "Timestamp of last update"
    }
    TASK {
        int id PK "Primary Key"
        string title "Title of the task"
        string description "Optional description"
        bool status "False (pending) or True (done)"
        int project_id FK "Foreign Key to PROJECT"
        datetime created_at "Timestamp of creation"
        datetime updated_at "Timestamp of last update"
    }

    AREA ||--o{ PROJECT : "contains"
    PROJECT ||--o{ TASK : "contains"
```
