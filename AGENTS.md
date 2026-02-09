# Agents

## Project

Comparative learning repo. The same reflective agent (task, validate, reflect, retry) is implemented independently across 6 frameworks. Implementations may use different languages.

## Structure rules

- Framework directories use kebab-case and are fully self-contained (own deps, own environment, no shared code).
- All implementations conform to `spec/task.md`.
- Do not create per-framework documentation files — observations are tracked externally.

## Evaluation harness

A shared cross-framework evaluation harness will be added later. When building any implementation, keep agent inputs and outputs aligned with the spec so the harness can be layered on without refactoring.
