---
status: new
---

# Motion settings commands

The settings every queued move uses unless the move passes its own: the speed, the motion profile, blending, the
inverse kinematics engine, and when a move counts as complete.

All of them:

- **Set a default for this robot, not for one move.** A move's own setting, passed as a keyword argument, wins for
  that move. Every setting is on the [Per-move settings](../per-move-settings.md) page.
- **Last until changed or until the robot software restarts,** for every client.

<!-- command-overview: motion_settings -->
