# Step 4: The service

`scripts/setup_system.sh` does the part of the setup the repository cannot carry, and checks all of it. With `sudo`
it sets up:

- **Groups:** your user in `dialout`, `i2c` and `gpio`, for the UART to the mainboard, the display's I2C and the GPIO
  header.
- **Password-free sudo** for the commands the runtime runs with `sudo` (bringing up `can0`, placing the CAN chip's
  interrupt threads, the display menu's reboot and power off), in `/etc/sudoers.d/10-rcb-runtime`, only where your
  user still needs a password for them.
- **Real-time priority:** the capability `cap_sys_nice` on the `python3` program. Without it the real-time loop
  refuses to start.
- **The service:** `autorun.service`, and `autorun.sh` next to the repository folder, enabled but not started, with
  `LimitMEMLOCK=infinity` so the real-time loop can lock its memory.
- **Log limits:** the journal at 200 MB, syslog at 50 MB.

Run it from the runtime's folder, with the addresses of the PCs that may send commands (more in
[Step 5](step-5-network.md)):

```bash
sudo bash scripts/setup_system.sh --allowed-ips "192.168.0.42"
```

Several addresses are separated by commas. Then log out and in again, or reboot, so the new groups apply. A second run
changes nothing that is already right.

!!! success "Check"
    ```bash
    bash scripts/setup_system.sh --check
    ```

    It ends with exit code 0 (`echo $?` prints `0`) when nothing is missing. Each missing item is a `MISSING` line,
    followed by the command that fixes it. Run the check with the arm disabled: it starts a Python that imports the
    runtime's packages, and that slows the real-time loop for a few seconds.

Enable no other service for the runtime. The runtime also has an older template, `rcb-runtime.service`
(`scripts/install_service.sh`), which has never been tested on a clean machine; with both enabled, two supervisors
start, and the check above reports it.

## Starting and stopping

```bash
sudo systemctl restart autorun.service      # every process; the arm is no longer homed: home it again
sudo systemctl stop autorun.service         # the drives let go of the arm about 0.1 s later: support or park it first
journalctl -u autorun.service -f            # the service's output
```
