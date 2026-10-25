---
status: new
---

# Connection and events commands

The calls that connect a program to the robot, report the connection, and register functions the client calls when
something happens.

- **`connect()` first.** It checks that the robot speaks this client's protocol.
- **Callbacks run on the client's own receiving thread.** Keep them short, and never wait for the robot inside one.

<!-- command-overview: connection -->
