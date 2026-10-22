<!-- One shared glossary, included by every manual's Terminology page. Keep entries alphabetical. -->

**Activity log**
:   The event history of the robot: every mode change, error, warning, program step and who asked for it. Shown in
    the dashboard's Activity Log tab and written to a file on the control box.

**Control box**
:   The Robot Control Box (RCB): the enclosure holding the single-board computer that runs the runtime, the
    mainboard PCB, the power electronics, the CAN bus connection to the arm, the isolated I/O and the front panel.

**Dashboard**
:   The operator web interface served by the control box on port 8081.

**Drive**
:   The motor driver board inside each joint and the CAN gripper: it closes the position, speed and current loops
    on its motor and reports position, speed, current, temperature and faults over the CAN bus.

**EXEC mode**
:   The mode in which the control box executes queued motion commands with its own trajectory planner. Commands
    reach it over the TCP command protocol or from the dashboard and block programs.

**Freedrive**
:   The robot at rest with its motors compensating gravity, so the arm can be moved by hand. Haptic walls and
    joint walls push back at the limits of the cell and of each joint.

**Homing**
:   The procedure that finds each joint's reference position after power-on. The encoders sit on the motors, so
    the arm must be homed before any mode that needs an absolute position.

**Joint space**
:   Describing the robot by its six joint angles, in degrees in the API.

**Payload**
:   The mass and centre of mass of the part the tool holds, declared to the robot so that gravity compensation
    and the safety checks account for it.

**Real-time interface (RTI)**
:   Streaming control: an external computer sends joint targets at a fixed rate and receives the robot's state
    every control cycle. The hard contract runs at the control loop's rate; the soft contract (SOFT_RTI) lets the
    computer send at its own, lower rate while the robot interpolates.

**Runtime**
:   The software that runs on the control box: the real-time control loop, the command executor, the dashboard,
    the supervisor and the helper processes.

**Safety zone**
:   A region of the cell declared as allowed or forbidden for the tool. The planner refuses a path that leaves an
    allowed zone or enters a forbidden one; the safety monitor stops the robot if the measured tool does.

**TCP (tool centre point)**
:   The operational point of the mounted tool, expressed in the base frame. Not to be confused with the TCP network
    protocol, also used in this documentation.

**Tool reference frame (TRF)**
:   The frame fixed to the mounted tool, with its origin at the tool centre point.

**World reference frame (WRF)**
:   The static frame in which poses are expressed; by default the robot's base frame.
