# Step 6: System check

Reboot the Pi. The service starts the runtime, and the real-time loop writes its start-up into `logs/RTI.log` in the
runtime's folder. Do the first start with the arm resting safely and nothing in its reach, and check that the
E-stop stops the robot before you enable motion.

!!! success "Check"
    `logs/RTI.log` has these lines from the start:

    - `real-time setup OK`, not `DEGRADED` or `FAILED`: the loop runs with real-time priority on its own core;
    - `memory locked`: its memory cannot be swapped out;
    - `interrupt threads ... on core 2 alone`: the CAN chip's interrupts have a core to themselves;
    - after `STARTUP SELFCHECK`, `CAN scan OK` with every drive present, and `PASSED — all checks OK`.

    Then home the arm ([Homing](../../par6/05-operating/homing.md)). If a line is missing or the self-check fails,
    `bash scripts/setup_system.sh --check` ([Step 4](step-4-service.md)) names what is not set up. A drive missing from
    the CAN scan does not answer on the bus: check its cable, its supply and its address
    ([CAN bus and drive addresses](../04-installing/can-bus.md)).
