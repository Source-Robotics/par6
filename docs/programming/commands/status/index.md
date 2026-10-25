---
status: new
---

# Status and data commands

The commands that read the robot: joint angles, the tool's pose, its status, latched errors, the health of every
part, its hardware and versions, and whether a pose can be reached.

- **The `get_` commands ask the robot** and wait for its answer.
- **`latest_status()` and `errors()` ask nothing:** they read the status the robot last sent. Every field is in the
  [Status fields](../../references/status-fields.md) reference.

<!-- command-overview: status -->
