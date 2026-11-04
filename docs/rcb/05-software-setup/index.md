# Setting up the software

The control box runs the runtime on a Raspberry Pi 5, under Ubuntu with a real-time kernel. These six steps set up
a new Pi in the order that reproduces the reference robot, and each ends with a check of what you should now see.
They follow the runtime's own setup list, in its
[README](<!-- version-url: runtime -->/README.md) at <!-- version-link: runtime -->.

!!! warning "Not yet repeated on a clean machine"
    The installation is written from how the reference robot was set up. It has not been repeated from scratch on a
    clean Pi, so a step can still be missing. Do every check before you go on to the next step. The faults known so
    far are on [Known issues](../../par6/09-troubleshooting/known-issues.md).

## In this chapter

- [Step 1: The operating system image](step-1-os-image.md)
- [Step 2: Boot configuration](step-2-boot-configuration.md)
- [Step 3: Installing the runtime](step-3-install.md)
- [Step 4: The service](step-4-service.md)
- [Step 5: Network](step-5-network.md)
- [Step 6: System check](step-6-system-check.md)
- [Updating the runtime](updating.md)
