# Step 2: Boot configuration

The CAN bus `can0`, the display's `/dev/i2c-1` and the mainboard's `/dev/ttyAMA0` do not exist until you set them up
in the Pi's boot files and reboot. Nothing in the runtime can create them, and nothing points at the boot files when
one is missing: you get a CAN start failure, or an lgpio "GPIO busy", and no reason.

## 1. Switch on CAN, SPI, I2C and the UART

Add these four lines to `/boot/firmware/config.txt`:

```
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=12   # creates can0
dtoverlay=spi0-1cs                                        # SPI for the CAN chip, CS0 only
dtparam=i2c_arm=on                                        # the display
enable_uart=1                                             # the link to the mainboard
```

`oscillator=` must match the crystal on the CAN board: 16 MHz here. A board with an 8 MHz crystal and this line runs
the bus at the wrong bit rate, without an error. Use `spi0-1cs`, not `dtparam=spi=on`: that also takes the pin of
isolated input 3, and the runtime then stops with "GPIO busy".

The runtime's `system_setup/boot_config.txt` is the reference robot's file, with what each line does. Merge the lines
into your own file; do not copy the whole file over it, because the rest of it holds display and audio settings for
that Pi.

## 2. Free the UART from the console

The runtime talks to the mainboard on `/dev/ttyAMA0` at 256000 baud. A new Pi also puts its kernel console and a login
prompt on that port, at 115200 baud. Nothing reports an error: the mainboard receives the boot messages mixed into its
protocol, and the link looks like faulty hardware.

1. In `/boot/firmware/cmdline.txt`, remove `console=serial0,115200` (or `console=ttyAMA0,115200`) and leave the rest
   of the line as it is. The file must stay one line, and it has no comments.
2. Switch off the login prompt on the port:

    ```bash
    sudo systemctl disable --now serial-getty@ttyAMA0.service
    ```

The runtime's `system_setup/boot_cmdline.txt` is the reference robot's `cmdline.txt`, to compare yours with.

## 3. Reboot

The settings take effect only at boot.

!!! success "Check"
    After the reboot:

    ```bash
    cat /proc/consoles            # tty1 only
    ip link show can0             # the interface exists
    ls /dev/i2c-1 /dev/ttyAMA0    # both exist
    ```

    If one is missing, compare your two files with the reference copies and reboot again.
