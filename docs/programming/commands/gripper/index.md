---
status: new
---

# Gripper commands

The commands that open, close and move the gripper, wait for it, read how its last move ended, and set how it is
driven.

- **Open, close and move are queued** with the moves, in program order. The robot starts the jaws once it has sent
  the moves before them, so the jaws can move while the arm still moves.
- **The settings run at once.** `GripperResult` is what `gripper_result()` returns.

<!-- command-overview: gripper -->
