## 1. Data model

- [x] 1.1 Add `Subtask` SQLAlchemy model in `database.py` with `task_id` FK, title, description, status (`TaskStatus`), `created_at`
- [x] 1.2 Add `subtasks` relationship on `Task` with `cascade="all, delete-orphan"` and `back_populates`

## 2. Schemas

- [x] 2.1 Add `SubtaskBase`, `SubtaskCreate`, `SubtaskUpdate`, and `Subtask` Pydantic schemas in `schemas.py`
- [x] 2.2 Add optional `subtasks: List[Subtask]` field to `schemas.Task` for nested responses

## 3. API endpoints

- [x] 3.1 Implement `POST /tasks/{task_id}/subtasks` with parent task ownership check
- [x] 3.2 Implement `GET /tasks/{task_id}/subtasks` returning ordered subtask list
- [x] 3.3 Implement `GET /tasks/{task_id}/subtasks/{subtask_id}`
- [x] 3.4 Implement `PUT /tasks/{task_id}/subtasks/{subtask_id}` with partial update
- [x] 3.5 Implement `DELETE /tasks/{task_id}/subtasks/{subtask_id}`

## 4. Task detail integration

- [x] 4.1 Update `GET /tasks/{task_id}` to load and return nested `subtasks` on the task response
- [x] 4.2 Import `Subtask` in `main.py` and wire response models

## 5. Documentation and verification

- [x] 5.1 Update `README.md` with subtask endpoints, example curl commands, and note under Next Steps
- [x] 5.2 Manually verify flows via `/docs`: create task, add/list/update/delete subtasks, confirm cascade on task delete
