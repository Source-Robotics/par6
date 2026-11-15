---
status: new
---

# Step 4: Joint test moves

Stage 3 of [the first-run check](first-run-check.md) is the first time the motors move the arm. One joint at a time, the wrist first, each joint moves a few degrees away from where it stands and back: on PAR6 5 degrees (J4 and J6: 10 degrees) at a peak speed of 5 deg/s, with its drive's current limited to a test value between 400 and 1500 mA while every other joint holds still. You then say which way the joint moved first. This shows, before the arm is homed, that each motor drives its joint, that the joint turns the way the robot's model calls positive, that the coupling between motor and joint holds, and that the joint moves freely. The move is made in the drive's own encoder count, which needs no home reference, so it works on an arm that is not homed yet. If you are not ready to power an unhomed arm, the stage can instead free each joint in turn for you to turn by hand: see [By hand instead](#by-hand-instead).

!!! danger "Danger"
    The arm moves under motor power each time you answer **go**: one joint, a few degrees out and back.

    A hand or a cable near the moving joint can be caught, and a joint that is wired wrong moves the opposite way to the one you expect.

    - Clear the space around the arm and keep a hand on the E-stop, as the check asks before the first move.
    - Keep your hands off the arm while a joint moves; watch from outside its reach.
    - **Skip**, Ctrl-C and **Stop the run** stop the check's test move, but they are not emergency stops. To stop the arm at once, press the E-stop or **Disable** in the dashboard.

**Prerequisites**

- Steps 1 to 3 done without a FAIL. The E-stop must work (Step 3) before anything moves.
- The arm ENABLED. When it is DISABLED, the check asks *The arm is DISABLED. Clear the space around it, then press Enable in the dashboard (it holds where it is; nothing moves yet) — waiting for the arm to be enabled* and waits up to 180 s; after that the step is skipped. It never enables the arm itself.
- The robot in IDLE: no error latched (clear errors first) and no other mode. Homed or not does not matter.
- Control of the robot free. The check takes control before the first move; the dashboard keeps it for 5 s after your last click there (the Enable click too), and the check waits up to 15 s for it.
- A `<first_run_move>` for each joint in the robot XML. PAR6's file has them ([the values](#small-test-moves-s3moves)); a joint without one is skipped.
- No Hall-sensor check and no freed joint active: the robot refuses a test move beside either.

## Procedure

**In the dashboard:** open the **First run** tab, tick **3 Small test moves** (untick the stages you do not want to run), leave **Stage 3 by hand** off, and press **Start**.

**In a terminal** on the robot's Raspberry Pi:

```bash
cd ~/Desktop/RCB-Runtime && .venv/bin/python3 tools/first_run.py --stages 3
```

Without stage 0 in the list, stage 0's configuration and robot-service checks still run first: this stage needs them.

The stage begins with *Stage 3: Small test moves* and the line *The arm ENABLED, homed or not: each joint moves a few degrees and back, slowly, its force limited, the others holding; you say which way it went. (--by-hand: you turn each joint yourself instead.)* Then:

1. If the arm is DISABLED, the check waits up to 180 s for you to press **Enable** (see Prerequisites).
2. If the robot is not in IDLE, the step ends with a SKIP and nothing moves.
3. The check asks: *The robot now moves each joint a few degrees and back, slowly, its force limited — J6 first, J2 last. Clear the space around the arm and keep a hand on the E-stop.*
    - **start**: go on.
    - **skip**: the step ends with a SKIP; nothing moves.
4. The check takes control of the robot. If the dashboard still holds it, the check shows *Another client holds control — the dashboard lets go 5 s after its last click; waiting for it* and waits up to 15 s.
5. Each joint follows, in the order **J6, J5, J4, J1, J3, J2** (the wrist first, the joints carrying the arm last). For each one:
    1. The check asks *`<name>`: moves `<amp>` deg and back at `<speed>` deg/s, its force limited (`<cur>` mA). Go?* — for example *J6: moves 10 deg and back at 5 deg/s, its force limited (400 mA). Go?*
        - **go**: the move starts.
        - **skip this joint**: a SKIP for this joint; the next joint follows.
    2. The joint moves the + way and back while the check shows *`<name>` is moving +`<amp>` deg and back — watch which way it goes FIRST*. The move ramps out smoothly, holds 0.5 s, ramps back and holds 0.5 s: about 4.1 s for a 5 degree joint and 7.3 s for a 10 degree joint. The check waits at most the move's time plus 3 s (about 7.1 s and 10.3 s). Skip (Ctrl-C in the terminal) stops the move at once and skips this joint.
    3. If the joint could not move the + way (at its end, blocked, or the robot refused the move), the check says *`<name>` could not move the + way (at its end, or blocked) — trying the other way* (when the robot refused the move, the brackets read *(refused: `<reason>`)*) and runs the same move the - way, once: *`<name>` is moving -`<amp>` deg and back — watch which way it goes FIRST*.
    4. The check asks *Which way did `<name>` move FIRST?* with three answers: the joint's `<positive_direction>` words from the robot XML (for J6 on PAR6: *the gripper turns counter-clockwise, seen from the elbow looking toward it*), **the other way**, and **I saw no movement**. After a blocked first try the question is *`<name>`'s first try was blocked and stopped at once. In its second try, which way did it move FIRST?* with the same three answers: the second try went the - way first, so a correctly built joint is then answered with **the other way**. When the robot XML has no `<positive_direction>` for the joint, the question is *Did you see `<name>` move?* with **yes** and **I saw no movement**, after one try or two.
    5. The joint's results appear; the next joint follows.
6. After J2 the stage ends. The arm stays ENABLED and in IDLE, each joint back near where it started. If the stage has a FAIL and a later stage is in the run, the check asks *Stage 3 has a FAIL — fix it first (the hints say what to check). Go on to stage `<next>` anyway?* — **no** ends the run, **yes** goes on.

!!! note "Note"
    On a homed arm the robot refuses a test move that would end past the joint's soft limit (*`<name>` would move to `<x>` deg, past its soft limits (`<lo>` to `<hi>` deg) — move it away first*). The check then tries the other way; when both ways are refused, the joint is a SKIP, not a FAIL.

### By hand instead

The by-hand variant replaces the powered test moves: no motor drives a joint. One joint at a time goes limp — its drive's current limit set to 0 — while every other joint does what the robot's IDLE mode makes it do (see [the table](#what-the-other-joints-do)); you turn the limp joint about 30 degrees, and its encoder must count the right way and about as far as you turned. It checks the encoder, the direction and the coupling, but not that the motor can drive the joint (its phase wiring, the drive's calibration): with this variant, the homing in [Step 5](step-5-homing.md) is the first powered motion.

!!! danger "Danger"
    A freed joint has no motor force: J2 and J3 carry the arm's weight, and with the arm DISABLED no joint has any.

    When J2 or J3 is freed, the arm beyond it falls unless you hold it; with the arm DISABLED, the whole arm can fold under its own weight.

    - Before you answer **ready**, read what the question says the other joints do, and hold the arm beyond the joint the check names, as it asks.
    - With the arm DISABLED, support the whole arm, not only the part beyond the freed joint.
    - Keep holding until the check has moved on to its next question: the freed joint gets its motor force back as soon as the turn is read, the wait has run out or you skipped (on a DISABLED arm it stays limp).

**In the dashboard:** tick **3 Small test moves**, switch **Stage 3 by hand (turn each joint yourself, no motor current)** on, and press **Start**. **In a terminal:**

```bash
cd ~/Desktop/RCB-Runtime && .venv/bin/python3 tools/first_run.py --stages 3 --by-hand
```

1. This variant does not wait for the arm to be enabled or disabled: it needs only the connection to the robot, and the robot in IDLE (else a SKIP). What the other joints do then depends on the arm's state (the table below).
2. The check takes control of the robot (waiting up to 15 s for the dashboard, as above). There is no start question: the first joint follows at once.
3. Each joint follows, in the order **J6, J5, J4, J1, J3, J2**. For each one:
    1. *`<name>` next: it goes limp (no motor force); `<others>`. Hold the arm beyond `<name>` so it cannot fall. Ready?* — `<others>` says what every other joint does, read from the robot's state at this question (the table below).
        - **ready**: the joint is freed.
        - **skip this joint**: a SKIP for this joint; the next joint follows.
    2. *Freeing `<name>` ...* — the check waits up to 3 s for the robot to report the joint free. Skip (Ctrl-C) here skips this joint.
    3. *Turn `<name>` by hand about 30 degrees so that `<words>`, then hold it still. (At its end already? Back it off a little first.)* — `<words>` are the joint's `<positive_direction>` words; without them the prompt says *either way (the robot XML has no `<positive_direction>` for it)*. The check waits up to 90 s. The turn counts as done once the joint has moved at least 15 degrees from the furthest point it reached the other way and then stays within 0.5 degrees for 1 s, so backing off an endstop first is fine. Skip (Ctrl-C) skips this joint.
    4. The check ends the free joint: its current limit is put back and it does again what the other joints do — always, also after a skip or when the 90 s ran out.
    5. If no finished turn was read in 90 s: *The robot read no turn of `<name>`. Did you turn it?*
        - **no**: a SKIP, not turned.
        - **yes**: when the reading moved through at least 15 degrees, the joint was turned but never held still for 1 s: a SKIP, not judged. Otherwise a FAIL: the encoder did not follow the turn.
    6. Otherwise: *The robot read `<name>` `<got>` degrees. Is that about what you turned it?* — **yes**, **it read much less** or **it read much more**. This question comes even when the reading was negative (counted backwards).
4. After J2 the stage ends, with the same question about a FAIL as the powered moves.

#### What the other joints do

While one joint is free, every other joint does what the robot's IDLE mode makes it do. The question before each joint says which case applies, in these words:

| The arm when the question is asked | `<others>` in the question | Every other joint |
|---|---|---|
| ENABLED and not homed, or homed with gravity compensation off | *every other joint keeps holding* | holds still |
| ENABLED, homed, gravity compensation on | *every other joint floats, weightless (freedrive: the arm is homed, gravity compensation on)* | carries its own weight but can be moved by hand |
| DISABLED | *the arm is DISABLED, so every other joint is limp too* | limp: no motor force |

!!! note "Note"
    The robot puts a freed joint's current limit back by itself after 2 minutes, and before any mode change (homing, a jog, an error, the E-stop): a check that dies mid-turn never leaves a joint freed.

## What each check looks at

### Small test moves `S3.moves`

**The test move.** The check asks the robot for a test move of one joint (`robot.joint_test`). The joint moves `<amp>` degrees away from where it stands and back on a smooth (cosine) ramp whose peak speed is `<speed>`, holding 0.5 s at each end. It runs in position mode in the drive's own encoder count, converted with the joint's gear ratio, encoder resolution and `<dir>`, so the + way is the + way of the robot's model. Meanwhile the joint's drive current limit is lowered to the test current `<cur>`, and every other joint holds still. The robot accepts an amplitude above 0 and up to 15 deg, a speed above 0 and up to 10 deg/s, and a current above 0 and up to the joint's own current limit, and only in IDLE with the arm ENABLED.

**When the robot stops it by itself.** At once, with the joint's normal limits and command back in the same control tick:

- when the joint falls more than **2 deg** behind the commanded motion (state *fell_behind*): blocked, at an endstop, too little current, or a motor that does not follow;
- when the robot leaves IDLE, the arm is disabled, or any mode change is asked for (homing, a jog, an error, the E-stop) (state *stopped*);
- when the check stops it (a skip, or no result in time).

**What the robot measures** for each move: how far the joint got the commanded way (`<moved>`, the largest displacement, deg), the largest tracking error (`<err>`, deg), the peak motor current (`<peak>`, mA) and where it ended against its start (`<end>`, deg).

**The rules**, in the order the check applies them:

| Check | Rule |
|---|---|
| Stopped by the robot | state *stopped* → SKIP: the move was interrupted, so nothing is judged. |
| Blocked the + way | no result within the move's time + 3 s, or *fell_behind*, or moved less than **50 %** of `<amp>`, or the robot refused the move → tried the - way once. |
| Blocked both ways | refused both ways → SKIP (the robot's state, not the build); otherwise → FAIL. |
| Coupling | you saw no movement → FAIL (the encoder moved, so the motor turned but the joint did not). No further checks for that joint. |
| Direction | your answer is not the direction of the move that ran (+: the `<positive_direction>` words; -: **the other way**) → FAIL. |
| Effort | `<peak>` at or above **85 %** of `<cur>` → WARN. |
| Following | `<err>` above **1.0 deg** (but under the 2 deg stop) → WARN. |
| Return | `<end>` further than **0.5 deg** from the start → WARN. |
| Nothing above | PASS, or INFO when the robot XML has no `<positive_direction>` (the direction is not judged). |

A joint can give several results: a FAIL for the direction together with WARNs. PASS (or INFO) comes only when there is no FAIL and no WARN.

**PAR6's test moves** (`robots/PAR6.xml`, `<first_run_move amplitude_deg speed_dps current_ma>` per joint). The XML's note sizes each test current at 1.5 times the joint's worst gravity torque over its range.

| Joint | Order | Amplitude | Peak speed | Test current | Blocked below | WARN current at | Move time | Wait limit |
|---|---|---|---|---|---|---|---|---|
| J1 | 4th | 5 deg | 5 deg/s | 600 mA | 2.5 deg | 510 mA | about 4.1 s | about 7.1 s |
| J2 | 6th | 5 deg | 5 deg/s | 1500 mA | 2.5 deg | 1275 mA | about 4.1 s | about 7.1 s |
| J3 | 5th | 5 deg | 5 deg/s | 800 mA | 2.5 deg | 680 mA | about 4.1 s | about 7.1 s |
| J4 | 3rd | 10 deg | 5 deg/s | 600 mA | 5 deg | 510 mA | about 7.3 s | about 10.3 s |
| J5 | 2nd | 5 deg | 5 deg/s | 600 mA | 2.5 deg | 510 mA | about 4.1 s | about 7.1 s |
| J6 | 1st | 10 deg | 5 deg/s | 400 mA | 5 deg | 340 mA | about 7.3 s | about 10.3 s |

The positive direction of each PAR6 joint (`<positive_direction>`, the first answer of the direction question):

| Joint | + means |
|---|---|
| J1 | the whole arm turns counter-clockwise, seen from above |
| J2 | the upper arm leans forward (toward where the arm reaches when parked) and the gripper goes down |
| J3 | the elbow opens: the forearm swings away from the upper arm (with the arm parked: the forearm lifts) |
| J4 | the forearm rolls counter-clockwise, seen from the elbow looking toward the gripper |
| J5 | the wrist bends so the gripper tips up (with the arm parked) |
| J6 | the gripper turns counter-clockwise, seen from the elbow looking toward it |

A `<first_run_move>` with a missing amplitude, speed or current, or one that is not a positive number, counts as missing: the check skips that joint rather than guess a force.

### Each joint by hand `S3.by_hand`

**Freeing a joint** (`robot.free_joint`): the joint's drive gets a current limit of 0, so the joint makes no torque while its encoder keeps counting; every other joint keeps its normal command and limits, so it does what IDLE makes it do ([the three cases](#what-the-other-joints-do)). The robot frees a joint only in IDLE, never beside the Hall-sensor check, and puts its current limit back on its own before any mode change, on leaving IDLE, and after 2 minutes without the command again.

**The turn.** You are asked for about **30 deg**. The check reads the joint's angle every 0.1 s and accepts the turn once the joint is at least **15 deg** from the furthest point it reached the other way and has stayed within **0.5 deg** for **1 s**. The reading `<got>` is that distance, + when the joint ended above the lowest angle it reached, - when below the highest. It waits up to **90 s**.

| Check | Rule |
|---|---|
| Counting at all | no accepted turn in 90 s and you say you did not turn it → SKIP. You say you turned it: the reading moved through less than 15 deg → FAIL; 15 deg or more, but never held still for 1 s → SKIP (not judged). |
| Direction | `<got>` negative while the joint has `<positive_direction>` words → FAIL (it counts backwards). |
| Amount | you answer **it read much less** or **it read much more** → FAIL. |
| Nothing above | PASS, or INFO when there are no `<positive_direction>` words (the direction is not judged). |

## Expected results

A correctly built PAR6 gives one PASS per joint, in the order J6, J5, J4, J1, J3, J2:

- **PASS** `<name>: moved <moved> deg the <way> way and back, peak <peak> of <cur> mA, within <err> deg` — `<moved>` close to the amplitude (for example `+10.0` for J6), `<way>` normally `+`, `<err>` at most 1 deg.

`<way>` is `-` when the + way was blocked (a joint at its end) and the - way passed.

By hand, one PASS per joint:

- **PASS** `<name>: counts the + way, <got> deg read, about what was turned` — `<got>` positive and close to what you turned (about `+30`).

## Troubleshooting

In the tables, `<name>` is the joint (J1 to J6), `<amp>` its test amplitude and `<cur>` its test current from `<first_run_move>`, `<moved>` how far it got the commanded way, `<err>` how far it fell behind at most, `<peak>` the peak motor current, `<end>` where it ended against its start, `<way>` `+` or `-`, `<words>` the joint's `<positive_direction>` words, `<got>` the angle read by hand, `<mode>` the robot's mode and `<reason>` the robot's own words.

### Small test moves `S3.moves`

| Result | What it means | What to check |
|---|---|---|
| **PASS** `<name>: moved <moved> deg the <way> way and back, peak <peak> of <cur> mA, within <err> deg` | The joint followed, moved the way you saw, needed under 85 % of the test current, stayed within 1 deg and came back within 0.5 deg. | — |
| **INFO** `<name>: moved <moved> deg the <way> way and back (direction not judged: no <positive_direction>), peak <peak> of <cur> mA, within <err> deg` | As PASS, but the robot XML has no `<positive_direction>` for this joint, so you were only asked whether it moved. | Add the joint's `<positive_direction>` words to the robot XML to have the direction checked. |
| **FAIL** `<name> moves BACKWARDS: commanded <way><amp> deg, seen the opposite` | You saw the joint move the opposite way to the one the robot commanded. Expected: the `<positive_direction>` words (for a + move) or `the opposite of: <words>` (for a - move). | `<name>`'s `<dir>` in the robot XML has the wrong value (0 <-> 1) — fix it and restart the robot service<br>or the words in `<name>`'s `<positive_direction>` do not match this arm — fix those instead (the kinematic model decides which way + is) |
| **FAIL** `<name>: the encoder read <moved> deg but the joint did not move` | The motor's encoder moved, but you saw no movement of the joint. | the motor turns but the joint does not: the coupling between motor and gearbox, a belt, a loose grub screw |
| **FAIL** `<name> did not follow its test move either way (moved <moved> deg of <amp>, behind up to <err> deg)` | Both moves were blocked: neither got to half the amplitude, or the joint fell 2 deg behind. The numbers are the - move's. Expected: `<amp> deg each way`. | the motor's wiring: its phase wires / connector to the drive<br>the drive's motor calibration (the drive's configuration tool)<br>the joint blocked: something in the way, a cable caught, the joint against its endstop both ways<br>the test current too low for this joint's load: `<first_run_move current_ma>` in the robot XML |
| **FAIL** `<name> did not follow its test move the + way, and the robot refused the other way: <reason> (moved <moved> deg of <amp>, behind up to <err> deg)` | The + move ran and was blocked; the robot refused the - move (for example past a soft limit on a homed arm). The numbers are the + move's. | The same four hints as above. Also read `<reason>`. |
| **FAIL** `<name> did not follow its test move the - way, and the robot refused the other way: <reason> (moved <moved> deg of <amp>, behind up to <err> deg)` | The robot refused the + move; the - move ran and was blocked. The numbers are the - move's. | The same four hints as above. Also read `<reason>`. |
| **WARN** `<name> needed <peak> of its <cur> mA test current` | The peak current was at or above 85 % of the test current. | binding: a belt or gearbox too tight, a bearing, a cable pulling<br>or a heavy load at this pose (the test current is 1.5 x its worst gravity torque) |
| **WARN** `<name> fell up to <err> deg behind its test move` | The joint lagged more than 1.0 deg behind the commanded motion, but not more than the 2 deg that stops it. | the joint's gains (the dashboard's Tune Joint), or friction / binding |
| **WARN** `<name> ended <end> deg from where it started` | After the move the joint was more than 0.5 deg away from its start. | it sagged or slipped while held: a load the test current cannot hold, or a slipping coupling |
| **SKIP** `<name>: the robot refused its test move both ways: <reason>` | The robot refused both moves, so nothing was tested. Two different reasons are joined with `; `. | The robot's state, not the build. The robot's reasons include: *only in IDLE (homed or not)*; *the arm is disabled: enable it first (a test move is powered motion)*; *RTI is still configuring the drives (the first ~1.2 s after its start)*; *the Hall sensor check or a freed joint is active — stop it first*; *amplitude 0-15 deg, speed 0-10 deg/s, current up to the joint's limit (`<limit>` mA)*; *`<name>` would move to `<x>` deg, past its soft limits (`<lo>` to `<hi>` deg) — move it away first*; *no position read from `<name>` yet — try again*. A test current above the joint's current limit is refused before the robot is asked: *joint_test: amplitude 0-15 deg, speed 0-10 deg/s, current up to J`<n>`'s limit (`<limit>` mA)*. |
| **SKIP** `<name>: the test move was stopped (the arm disabled, an error, a mode change)` | The robot stopped the move itself, on the + or the - way: the arm was disabled, an error latched (the E-stop too), or a mode change was asked for. | The dashboard's Errors tab; clear the errors, enable the arm and run stage 3 again. |
| **SKIP** `<name>: no <first_run_move> in the robot XML — its test move is not defined` | The joint has no `<first_run_move>`, or its amplitude, speed or current is missing or not a positive number. The check never guesses a force. | Add `<first_run_move amplitude_deg speed_dps current_ma>` to the joint in the robot XML (see PAR6's values above). |
| **SKIP** `<name>: skipped by the user` | You answered **skip this joint**. | — |
| **SKIP** `<name>: skipped by the user (its test move stopped)` | You skipped (Skip, Ctrl-C) while the joint moved; the move was stopped at once. | — |
| **SKIP** `not started (the user's choice)` | You answered **skip** at the first question. Nothing moved. | — |
| **SKIP** `needs IDLE (the robot is in <mode>: clear its errors first)` | The robot was not in IDLE when the step began, for example in ACTIVE_ERROR with an error latched. Nothing moved. | Clear the errors in the dashboard, then run stage 3 again. |
| **SKIP** `another client holds control (<reason>) — the dashboard keeps it ~5 s after its last command: wait, or release it there, then run this step again` | Another client still held control of the robot after 15 s. Nothing moved. | Wait 5 s after your last click in the dashboard, or release control there, then run stage 3 again. |

### Each joint by hand `S3.by_hand`

| Result | What it means | What to check |
|---|---|---|
| **PASS** `<name>: counts the + way, <got> deg read, about what was turned` | The encoder counted the + way, and you confirmed the amount. | — |
| **INFO** `<name>: counts (direction not judged), <got> deg read, about what was turned` | The encoder counted and you confirmed the amount; the robot XML has no `<positive_direction>` for the joint, so the direction is not judged. | Add the joint's `<positive_direction>` words to the robot XML to have the direction checked. |
| **FAIL** `<name> counts BACKWARDS: turned so that <words>, the robot read <got> deg` | You turned the joint the + way and the reading was negative. Expected: `a + reading`. | `<name>`'s `<dir>` in the robot XML has the wrong value (0 <-> 1) — fix it and restart the robot service<br>or the words in `<name>`'s `<positive_direction>` do not match this arm — fix those instead (the kinematic model decides which way + is) |
| **FAIL** `<name> turned by hand but the encoder read only <seen> deg` | No finished turn in 90 s, you said you turned it, and the reading moved through less than 15 deg in all (`<seen>`). Expected: `>= 15 deg`. | the motor does not turn with the joint: the coupling between motor and gearbox, a belt, a loose grub screw<br>the encoder: its magnet on the motor shaft, the drive's encoder setting |
| **SKIP** `<name>: read a turn of <seen> deg, but it never held still for 1 s — not judged` | No finished turn in 90 s and you said you turned it: the reading moved through 15 deg or more (`<seen>`), but the joint never stayed within 0.5 deg for 1 s, so the turn was not judged. | turn it, then hold it still for a second; run this stage again |
| **FAIL** `<name>: read <got> deg, the user turned it clearly further` | You answered **it read much less**. `<got>` is shown without its sign. | the motor turns less than the joint: the coupling or a belt slips<br>the robot XML's gear ratio or encoder bits for `<name>` too small |
| **FAIL** `<name>: read <got> deg, the user turned it clearly less` | You answered **it read much more**. `<got>` is shown without its sign. | the robot XML's gear ratio or encoder bits for `<name>` too large |
| **FAIL** `<name>: the robot did not free it` | The robot did not report the joint free within 3 s. | logs/RTI.log says why (IDLE only) |
| **SKIP** `<name>: the robot refused to free it: <reason>` | The robot refused to free the joint, so it was not checked. | The robot's reasons: *only in IDLE (enabled or not, homed or not)*; *RTI is still configuring the drives (the first ~1.2 s after its start)*; *the Hall sensor check is running — stop it first*. |
| **SKIP** `<name>: not turned` | No turn was read and you answered **no** to *Did you turn it?* | — |
| **SKIP** `<name>: skipped by the user` | You answered **skip this joint**, or skipped (Skip, Ctrl-C) while the check freed the joint or waited for your turn. The joint gets its current limit back, and the next joint follows. | — |
| **SKIP** `needs IDLE (the robot is in <mode>: clear its errors first)` | The robot was not in IDLE when the step began. | Clear the errors in the dashboard, then run stage 3 again. |
| **SKIP** `another client holds control (<reason>) — the dashboard keeps it ~5 s after its last command: wait, or release it there, then run this step again` | Another client still held control of the robot after 15 s. | Wait 5 s after your last click in the dashboard, or release control there, then run stage 3 again. |

### Any step of this stage

| Result | What it means | What to check |
|---|---|---|
| **SKIP** `the arm stayed disabled (this step needs it enabled)` | The powered moves only: the arm was not enabled within 180 s. | Press **Enable** in the dashboard while the check waits. |
| **SKIP** `no connection to the robot (S0's 'Robot service' step)` | The check has no connection to the robot. | The robot service step of stage 0 (Step 1). |
| **SKIP** `skipped by the user` | You skipped a wait that belongs to the step as a whole: the wait for **Enable** (powered moves only) or the wait for control. Nothing was checked yet. | — |
| **SKIP** `skipped by the user (Ctrl-C)` | In the terminal: Ctrl-C while the check was working on its own, outside a wait or a question (for example while it sent a command). The step ends here; its results so far are not kept. | — |
| **SKIP** `the run was stopped here` | The run was stopped (**Stop the run**, or Ctrl-C at a question). The results of the joints already checked are kept before this line. | — |
| **FAIL** `the check itself failed: <error>` | The check's own code failed. The report holds its traceback. | this is a fault of the check, not necessarily of the robot — send the report |

## What's next

Continue with [Step 5: The first homing](step-5-homing.md).
