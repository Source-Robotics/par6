---
status: draft
---

# Emergency stop and safety peripherals

*Stub.* <!-- sources: planning/01_structure_proposal_v1.md §4 -->

## If someone is caught by the arm

!!! danger "The E-stop does not free anyone"
    Pressed, the E-stop stops the robot and disables it ([`ESTOP`](../../programming/references/error-codes.md#1001-estop)),
    and a disabled robot holds every joint still: its motors stay on and resist being pushed back by hand. To free a
    trapped hand or finger, do one of these:

    - Support the arm and switch its motors off: the dashboard's **MOTORS OFF** button (confirm it in the dialog), or
      [`safety_stop()`](../../programming/commands/robot-control/safety_stop.md), which the robot accepts also with
      an error latched. The arm then goes limp and falls under its own weight.
    - Release the E-stop, clear the error and enable the robot. An enabled, homed arm in IDLE mode, with gravity
      compensation on, is in freedrive: it holds itself up and can be moved away by hand
      ([`enter_idle_mode()`](../../programming/commands/robot-control/enter_idle_mode.md)).

    Decide which before you need it.
