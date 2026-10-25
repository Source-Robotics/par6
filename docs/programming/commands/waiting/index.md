---
status: new
---

# Waiting commands

The calls that wait, in your program, for something the robot reports: the queued moves to
finish, a mode, homing, the robot enabled, the errors cleared, or any condition of your own.

All of them:

- **Run in the client.** They read the status the robot sends, or the answers to the commands this client sent. A
  wait sends nothing to the robot.
- **End with an exception when time runs out.** A wait that runs out of time raises `RobotTimeout`; so does a wait
  during which the connection drops.

<!-- command-overview: waiting -->
