We have a new flexible 6-level hierarchy: sector > area > project > section > task > subtask. Each entity is a Node with a type. Tasks can be promoted/demoted (e.g., task → project), and every Node can be reparented.

Write Python code using `sqlmodel` that does the following:

1. Define a schema with a single `node` table:
   - `id TEXT PRIMARY KEY`
   - `title TEXT NOT NULL`
   - `type TEXT` CHECKed to be one of the allowed types
   - `parent_id TEXT` as a self-referential foreign key
   - `order REAL` for sorting among siblings
   - `metadata TEXT` to store JSON as a string
   - Also add indexes on `parent_id`, `(parent_id, type)`, and `type`

2. Create a helper `Node` class in Python that:
   - Can insert a node into the DB
   - Can promote/demote a node (change its type)
   - Can reparent a node
   - Can get all children of a node sorted by `order`

Use only the Python standard library (`sqlite3`, `uuid`, `json`). Use SQLModel