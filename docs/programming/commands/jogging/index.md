---
status: new
---

# Jogging commands

The commands that move one joint at a time on request, as a teach pendant's jog buttons do, and the settings for
how a jog speeds up and brakes.

- **JOG mode first:** `enter_jog_mode()`. A joint moves while `jog()` asks for it and stops at `jog_stop()` or at a
  limit, where it brakes by itself.
- **Joints are counted from 0** in `jog()`: `0` is J1, `5` is J6.

<!-- command-overview: jogging -->
