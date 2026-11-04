# Step 1: The operating system image

The runtime needs a real-time kernel. Write the image the runtime is tested on to the Pi's SD card and boot the Pi
from it: [ros-realtime-rpi4-image, release <!-- version: os_image -->](<!-- version-url: os_image -->). The OS
image column of [Versions & compatibility](../../support/versions.md) names the same image.

Two things about it are not obvious from its name:

- **It says rpi4, but it runs on a Raspberry Pi 5.** It is the image on the reference robot, a Pi 5 Model B.
- **It includes ROS 2 Jazzy, which the runtime does not use.** The runtime needs only the real-time kernel; you can
  leave the ROS packages or remove them.

!!! success "Check"
    On the Pi:

    ```bash
    uname -r                    # 6.8.4-rt11-raspi
    cat /sys/kernel/realtime    # 1
    ```

    If either differs, the Pi does not run the real-time kernel: write the image again.
