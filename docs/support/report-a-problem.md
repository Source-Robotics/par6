# Report a problem

Pick the kind of problem; each goes to the place where it gets fixed.

## A mistake in the documentation

At the end of every page:

- **Edit it on GitHub** opens the page's source in the documentation repository. Fix the text and open a pull
  request; no local setup needed.
- **Report it** opens a new issue with the page's title and address already filled in. Say what is wrong and, if
  you know it, what it should say.

## A bug in the runtime (the control box software)

Open an issue in the runtime repository: [Source-Robotics/RCB-Runtime → Issues](https://github.com/Source-Robotics/RCB-Runtime/issues/new).

Attach the **support bundle** (Dashboard → Logs → *Support bundle*): it holds the logs of every process, the
activity log, the incident recordings around any fault, and your configuration files. Without it, the first
reply will ask for it.

Also state:

- the runtime version (Dashboard → System Info → *Versions*, or the manual's landing page),
- the drive firmware version shown there,
- the control box PCB revision,
- what the robot was doing (mode, program, command), what you expected and what happened.

## A bug in the motor driver firmware

Open an issue in the firmware repository for the driver type (joint drives or the gripper drive) and attach the
same support bundle: the runtime logs show what the drive reported. Say which firmware version is flashed
(Dashboard → Motor tab).

## A hardware problem

Write to [petar@source-robotics.com](mailto:petar@source-robotics.com) with photos, the arm's serial number and
revision (the label on the base), and the support bundle if the robot was running.

## A safety concern

Anything that could injure someone: stop using the robot and write to the e-mail address above with "SAFETY" in
the subject. Do not wait for an issue to be answered.
