# Frequently asked questions

Short answers with a link to the page that has the long one. Grouped by who is asking.

## Building and setting up

**Which operating system image does the control box need?**
:   A real-time kernel image; the exact one is named in the Control Box Manual.
    [Step 1: The operating system image](../rcb/05-software-setup/step-1-os-image.md)

**How do I know my build is wired correctly before the first move?**
:   Run the first-run check; it verifies the box, every drive, the E-stop and the I/O before anything moves.
    [Step 1: The control box and the configuration](../par6/building/step-1-control-box.md)

## Operating

**Why must the arm be homed after every restart of the real-time loop?**
:   The encoders sit on the motors, not on the joints; the reference is found at the endstops.
    [Homing](../par6/05-operating/homing.md)

**The arm went limp when I stopped the service. Is that normal?**
:   Yes: the drives let go about 0.1 s after the runtime stops. Park or support the arm first.
    [Power and what "disabled" means](../rcb/02-safety/power-and-disabled.md)

## Programming

**Degrees or radians?**
:   Degrees and millimetres in the API; the runtime works in radians and newton-metres internally.
    [Units](../programming/02-basic-theory/units.md)

**Can two programs control the arm at the same time?**
:   No. One client holds control; stop, disable and clear-errors stay open to everyone.
    [Control ownership](../programming/02-basic-theory/control-ownership.md)

## Real-time interface

**What rate do I have to send at?**
:   The hard contract: every control cycle. The soft contract: your own rate, 5 to 50 Hz, and the robot
    interpolates. [Hard and soft contracts](../rti/contracts.md)
