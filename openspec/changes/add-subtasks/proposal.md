## Why

The Task Manager API (Workshop_SDD) supports top-level tasks per project but cannot break work into smaller trackable units. Users need subtasks to decompose complex tasks, track partial progress, and complete parent work only when children are done. This is already listed as a planned enhancement in the project README.

## What Changes

- Add a `Subtask` data model linked to a parent `Task` with title, optional description, status, and timestamps
- Expose REST endpoints to create, list, get, update, and delete subtasks under an owned task
- Include subtasks in task detail responses (nested list) for convenient reads
- Enforce authorization: subtasks are only accessible when the parent task belongs to the authenticated user's project
- Cascade delete subtasks when a parent task is deleted
- Document new endpoints in README

## Capabilities

### New Capabilities

- `subtasks`: CRUD and listing of sub-items under a parent task, with status tracking aligned to existing task statuses (`todo`, `in_progress`, `done`)

### Modified Capabilities

<!-- No existing openspec specs; task and comment behavior at the API level is extended via nested responses only -->

## Impact

- **database.py**: New `Subtask` model and relationship on `Task`
- **schemas.py**: Pydantic create/update/response schemas for subtasks; optional nested subtasks on `Task` response
- **main.py**: New routes under `/tasks/{task_id}/subtasks` and updates to task GET if nesting is included
- **README.md**: API documentation and examples for subtasks
- **SQLite schema**: New `subtasks` table (created via `init_db` on startup; existing DBs get table on restart)
