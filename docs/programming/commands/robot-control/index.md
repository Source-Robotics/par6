---
status: draft
---

# Robot control commands

The commands that switch the motors on and off, home the arm, change the robot's mode, stop or pause a program, and
decide which client controls the robot.

All robot control commands:

- **Run at once.** They are not queued. The robot acts on each one when it arrives, also while moves are queued.
- **Can wait for the robot.** With `wait=True`, or on a client created with `RobotClient(sync=True)`, a call waits
  until the robot's status shows the change: up to 10 s, or 3 minutes for `home()`. Without a wait, the call returns
  once the robot has answered.
- **Mostly take control.** A command that changes what the robot does claims control for its client when no client
  holds it. Each page says whether its command takes control or is open to every client.

<!-- command-overview: robot_control -->
