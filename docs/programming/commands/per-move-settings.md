---
status: new
---

# Per-move settings

Every move command takes these as keyword arguments. They apply to that one move:

```python
robot.move_joints(90, -105, 165, 0, -30, 180, speed=20, profile="trapezoid")
```

A setting you leave out takes its default. The commands in the last column change a default for every move sent
after them; a move's own setting still overrides it. Some settings matter only for some moves: a command's page says
which have no effect on it.

<!-- per-move-settings -->
