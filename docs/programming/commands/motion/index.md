---
status: new
---

# Motion commands

The moves a program queues: to joint angles or a pose, along straight lines, arcs, circles and smooth curves, and a
timed pause between them.

All motion commands:

- **Are queued.** A call returns once the robot has accepted the move, and the robot runs the moves in the order
  they were sent. Call `robot.wait_idle()` to wait until they have finished.
- **Need EXEC mode.** Every move also needs the robot enabled and homed; a pause only needs EXEC mode.
- **Take per-move settings** as keyword arguments, such as `speed`, `profile` or `blend`. They apply to that one
  move. Every setting is on the [Per-move settings](../per-move-settings.md) page.

Positions are in metres. Pose angles are in radians, or degrees with `angle_unit="deg"`. Joint angles are in
degrees.

<!-- command-overview: motion -->

The relative moves end in `_world` or `_tool`, for the frame their offsets are measured in:

- **`_world`**: along axes parallel to the robot's base frame.
- **`_tool`**: along the tool's own axes, as they are when the move starts.

## Other names

Some commands have a second name from earlier versions of the library. Both names do exactly the same, in a program
and in a raw protocol message, and programs that use the second name keep working. New programs use the names on
these pages.

<!-- command-aliases: motion -->
