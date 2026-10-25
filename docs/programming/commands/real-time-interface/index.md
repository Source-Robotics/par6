---
status: new
---

# Real-time interface commands

The commands that let a PC stream joint targets to the robot itself, every control cycle or at a lower rate, and
the settings of that stream. `RTIClient` is the client class that streams them.

- **The two contracts:** hard real time, one target for every control cycle (4 ms) over UDP, each carrying its send
  time; soft real time, `rti_connect(pc_ip, rate_hz=...)`, where the robot moves smoothly between targets sent at a
  lower rate.
- **The order:** `rti_connect()`, `rti_claim()`, stream, `rti_release()`, `rti_disconnect()`.

<!-- command-overview: rti -->
