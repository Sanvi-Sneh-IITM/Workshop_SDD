## Context

The Workshop_SDD Task Manager API is a FastAPI + SQLAlchemy + SQLite application with users, projects, tasks, and comments. Tasks are flat: each row in `tasks` belongs to exactly one project. Authentication uses JWT; all task operations verify project ownership via `Project.owner_id`. Subtasks are a new child entity, not a second project-level task type.

## Goals / Non-Goals

**Goals:**

- Model subtasks as rows in a dedicated `subtasks` table with `task_id` foreign key
- Reuse existing `TaskStatus` enum for subtask status
- Provide full CRUD at `/tasks/{task_id}/subtasks` with the same ownership checks as comments
- Return subtasks nested on `GET /tasks/{id}` for a single-call task detail view
- Delete subtasks automatically when parent task is deleted (SQLAlchemy cascade)

**Non-Goals:**

- Multi-level nesting (subtasks of subtasks)
- Subtasks without a parent task or attached to projects directly
- Automatic parent task status rollup when all subtasks are done
- Comments on subtasks (comments remain task-level only)
- Database migrations framework (continue using `create_all` on startup)

## Decisions

### 1. Separate `Subtask` table vs. self-referential `Task.parent_id`

**Choice:** Dedicated `Subtask` model and table.

**Rationale:** Parent tasks already require `project_id`; subtasks should not duplicate project scope or appear in project-level task lists/filters. A separate table keeps list/filter queries unchanged and avoids nullable `project_id` on child rows.

**Alternative:** Add `parent_task_id` to `Task` — simpler one-model API but pollutes `GET /tasks` unless every query filters `parent_task_id IS NULL`.

### 2. API shape: nested resource routes

**Choice:** `/tasks/{task_id}/subtasks` for list/create; `/tasks/{task_id}/subtasks/{subtask_id}` for get/update/delete.

**Rationale:** Matches existing pattern (`/tasks/{task_id}/comments`) and makes ownership verification reuse the same parent-task lookup.

### 3. Status model

**Choice:** Reuse `TaskStatus` (`todo`, `in_progress`, `done`) on subtasks; default `todo`.

**Rationale:** Consistent with parent tasks and existing schemas; no new enum surface for clients.

### 4. Response nesting

**Choice:** Add optional `subtasks: List[Subtask]` on `schemas.Task` for `GET /tasks/{id}` only (eager load relationship). List endpoint `GET /tasks` returns tasks without subtasks to avoid N+1 payload bloat.

**Rationale:** Detail view needs breakdown; list view stays lightweight.

### 5. Schema creation

**Choice:** Rely on `init_db()` / `Base.metadata.create_all` for new `subtasks` table.

**Rationale:** Matches current project; no Alembic in repo. Document that developers may delete `task_manager.db` locally if schema drift occurs.

## Risks / Trade-offs

- **[Risk] Existing SQLite DB missing `subtasks` table** → Mitigation: `create_all` adds new table on restart; document local reset if needed
- **[Risk] Large subtask lists on task detail** → Mitigation: Accept for workshop scope; pagination is a future enhancement
- **[Risk] Client confusion between tasks and subtasks** → Mitigation: Clear README and OpenAPI tags/descriptions

## Migration Plan

1. Deploy code with new model and routes
2. Restart app so `init_db()` creates `subtasks` table
3. No data backfill required (greenfield feature)
4. Rollback: revert code; old clients ignore unknown routes; optional manual drop of `subtasks` table if needed

## Open Questions

- None blocking implementation. Optional future: auto-set parent task to `done` when all subtasks are `done`.
