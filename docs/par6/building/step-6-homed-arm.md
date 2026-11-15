---
status: new
---

# Step 6: The homed arm

Stage 5 of [the first-run check](first-run-check.md) moves the homed arm with normal joint moves, the kind a program makes, at 10 % speed and with the joints' normal force: nothing is limited for this test, and every move passes the robot's own checks first (the joint limits, the safety zones, the self-collision check). It has three checks. First each joint turns a visible amount and back, on PAR6 between 30 degrees and a quarter turn, and you judge how far it turned: a wrong gear ratio or encoder setting turns a joint clearly more or less than commanded, a slipping coupling not at all. Meanwhile the robot measures the joint's friction against the robot XML's friction model and checks that the joint holds still without buzzing. Then the gripper closes and opens. Last, J1 starts a slow 15 degree move that is stopped part-way: the arm must stop short and hold.

!!! danger "Danger"
    The homed arm moves at 10 % speed with its normal motor force, nothing limited for the test: a joint up to a quarter turn, J1 turning the whole arm, the gripper's jaws closing.

    Anyone in the arm's reach can be struck, and fingers between the jaws can be pinched.

    - Clear the space around the arm and keep a hand on the E-stop, as the check asks before the joints turn and before the stop test.
    - Keep your fingers away from the jaws, as the check asks before the gripper moves.
    - **Skip** and **Stop the run** stop a joint's turn where it is. During the gripper's moves and J1's move and return the check offers no Skip, and **Stop the run** takes effect at the next wait or question. None of them, Ctrl-C included, is an emergency stop: to stop the arm at once, press the E-stop or **Disable** in the dashboard.

**Prerequisites**

- Step 5 passed: the arm homed. On an arm that is not homed every step of this stage is skipped.
- The arm ENABLED. When it is DISABLED, each step asks *The arm is DISABLED. Clear the space around it, then press Enable in the dashboard (it holds where it is; nothing moves yet) — waiting for the arm to be enabled* and waits up to 180 s; after that the step is skipped. The check never enables the arm itself.
- The robot in IDLE or EXEC, no error latched. Each step puts the robot in EXEC for its moves and back in IDLE when it ends.
- Room for each joint to turn one way or the other: a turn the robot refuses one way (a joint limit, a safety zone, the arm against itself) is tried the other way.
- For the gripper step: a gripper on CAN (stage 0 reads it from the configuration), powered, with nothing between its jaws.
- Control of the robot free. Each step takes control; the dashboard keeps it for 5 s after your last click there (the Enable click too), and the check waits up to 15 s for it.
- The check runs on the robot's Raspberry Pi: the friction is read from the Pi's shared memory. From another computer (`--host`) it reads nothing and the friction is not measured.

## Procedure

**In the dashboard:** open the **First run** tab, tick **5 The homed arm** (untick the stages you do not want to run) and press **Start**.

**In a terminal** on the robot's Raspberry Pi:

```bash
cd ~/Desktop/RCB-Runtime && .venv/bin/python3 tools/first_run.py --stages 5
```

Without stage 0 in the list, stage 0's configuration and robot-service checks still run first: this stage needs them.

The stage begins with *Stage 5: The homed arm* and the line *The arm homed: each joint turns a visible amount and back (you judge how far; its friction and a quiet hold are measured), the gripper closes and opens, and a slow move is stopped part-way.* Its three checks run in this order, and each one starts the same way:

1. If the arm is DISABLED, the check waits up to 180 s for you to press **Enable** (see Prerequisites).
2. If the arm is not homed, the step ends with a SKIP. If the robot is in neither IDLE nor EXEC, the step ends with a SKIP. (The gripper step first checks that there is a gripper on CAN.)
3. The step's own question, answered with **start** or **skip** (skip: the step ends with a SKIP, nothing moves).
4. The check takes control of the robot. If the dashboard still holds it, the check shows *Another client holds control — the dashboard lets go 5 s after its last click; waiting for it* and waits up to 15 s.
5. The robot is put in EXEC, unless it is there already.
6. The step's moves (below). When the step ends, whatever the result, the robot is put back in IDLE.

**Each joint** (`S5.joints`). The question: *Each joint now turns a visible amount and back, slowly, J6 first: you judge how far it turned; the robot measures its friction and checks that it holds quietly. Clear the space around the arm and keep a hand on the E-stop.* Then each joint, in the order **J6, J5, J4, J1, J3, J2**:

1. *`<name>`: turns `<deg>` deg (`<looks like>`) and back, slowly. Go?* — for example *J6: turns 90 deg (a quarter turn) and back, slowly. Go?*
    - **go**: the turn starts.
    - **skip this joint**: a SKIP for this joint; the next joint follows.
2. *`<name>` turns +`<deg>` deg — watch how far*: the joint turns the + way at 10 % speed. The check waits up to 60 s for the move. If the robot refuses the + turn before moving (a joint limit, a safety zone, the arm against itself, or the zone check unavailable), the - turn follows at once, without a message: *`<name>` turns -`<deg>` deg — watch how far*.
3. *`<name>` turns back*: back to where it started, again up to 60 s.
4. *`<name>` holds still for 2 s*.
5. *Did `<name>` turn about `<deg>` deg (`<looks like>`) and back?* — four answers:
    - **about that**
    - **clearly less (half or less)**
    - **clearly more (double or more)**
    - **I saw no movement**
6. The joint's results appear; the next joint follows.

A Skip (Ctrl-C) during 2 or 3 stops the joint where it is and skips that joint: the joint is not turned back, and the next joint starts from where the arm now is. A Skip during the 2 s hold skips the joint as well. If a move fails for any other reason than the four refusals above, or a turn does not finish within 60 s (the check then stops it), the step ends with a FAIL and the joints after it are not turned.

**The gripper** (`S5.gripper`). Without a gripper on CAN the step is a SKIP at once (after the wait for **Enable**). The question: *The gripper now closes, then opens. Keep fingers away from the jaws.* Then:

1. The gripper closes; the check waits up to 30 s for the robot to report the move finished. No Skip is offered during this wait. If the move has not finished after 30 s, the check sends a Stop, which holds the jaws where they are.
2. *Did the jaws close fully?* — **yes** or **no**.
3. The gripper opens, again up to 30 s.
4. *Did the jaws open fully?* — **yes** or **no**.

If the robot reports that the close failed, or the close did not finish within 30 s, the step ends with a FAIL and the gripper is not opened. The same for the opening.

**A stop mid-move** (`S5.stop`). The question: *J1 now starts a slow 15 deg move and is stopped part-way (as a program's stop() does), then returns. Clear the space around the arm and keep a hand on the E-stop.* Then:

1. J1 starts a 15 degree turn the + way at 10 % speed (the - way when the robot refuses the + way before moving, for the same four reasons as above).
2. 0.6 s after the move was sent, the check sends a Stop.
3. *J1 holds after the stop*: the check waits 1 s and measures how far J1 drifts. A Skip here ends the step with a SKIP that says how far J1 had turned: the hold is not judged, and J1 stays where it stopped (it is not moved back).
4. J1 moves back to where it started; the check waits up to 60 s, with no Skip offered.
5. The results appear.

Stage 5 is the last stage: after it the run ends and the report is written, also when the stage has a FAIL.

!!! note "Note"
    During the gripper's moves, J1's move and return, and the switches between IDLE and EXEC, the check waits for the robot itself, so the dashboard shows no Skip. In the terminal, Ctrl-C there ends the step with the SKIP *skipped by the user (Ctrl-C)*; the step's results so far are not kept, and the run and its report go on. The check then puts the robot back in IDLE: from EXEC the arm first brakes along its path to rest. A command that was still running is cancelled, and the robot then refuses new moves until errors are cleared: press **Clear Errors** before you run stage 5 again.

## What each check looks at

### Each joint: how far, friction, holding `S5.joints`

**The turn.** A normal joint move (`move_joints`) of this joint alone, from where the arm stands to `<deg>` further and back, at `speed` 10 % (of the joint's EXEC speed limit). Before it moves, the robot checks the joint limits, the safety zones and the self-collision check. A refusal before moving, with one of the codes `JOINT_LIMIT`, `SELF_COLLISION`, `ZONE_LIMIT` or `ZONE_CHECK_UNAVAILABLE`, makes the check try the other way; refused both ways, the joint is a SKIP. Any other failure of a move ends the step with a FAIL. Each leg may take up to **60 s**; a leg that has not finished by then is stopped, and the step ends with a FAIL (code `TIMEOUT`).

**How far.** Your answer. A wrong gear ratio in the robot XML or a wrong encoder setting in the drive turns the joint clearly more or less than commanded; a coupling that slips can leave the joint standing while its motor turns.

**Friction.** While each leg runs, the check reads the joint's speed and its external-torque estimate from the robot's shared memory, about every 0.05 s. The external-torque estimate is the measured torque minus the robot's model, so friction above the robot XML's friction model reads positive in the direction of motion.

- Only the steady part of each leg counts: the readings at **70 %** or more of that leg's top speed. With fewer than **5** such readings in either leg, the friction is not measured.
- Per leg, the check takes the mean of the torque times the sign of the speed, and the mean speed. The friction above the model is the average of the two legs. Both legs pass the same poses, in opposite directions, so an error of the gravity model cancels out and what stays is friction the model lacks.
- The model's friction at that speed is `<friction_coulomb_nm>` + `<friction_viscous_nm_s>` × speed (rad/s), from the robot XML; its load term is not used here.
- **WARN** when the friction above the model is more than **max(50 % of the model's friction, 0.1 Nm)**. Never a FAIL: the model's values were measured on one arm.

**The hold.** After the turn the joint holds still for **2 s**. Any new `J<n>:HOLD_OSCILLATION_WARNING` since the step began is a WARN, whichever joint it names. The robot raises that warning when a still joint's motor current ripples at more than 25 Hz for 1.5 s. Each warning is reported once per step.

**The results of one joint**, in this order: the answer about how far (a FAIL unless **about that**), the friction (a WARN or nothing), one WARN per new hold warning. With none of them, the joint gets one PASS. When there is a FAIL or WARN and the friction could not be measured, an INFO says so.

**PAR6's values** (`robots/PAR6.xml`): `<first_run_move scale_deg>` per joint, and the friction model the measurement is compared with.

| Joint | Order | Turn | The question calls it | `<friction_coulomb_nm>` | `<friction_viscous_nm_s>` |
|---|---|---|---|---|---|
| J1 | 4th | 45 deg | half of a right angle | 0.190 Nm | 0.051 Nm·s/rad |
| J2 | 6th | 30 deg | a third of a right angle | 0.609 Nm | 0.658 Nm·s/rad |
| J3 | 5th | 30 deg | a third of a right angle | 0.541 Nm | 0.227 Nm·s/rad |
| J4 | 3rd | 90 deg | a quarter turn | 0.190 Nm | 0.086 Nm·s/rad |
| J5 | 2nd | 45 deg | half of a right angle | 0.093 Nm | 0.064 Nm·s/rad |
| J6 | 1st | 90 deg | a quarter turn | 0.109 Nm | 0.025 Nm·s/rad |

A `scale_deg` that is missing or not a positive number skips that joint's turn. The question names 30, 45, 90 and 180 deg in words (180: half a turn); any other value is shown in degrees.

### The gripper `S5.gripper`

Only with a gripper on CAN. The gripper closes (`close_gripper`) and the check waits up to **30 s** for the robot to report the move settled; you then say whether the jaws closed fully. The same for opening (`open_gripper`). The robot's report says only that the move finished, not where the jaws are: your answer is the check. A move the robot reports as failed (with its code) is a FAIL, and so is one that has not finished after **30 s**: the check then sends a Stop, which holds the jaws where they are. After a FAIL of the close the gripper is not opened. After a passing step the jaws are left open.

### A stop mid-move `S5.stop`

J1 starts a normal joint move of **15 deg** at 10 % speed. **0.6 s** after the move was sent, the check stops it (`stop`), reads the robot's mode and J1's angle at once, waits **1 s** and reads J1's angle again. Then J1 moves back to its start (up to **60 s**). When you skip the 1 s hold, the step ends there with a SKIP: nothing after the stop is judged, and J1 is not moved back.

| Check | Rule |
|---|---|
| The stop came in time | the move finished within 0.6 s → WARN: the stop was not tested. |
| No room | refused the + way before moving (`JOINT_LIMIT`, `SELF_COLLISION`, `ZONE_LIMIT`, `ZONE_CHECK_UNAVAILABLE`) → the - way; any other refusal, or a refusal of the - way → SKIP. |
| Holding in EXEC | the robot is not in EXEC right after the stop → FAIL. |
| Holding still | J1 moved more than **0.5 deg** in the 1 s after the stop → FAIL. |
| Stopped short | J1 had already turned **14.5 deg** or more (within 0.5 deg of its target) → WARN: the stop came too late to show. |
| Moving at all | J1 had turned less than **0.5 deg** when the stop came → WARN: the stop was not tested. |
| Nothing above | PASS. |
| The way back | the return move failed or did not finish in 60 s → an extra WARN. |

## Expected results

A correctly built PAR6 with its gripper on CAN gives:

- **PASS** `<name>: turned <way><deg> deg as commanded; friction <friction> Nm (reference <reference>); held quietly` — one per joint, J6, J5, J4, J1, J3, J2; `<way>` normally `+`.
- **PASS** `the jaws close`
- **PASS** `the jaws open`
- **PASS** `J1 stopped after <moved> of 15 deg and held (drift <drift> deg)` — `<moved>` at least 0.5 and under 14.5, `<drift>` at most 0.5.

## Troubleshooting

In the tables, `<name>` is the joint (J1 to J6), `<deg>` its turn from `<first_run_move scale_deg>`, `<looks like>` the turn in words, `<way>` `+` or `-`, `<friction>` the friction measured (the model's friction plus what is above it) and `<reference>` the model's friction at the measured speed (Nm), `<code>` and `<message>` the robot's failure code and text, `<mode>` the robot's mode and `<reason>` the robot's own words.

### Each joint: how far, friction, holding `S5.joints`

| Result | What it means | What to check |
|---|---|---|
| **PASS** `<name>: turned <way><deg> deg as commanded; friction <friction> Nm (reference <reference>); held quietly` | You saw the commanded turn, the friction was within the limit and no hold warning came. | — |
| **PASS** `<name>: turned <way><deg> deg as commanded; friction not measured; held quietly` | As above, but the friction could not be measured: fewer than 5 steady readings in a leg, or no shared memory (the check not run on the robot's Pi). | — |
| **FAIL** `<name> turned clearly LESS than the <deg> deg commanded` | You answered **clearly less (half or less)**. Expected: `<deg> deg (<looks like>)`. | `<name>`'s gear ratio in the robot XML does not match its gearbox<br>the drive's encoder setting (its resolution)<br>a belt or coupling that slips under load |
| **FAIL** `<name> turned clearly MORE than the <deg> deg commanded` | You answered **clearly more (double or more)**. Expected: `<deg> deg (<looks like>)`. | `<name>`'s gear ratio in the robot XML does not match its gearbox<br>the drive's encoder setting (its resolution) |
| **FAIL** `<name> was commanded <way><deg> deg but did not move` | You answered **I saw no movement**. | the motor turns but the joint does not: the coupling between motor and gearbox, a belt, a grub screw |
| **WARN** `<name> needs about <friction> Nm to turn; the robot XML's friction model says <reference> Nm` | The friction above the model is more than max(50 % of the model, 0.1 Nm). Expected: `about <reference> Nm`. | a belt or gearbox too tight, a bearing, a cable pulling on the joint<br>the model was measured on one arm: a new gearbox can run stiffer for its first hours |
| **WARN** `<joint> buzzed while holding (its motor current ripples)` | A new hold warning (`<joint>:HOLD_OSCILLATION_WARNING`) came during this joint's turn or hold. `<joint>` can be another joint than the one turned. | the joint's gains (the dashboard's PID Config): too high for this arm<br>the encoder's magnet on the motor shaft: loose or too far from the drive |
| **INFO** `<name>: friction not measured (too few readings while it moved)` | Comes with a FAIL or WARN of the same joint: the friction could not be measured (fewer than 5 steady readings in a leg, or no shared memory). | — |
| **FAIL** `a move did not finish (<code>): <message>` | A turn failed after the robot accepted it, or was refused with a code other than the four that make the check try the other way, or the way back failed, or a leg did not finish within 60 s (`TIMEOUT`: *the move did not finish within 60 s*; the check stopped it). The step ends here: the joints after it are not turned. | an error stopped it: the dashboard's Errors tab names it (a collision, a limit, a drive fault)<br>clear the errors, then run stage 5 again |
| **SKIP** `<name>: the robot refused its turn both ways (+: <message>; -: <message>)` | The robot refused the turn both ways before moving (a joint limit, a safety zone, the arm against itself, or the zone check unavailable). | The arm's pose: move it so the joint has `<deg>` of room one way, then run stage 5 again. |
| **SKIP** `<name>: no <first_run_move scale_deg> in the robot XML — its turn is not defined` | The joint's `<first_run_move>` has no `scale_deg`, or it is not a positive number. | Add `scale_deg` to the joint's `<first_run_move>` (see PAR6's values above). |
| **SKIP** `<name>: skipped by the user` | You answered **skip this joint**. | — |
| **SKIP** `<name>: skipped by the user (its move stopped where it was)` | You skipped (Skip, Ctrl-C) while the joint turned or held. The joint stopped where it was and was not turned back. | — |

### The gripper `S5.gripper`

| Result | What it means | What to check |
|---|---|---|
| **PASS** `the jaws close` | The robot reported the close finished and you saw the jaws close fully. | — |
| **PASS** `the jaws open` | The robot reported the opening finished and you saw the jaws open fully. | — |
| **FAIL** `the jaws did not close fully (the robot says the move finished)` | You answered **no** after the close. The check still opens the gripper. | something between the jaws, or the jaws binding on their rail<br>the gripper XML's open / closed positions for this gripper |
| **FAIL** `the jaws did not open fully (the robot says the move finished)` | You answered **no** after the opening. | something between the jaws, or the jaws binding on their rail<br>the gripper XML's open / closed positions for this gripper |
| **FAIL** `the gripper did not close (<code>): <message>` | The robot reported the close as failed, for example with `GRIPPER_SETTLE_TIMEOUT`. The gripper is not opened. | the jaws move freely, nothing between them<br>the gripper's power and CAN cable; its calibration (homing does it) |
| **FAIL** `the gripper did not open (<code>): <message>` | The robot reported the opening as failed. | the jaws move freely, nothing between them<br>the gripper's power and CAN cable; its calibration (homing does it) |
| **FAIL** `the gripper did not finish its close within 30 s (stopped)` | The close had not finished after 30 s. The check sent a Stop, which holds the jaws where they are; the gripper is not opened. | the jaws move freely, nothing between them<br>the gripper's power and CAN cable; its calibration (homing does it) |
| **FAIL** `the gripper did not finish its open within 30 s (stopped)` | The opening had not finished after 30 s. The check sent a Stop, which holds the jaws where they are. | the jaws move freely, nothing between them<br>the gripper's power and CAN cable; its calibration (homing does it) |
| **SKIP** `no gripper on CAN (stage 0's configuration)` | The configuration has no gripper on CAN, so there is nothing to test. | — |

### A stop mid-move `S5.stop`

| Result | What it means | What to check |
|---|---|---|
| **PASS** `J1 stopped after <moved> of 15 deg and held (drift <drift> deg)` | After the stop the robot was in EXEC, J1 had turned at least 0.5 and less than 14.5 deg, and it drifted at most 0.5 deg in 1 s. | — |
| **FAIL** `after the stop the robot is in <mode>, not holding in EXEC` | Right after the stop the robot was not in EXEC. | the dashboard's Errors tab: an error latched with the stop |
| **FAIL** `J1 drifted <drift> deg after the stop` | J1 moved more than 0.5 deg in the 1 s after the stop. | a load the joint cannot hold, or a slipping coupling / belt |
| **WARN** `J1 reached its target (<moved> deg) — the stop came too late to show` | J1 had turned 14.5 deg or more when it stopped, so the test cannot show that it stopped short. | No hint from the check: the stop came 0.6 s after the move was sent. |
| **WARN** `J1 had moved only <moved> deg when the stop came — the stop was not tested` | J1 had turned less than 0.5 deg when the stop came, so the test cannot show that it stops. | the move started late (the robot was busy planning), or it was refused: the dashboard's Errors / Activity Log tab |
| **SKIP** `J1 stopped after <moved> of 15 deg; the hold after it was skipped by the user (J1 stays where it stopped)` | You skipped (Skip, Ctrl-C, or **Stop the run**) during the 1 s hold after the stop. The mode and the drift are not judged, and J1 is not moved back. | — |
| **WARN** `J1's move finished before the stop could come — the stop was not tested` | J1's whole move finished within 0.6 s. | the arm's EXEC speed limits are high: this check's STOP_AFTER_S is too long |
| **WARN** `J1 did not return to where it started: <error>` | Comes after the stop's own result: the move back failed (`<error>` is the robot's failure) or did not finish within 60 s. J1 stays where it stopped. | — |
| **SKIP** `J1's move was not possible (<code>): <message>` | The robot refused J1's move, or it failed within the first 0.6 s: with a code other than the four that make the check try the other way, or on the - way after the + way was refused. | The arm's pose: J1 needs 15 deg of room one way. |

### Any step of this stage

| Result | What it means | What to check |
|---|---|---|
| **SKIP** `needs a homed arm (stage 4)` | The arm is not homed. | Run stage 4 (Step 5) until it passes. |
| **SKIP** `needs IDLE (the robot is in <mode>: clear its errors first)` | The robot was in neither IDLE nor EXEC when the step began, for example in ACTIVE_ERROR. | Clear the errors in the dashboard, then run stage 5 again. |
| **SKIP** `not started (the user's choice)` | You answered **skip** at the step's question. | — |
| **SKIP** `another client holds control (<reason>) — the dashboard keeps it ~5 s after its last command: wait, or release it there, then run this step again` | Another client still held control of the robot after 15 s. | Wait 5 s after your last click in the dashboard, or release control there, then run stage 5 again. |
| **SKIP** `the robot refused EXEC mode: <reason>` | The robot refused to enter EXEC, so nothing moved. | Read `<reason>`. |
| **SKIP** `the arm stayed disabled (this step needs it enabled)` | The arm was not enabled within 180 s. | Press **Enable** in the dashboard while the check waits. |
| **SKIP** `no connection to the robot (S0's 'Robot service' step)` | The check has no connection to the robot. | The robot service step of stage 0 (Step 1). |
| **SKIP** `skipped by the user` | You skipped the wait for **Enable** or the wait for control. Nothing moved. | — |
| **SKIP** `skipped by the user (Ctrl-C)` | In the terminal: Ctrl-C while the check waited for the robot itself (the gripper's moves, J1's move and return, the switches between IDLE and EXEC). The step's results so far are not kept, and the robot is put back in IDLE. If a command was still running, it is cancelled and new moves are refused until errors are cleared. | Press **Clear Errors** in the dashboard before you run stage 5 again. |
| **SKIP** `the run was stopped here` | The run was stopped (**Stop the run**, or Ctrl-C at a question). In the joints and the gripper steps the results so far are kept before this line. | — |
| **FAIL** `the check itself failed: <error>` | The check's own code failed. The report holds its traceback. | this is a fault of the check, not necessarily of the robot — send the report |

## What's next

The run is complete. Read [the report and the support bundle](first-run-check.md#the-report-and-the-support-bundle) for what the check wrote and how to ask for help with it.
