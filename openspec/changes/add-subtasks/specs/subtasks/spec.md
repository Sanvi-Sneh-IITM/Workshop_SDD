## ADDED Requirements

### Requirement: Create subtask under owned task

The system SHALL allow an authenticated user to create a subtask on a task that belongs to one of the user's projects.

#### Scenario: Successful create

- **WHEN** the user sends `POST /tasks/{task_id}/subtasks` with a valid title and optional description/status
- **THEN** the system returns HTTP 201 with the created subtask including `id`, `task_id`, `title`, `status`, and `created_at`

#### Scenario: Parent task not found or not owned

- **WHEN** the user sends `POST /tasks/{task_id}/subtasks` for a task that does not exist or is not in the user's projects
- **THEN** the system returns HTTP 404

### Requirement: List subtasks for a task

The system SHALL return all subtasks for a given parent task when the user owns the parent task's project.

#### Scenario: Successful list

- **WHEN** the user sends `GET /tasks/{task_id}/subtasks`
- **THEN** the system returns HTTP 200 with a JSON array of subtasks ordered by creation time (ascending)

#### Scenario: List unauthorized task

- **WHEN** the user sends `GET /tasks/{task_id}/subtasks` for a task they do not own
- **THEN** the system returns HTTP 404

### Requirement: Get single subtask

The system SHALL return one subtask by id when it belongs to the specified parent task and the user owns the project.

#### Scenario: Successful get

- **WHEN** the user sends `GET /tasks/{task_id}/subtasks/{subtask_id}` with valid ids
- **THEN** the system returns HTTP 200 with the subtask body

#### Scenario: Subtask not found

- **WHEN** the subtask id does not exist or does not belong to `task_id`
- **THEN** the system returns HTTP 404

### Requirement: Update subtask

The system SHALL allow partial updates to subtask title, description, and status for owned tasks.

#### Scenario: Successful update

- **WHEN** the user sends `PUT /tasks/{task_id}/subtasks/{subtask_id}` with one or more optional fields
- **THEN** the system returns HTTP 200 with the updated subtask

#### Scenario: Invalid status

- **WHEN** the user sends a status value outside `todo`, `in_progress`, or `done`
- **THEN** the system returns HTTP 422

### Requirement: Delete subtask

The system SHALL allow an authenticated user to delete a subtask on an owned parent task.

#### Scenario: Successful delete

- **WHEN** the user sends `DELETE /tasks/{task_id}/subtasks/{subtask_id}` with valid ids
- **THEN** the system returns HTTP 200 with a confirmation message and removes the subtask from storage

### Requirement: Task detail includes subtasks

The system SHALL include the list of subtasks when returning a single task by id for an authorized user.

#### Scenario: Get task with subtasks

- **WHEN** the user sends `GET /tasks/{task_id}` for an owned task that has subtasks
- **THEN** the response includes a `subtasks` array containing all subtasks for that task

### Requirement: Cascade delete subtasks with parent task

The system SHALL delete all subtasks when the parent task is deleted.

#### Scenario: Delete parent task

- **WHEN** the user deletes a task that has subtasks
- **THEN** all associated subtask rows are removed and are no longer retrievable

### Requirement: Subtask status values

Subtask status SHALL use the same values as tasks: `todo`, `in_progress`, and `done`, with default `todo`.

#### Scenario: Default status on create

- **WHEN** the user creates a subtask without specifying status
- **THEN** the stored status is `todo`
