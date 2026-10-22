# Diagrams and math

Diagrams are text (Mermaid) rendered in the browser, so they follow the colour scheme and can be edited like any
paragraph. Math is LaTeX rendered by MathJax.

## Flowchart

```mermaid
flowchart LR
  BOOT[BOOTING] --> IDLE
  IDLE -->|enable + home| HOMING --> IDLE
  IDLE -->|enter_exec_mode| EXEC
  IDLE -->|rti_connect| RTI
  IDLE -->|jog| JOG
  EXEC -->|stop| IDLE
  RTI -->|rti_release| IDLE
  JOG -->|release| IDLE
  EXEC & RTI & JOG -. fault .-> ERR[ACTIVE_ERROR]
  ERR -->|clear_errors + enable| IDLE
```

````markdown
```mermaid
flowchart LR
  IDLE -->|enter_exec_mode| EXEC
  EXEC -->|stop| IDLE
  EXEC -. fault .-> ERR[ACTIVE_ERROR]
```
````

## Sequence diagram

```mermaid
sequenceDiagram
  participant PC as Your program
  participant EX as Command executor
  participant RT as Real-time loop
  PC->>EX: move_joints(...)  (TCP, JSON)
  EX-->>PC: queued (id 42)
  EX->>EX: plan the trajectory
  EX->>RT: trajectory batch (IPC)
  loop every 4 ms
    RT->>RT: next setpoint -> drives (CAN)
  end
  RT-->>EX: checkpoint 42 reached
  EX-->>PC: motion complete (id 42)
```

## State diagram

```mermaid
stateDiagram-v2
  [*] --> DISABLED
  DISABLED --> ENABLED: enable
  ENABLED --> DISABLED: disable
  ENABLED --> DISABLED: any hard error
  state ENABLED {
    IDLE --> EXEC
    EXEC --> IDLE
    IDLE --> RTI
    RTI --> IDLE
  }
```

## Class diagram

```mermaid
classDiagram
  class RobotClient {
    +connect(ip)
    +enable(wait)
    +home(wait)
    +move_joints(j1..j6, speed)
    +move_linear(x, y, z, rx, ry, rz)
    +wait_motion_complete()
  }
  class RTIClient {
    +connect()
    +claim()
    +control(callback)
    +send_joint_position(q)
  }
  RobotClient --> RTIClient : rti_connect() pairs
```

## Pie and Gantt

```mermaid
pie title Where a 4 ms tick goes
  "CAN read + measurement" : 0.6
  "dispatch + send" : 0.5
  "safety + telemetry" : 0.5
  "sleep" : 2.4
```

```mermaid
gantt
  title Documentation phases
  dateFormat YYYY-MM-DD
  section Runtime
    Versioning V1-V5      :2026-10-22, 4d
  section Docs
    Reference & generated :2026-10-26, 3d
    Programming Guide    :2026-10-29, 12d
    Control Box Manual    :2026-11-10, 7d
```

## Math

Inline: the joint torque is $\tau = K_t \, i_q \, N \, \eta$, and the TCP force follows from $\tau = J^T F$.

Block:

$$
{}^{i-1}T_i =
\begin{bmatrix}
\cos\theta_i & -\sin\theta_i\cos\alpha_i & \sin\theta_i\sin\alpha_i & a_i\cos\theta_i \\
\sin\theta_i & \cos\theta_i\cos\alpha_i & -\cos\theta_i\sin\alpha_i & a_i\sin\theta_i \\
0 & \sin\alpha_i & \cos\alpha_i & d_i \\
0 & 0 & 0 & 1
\end{bmatrix}
$$

```markdown
Inline: the joint torque is $\tau = K_t \, i_q \, N \, \eta$.

$$
{}^{i-1}T_i = \begin{bmatrix} \cos\theta_i & \dots \end{bmatrix}
$$
```
