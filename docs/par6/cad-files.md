# Downloads and files

Everything to download for a PAR6 system, the arm and its control box, at the versions these pages describe. The
versions come from one file, `versions.yml`, so this page changes with them; which versions work together is in
[Versions & compatibility](../support/versions.md).

## Software and firmware

| What | Version | Download | How to install |
|---|---|---|---|
| Runtime: the control box's software, with the Python client (`robotclient/`) and the dashboard | <!-- version-link: runtime --> | [RCB-Runtime](<!-- version-url: runtime -->) | [Installing the runtime](../rcb/05-software-setup/step-3-install.md) |
| Operating system image for the control box's Raspberry Pi 5, with a real-time kernel | the image the runtime is tested on | [ros-realtime-rpi4-image](<!-- version-url: os_image -->) | [Step 1: The operating system image](../rcb/05-software-setup/step-1-os-image.md) |
| Drive firmware of the joints (STEPFOC) | the range in [Versions & compatibility](../support/versions.md) | [STEPFOC releases](https://docs.source-robotics.com/STEPFOC-docs/07-firmware/releases/) | [Drive firmware updates](../rcb/07-operating/firmware-update.md) |
| Drive firmware of the grippers: STEPFOC for the MSG, Spectral Micro for the SSG48 | the same range | [STEPFOC releases](https://docs.source-robotics.com/STEPFOC-docs/07-firmware/releases/), [Spectral Micro releases](https://docs.source-robotics.com/Spectral-BLDC-docs/07-firmware/releases/) | [Drive firmware updates](../rcb/07-operating/firmware-update.md) |
| Control box mainboard firmware, a PlatformIO project | main branch | [RCB motherboard firmware](https://github.com/Source-Robotics/RCB-Robot-Control-Box/tree/main/RCB%20motherboard%20firmware) | |
| ST-Link USB driver, for uploading the mainboard firmware from Windows | | [STSW-LINK009](https://www.st.com/en/development-tools/stsw-link009.html) | |
| Robot models: URDF and MuJoCo, PAR6 with each tool | main branch | [robot_descriptions: PAR6](https://github.com/Source-Robotics/robot_descriptions/blob/main/guides/par6.md) | [Robot models & simulation](../simulation/models.md) |

The version links open the files at exactly that release. The mainboard firmware and the robot models have no
release these pages follow: use their main branch. Known faults are on [Known issues](09-troubleshooting/known-issues.md).

## The arm: CAD and build files

The latest files, on the main branch of the
[arm repository](https://github.com/Source-Robotics/PAR6-Collaborative-Robot-Arm). PAR6 is in beta: the files can
still change.

| What | Where |
|---|---|
| Printable parts (STL) | [3D Print Files](https://github.com/Source-Robotics/PAR6-Collaborative-Robot-Arm/tree/main/3D%20Print%20Files) |
| Bill of materials, with reference images and the custom and machined parts | [BOM](https://github.com/Source-Robotics/PAR6-Collaborative-Robot-Arm/tree/main/BOM) |
| Building the cables, datasheets and diagrams | [Assembly manual](https://github.com/Source-Robotics/PAR6-Collaborative-Robot-Arm/tree/main/Assembly%20manual) |
| Photos | [Photos](https://github.com/Source-Robotics/PAR6-Collaborative-Robot-Arm/tree/main/Photos) |
| Beta guide: the operating system, the beta mainboards, setting up the drives | [beta_guide.md](https://github.com/Source-Robotics/PAR6-Collaborative-Robot-Arm/blob/main/beta_guide.md) |
| Assembly videos | [The arm](https://youtu.be/3Rrd6hjBnM4) · [Cables, part 1](https://youtu.be/QlNfWAga1l0) · [Cables, part 2](https://youtu.be/GOb1vQsjfOs) |

## The control box: CAD and build files { #the-control-box }

The latest files, on the main branch of the
[control box repository](https://github.com/Source-Robotics/RCB-Robot-Control-Box).

| What | Where |
|---|---|
| Enclosure and printed parts (STEP) | [STEP files](https://github.com/Source-Robotics/RCB-Robot-Control-Box/tree/main/STEP%20files) |
| Bill of materials | [BOM](https://github.com/Source-Robotics/RCB-Robot-Control-Box/tree/main/BOM) |
| Building the cables, the print table | [Assembly manual](https://github.com/Source-Robotics/RCB-Robot-Control-Box/tree/main/Assembly%20manual) |
| Assembly video | [The control box](https://youtu.be/qAzd839ixuw) |
| The connector panel's pin map: every terminal, Pi pin and signal | [pin_map.md](<!-- version-url: runtime -->/docs/pin_map.md), in the runtime at <!-- version-link: runtime --> |

## More

| What | Where |
|---|---|
| Safety warning and disclaimer | [The arm](https://github.com/Source-Robotics/PAR6-Collaborative-Robot-Arm/blob/main/SAFETY_WARNING_AND_DISCLAIMER.md) · [The control box](https://github.com/Source-Robotics/RCB-Robot-Control-Box/blob/main/SAFETY_WARNING_AND_DISCLAIMER.md) |
| Grippers and other end effectors | [End effectors](../grippers/index.md), with their own CAD and downloads |
| This documentation | [Source-Robotics/par6](https://github.com/Source-Robotics/par6) |
