# Versions & compatibility

Every part of the robot carries a version of its own kind. This page says how to read them and which combinations
work together. It is generated from the runtime repository at every release; what changed in each part is in that
part's release notes, linked in the table.

## How to read a version

| Part | Form | Example | Where to see it |
|---|---|---|---|
| Runtime (the control box software) | `major.minor.patch` | 1.2.0 | Dashboard → System Info → Versions; the landing page of the software manuals |
| Python client | `major.minor.patch` | 1.2.0 | `robotclient.__version__` |
| Drive firmware (joints, gripper) | integer | 109 | Dashboard → Motor tab; `get_hardware` |
| Control box PCB | `v` + revision | v2 | the label inside the box; Dashboard → System Info |
| PAR6 arm | `v` + revision, plus a serial number | PAR6 v1.1 | the label on the base |
| End effectors | `v` + revision | MSG v1.0 | the label on the module |
| Description package (models) | `major.minor.patch` | 2.0.0 | the package changelog |
| Manuals | runtime `major.minor` for guides; `year.letter` for hardware manuals | SR-4001 1.2 · SR-1001 2026.B | each manual's landing page |

A `patch` release changes nothing a program or a configuration file can see. A `minor` release adds commands,
fields or keys and stays backward compatible. A `major` release breaks a protocol or a file format.

## Compatibility matrix

| Runtime | Client | TCP protocol | RTI protocol | Telemetry format | Drive firmware | Control box PCB | Description package | OS image | Manuals |
|---|---|---|---|---|---|---|---|---|---|
| 0.9.0 (development) | — | — | — | — | 103 | v1, v2 | 2.0.0 | Ubuntu 24.04.2, kernel 6.8.4-rt11 | draft |

## Release notes, by part

- Runtime: [Runtime release notes](../programming/references/runtime-release-notes.md)
- Drive firmware: [Firmware release notes](../rcb/07-operating/firmware-release-notes.md)
- PAR6 arm: [Hardware revisions](../par6/appendices/hardware-revisions.md)
- End effectors: [MSG](../grippers/msg/hardware-revisions.md) · [SSG48](../grippers/ssg48/hardware-revisions.md)
  · [Pneumatic tools](../grippers/pneumatic/hardware-revisions.md)
- Description package: [Package changelog](../simulation/package-changelog.md)
- The manuals and guides: the *Document history* on each one's *About* page.
