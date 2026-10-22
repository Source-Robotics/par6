# Robot models & simulation

The maintained models of the PAR6 and its tools, in the formats the common simulators and planners take. These
are the files the runtime itself uses for its kinematics and self-collision geometry, so a simulation built on
them matches the real arm.

## Why these assets

1. **Visualization** — show the arm's measured or commanded pose in a viewer.
2. **Simulation** — run the same programs against a physics engine before the arm.
3. **Motion planning and control** — kinematics, dynamics and collision geometry identical to the robot's own.
4. **AI and data collection** — the frames, joint conventions and tool poses teleoperation and learning pipelines need.

## Download

| Robot | CAD | URDF | MJCF (MuJoCo) | Sim2Bot |
|---|---|---|---|---|
| PAR6 with flange, MSG gripper or SSG48 gripper | [CAD files](../par6/cad-files.md) | `par6_urdf.zip` | `par6_mujoco.zip` | included in both packages |

Package version 2.0.0 (see the package changelog). The three tool variants share one set of link meshes; only the
end-effector geometry differs. Joint directions follow the real hardware: positive in the model is positive on the
arm. [Details](description-package.md)

## Accessories

- MSG gripper family (three motor sizes, three rail lengths), SSG48 gripper, the control box enclosure: CAD on the
  [CAD files](../grippers/cad-files.md) pages.

## Simulate

| Robot | MuJoCo | ROS / RViz | NVIDIA Isaac Sim |
|---|---|---|---|
| PAR6 | `scene_msg.xml` (default), `scene_flange.xml`, `scene_ssg48.xml` — [docs](mujoco.md) | `par6_description` package, `display.launch` — [docs](urdf-ros.md) | planned — [docs](isaac-sim.md) |

## Stream the real arm in

Move the real arm by hand and drive the simulated one with its measured tool pose, over UDP, one way.
[docs](tcp-pose-stream.md)
