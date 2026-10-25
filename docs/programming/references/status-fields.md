---
status: new
---

# Status fields

What the robot reports about itself, field by field: the status stream that `latest_status()` reads, and the answers
of `get_status()`, `get_health()`, `get_hardware()` and `get_versions()`.

## The status stream

The robot sends its status to every connected client whenever a field changes, checked 50 times a second.
`latest_status()` returns the newest one the client received, without asking the robot.

| Field | Meaning | Unit or values |
|---|---|---|
| `type` | Always `"status"`. | text |
| `runtime_version` | The robot software's version. | text, such as `"0.10.0"`; `"unknown"` if it cannot be read |
| `protocols` | The protocol versions: `commands`, `rti`, `telemetry`. | whole numbers |
| `control_holder` | The client that holds control, by its address as the robot sees it. | `"ip:port"`, or `None` |
| `force_confirm` | A forced takeover needs a button press at the control box. | true / false |
| `force_confirm_pending` | A forced takeover is waiting for that button press now. | true / false |
| `mode` | The robot's mode. | `BOOTING`, `IDLE`, `ACTIVE_ERROR`, `HOMING`, `JOG`, `RTI`, `SOFT_RTI`, `EXEC`, `HAND_GUIDING`, `IMPEDANCE`, `SAFETY_STOP`, `FLASHING` |
| `state` | Whether the robot is enabled. | `ENABLED`, `DISABLED` |
| `homed` | The arm is homed. | true / false |
| `err` | An error is latched (warnings do not count). | 1 / 0 |
| `errors` | Every latched error and warning, by key, such as `"J3:WATCHDOG"`. | list of text |
| `error_details` | Each latched key with its `key`, `number`, `title`, `level` and `since`. | list; `since` in seconds since 1970 |
| `motion_aborted` | The failure that aborted the program: `cid`, `code`, `message`. | or `None` |
| `safety` | A safety-monitor error is latched. | 1 / 0 |
| `estop` | The software E-stop is on. | 1 / 0 |
| `exec_paused` | The EXEC program is paused. | 1 / 0 |
| `exec_settling` | EXEC waits for the arm to settle at the end of a move. | 1 / 0 |
| `exec_stopping` | EXEC brakes for a stop. | 1 / 0 |
| `exec_completion_policy` | When a move counts as complete. | `"commanded"`, `"settled"`, `"strict"` |
| `recipe` | The active telemetry recipe. | text |
| `recipes` | The recipe files on the robot. | list of text |
| `gravity_comp` | Gravity compensation is on. | true / false |
| `friction_comp` | Friction compensation in freedrive is on. | true / false |
| `inertia_comp` | The inertia feedforward is on. | true / false |
| `coriolis_comp` | The Coriolis feedforward is on. | true / false |
| `friction_ff` | The friction feedforward is on. | true / false |
| `collision_detection` | What a detected collision does. | `"off"`, `"warn"`, `"stop"` |
| `can_read_first` | The control loop reads the drives before it commands them (off while homing). | true / false |
| `hall_check` | The Hall sensor check: `joint` (from 1; 0 = off), `pin` (0 / 1), `changes`, `edge_deg` (the angle at the last change to 0 and to 1). | deg |
| `free_joint` | The joint that is free to turn by hand, from 1. | 0 = none |
| `joint_test` | The last joint test: `joint` (from 1), `state` (`idle`, `running`, `done`, `fell_behind`, `stopped`), `amplitude_deg`, `moved_deg`, `max_error_deg`, `peak_current_ma`, `end_error_deg`, `seq`. | deg, mA |
| `tick_s` | The control loop's period. | s (0.004 on PAR6) |
| `payload` | The declared payload: `mass` and `com` (centre of mass `[x, y, z]` in the tool frame). | kg, m |
| `executing_seq` | The queued command being executed, by its queue number. | whole number |
| `completed_seq` | The last completed queued command. | whole number |
| `queue_depth` | Queued commands not yet taken up. | whole number |
| `active_command` | The command being executed, such as `"move_joints"`. | text, or `None` |
| `current_profile` | The motion profile of the current or last command. | text |
| `last_error` | The last failed command: `seq`, `cmd`, `code`, `message`. | or `None` after a success |
| `last_diagnostic` | The planner's notes on the current command (blends, inverse kinematics, singularities, path deviation). | or `None` |
| `ik_config` | The inverse kinematics settings in use. | as named in each key |
| `default_ik_solver` | The inverse kinematics engine the session uses. | text |
| `default_fk_jacobian_backend` | The kinematics library in use. | text |

## get_status()

`get_status()` asks the robot and returns `mode`, `state`, `homed`, `runtime_version`, `protocols`, `exec_paused`,
`exec_settling`, `exec_stopping` and `exec_completion_policy` as above, and:

| Field | Meaning | Unit or values |
|---|---|---|
| `pose_angles` | The convention of pose angles. | `"xyz-mobile"`: see [Pose and angles](../02-basic-theory/pose-and-angles.md) |
| `error_active` | The same as `err`. | true / false |
| `safety_violation` | The same as `safety`. | true / false |
| `software_estop` | The same as `estop`. | true / false |
| `planner` | The planner fields of the stream in one block, `default_ik_solver` and `default_fk_jacobian_backend` included. | |
| `joints` | The measured joint angles. | deg |

## get_health()

`get_health()` answers with a `level` (the worst part's: `OK` < `WARN` < `ERROR` < `STALE`), a `time` (seconds since
1970) and its `components`, in this order:

| Part | Values | Levels |
|---|---|---|
| control loop | `tick`, `p99_period_ms`, `nominal_ms`, `overruns`, `exec_time_ms` | STALE: the loop stopped for 50 ms; ERROR: the 99th percentile period over 1.5 x nominal; WARN: over 1.05 x |
| memory lock | `locked_mb` | WARN: not locked |
| CAN | `lost`, `stale`, `connected` | ERROR: a drive lost; WARN: old data |
| drives | `temperature_c`, `faulted`, `voltage_v` per joint | ERROR: a drive fault; WARN: 60 °C or more |
| gripper | `connected`, `fault`, `homed` (a CAN gripper only) | ERROR: not answering or a fault; WARN: not homed |
| errors | `errors`, `warnings` | ERROR: any error; WARN: any warning |
| homing | `homed`, `mode` | WARN: not homed |
| executor | `heartbeat` | STALE: no heartbeat |
| self-collision worker | `heartbeat`, `slowest_cycle_ms` | STALE: no heartbeat; WARN: a cycle over 10 ms |
| recorder | `last_pass_s_ago`, `rows_written` | STALE: no pass for 1 s |
| processes | each process's `pid N` or `missing` | ERROR: one missing |
| disk | `free_mb`, `total_mb` | ERROR: under 200 MB free; WARN: under 500 MB |
| memory | `used_pct`, `available_mb` | ERROR: over 95 %; WARN: over 85 % |
| CPU temperature | `celsius` | ERROR: over 80 °C; WARN: over 70 °C or unreadable |
| clock | `ntp_synced`, `rtc`, `utc` | WARN: neither network time nor a battery clock |

## get_hardware()

`get_hardware()` answers with `time`, `tick`, `joint_num`, `has_gripper` and:

- **`drives`**, one per joint: `name`, `can_id`, `answered_scan`, `answering`, `lost`, `firmware`, `hardware`,
  `serial`, `batch`, `voltage_v` (V), `temperature_c` (°C), `fault`, `flags` (`temperature`, `encoder`,
  `supply_voltage`, `driver`, `velocity`, `current`, `estop`, `watchdog`), `calibrated`, `driver_type`,
  `firmware_supported` (`None`, `"ok"`, `"too_old"`, `"too_new"` or `"undeclared"`) and `supported_range`.
- **`gripper`**: the same for the gripper's drive, or `None`.
- **`scan_unexpected_ids`**: CAN IDs from 0 to 15 that answered the start-up scan but are not used.
- **`can_link`**: the CAN interface's `interface`, `state`, `restart_ms`, `restarts`, `bus_errors`,
  `arbitration_lost`, `error_warning`, `error_passive` and `bus_off`, or `None`.
- **`io`**: `pcb_version`, `estop_channels_used`, `estop_raw` (per channel, 0 = pressed), `estop_channel_pressed`,
  `estop_pressed`, `software_estop`, `buttons_pressed` (`B1`, `B2`), `inputs` and `outputs` (3 each).

## get_versions()

`get_versions()` answers with:

- **`runtime`**: `version`, `branch`, `commit`.
- **`python`**, and **`os`**: `name`, `kernel`, `realtime`.
- **`description_package`**: `version`, `path`, `min`, `ok`.
- **`protocols`**: `commands`, `rti`, `telemetry`.
- **`hardware`**: `robot`, `revision`, `driver_types`, `gripper`, `gripper_revision`, `gripper_driver_type`,
  `description_package_min`.
- **`drives`**, one per joint: `joint` (from 1), `can_id`, `firmware`, `hardware`, `serial`, `batch`, `driver_type`,
  `supported`, `supported_range`.
- **`gripper`**: the same without `batch`, or `None`.
- **`control_box`**: `pcb_configured`, `hardware`, `software`, `serial`, `batch`.
- **`config_formats`**: the configuration file formats this software reads (`reads`) and those of the files it read
  (`files`).
- **`time`**, and **`clients`**: each connected client's `client`, `version` and `protocol`.

A value the hardware has not reported yet reads as `None`.
