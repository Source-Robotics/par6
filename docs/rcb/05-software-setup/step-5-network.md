# Step 5: Network

!!! danger "The runtime has no authentication"
    No password, no key, no encryption. The command port lets in a PC by its IP address only, which is easy to fake,
    and the dashboard has no login at all: anyone who can open it can enable the arm, jog it, run programs and change
    settings. Run the robot on an isolated network: the robot, its control PC and nothing else, on a switch of their
    own or a direct cable. Never open ports 8081, 29000 or 30001 to a shared network, and never to the internet.

## The ports

| Service | Port | Who can use it |
|---|---|---|
| Command hub: the Python client and every other client (TCP) | 29000 | a PC whose address is in the allowed list |
| Real-time command stream (UDP) | 30001 | the paired PC, checked by its address |
| Real-time state stream (UDP) | sent to port 30002 of the paired PC | |
| Telemetry (UDP) | sent to port 30003 of every device on the subnet | anyone on the network can read it |
| Dashboard (HTTP) | 8081 | anyone who can reach it |
| Motor tuner and firmware flasher (HTTP), while the tool runs | 8082, 8083 | anyone who can reach it |

## Allowing your PC

The command hub accepts the addresses built into the runtime (the development PCs) and those in `RCB_ALLOWED_IPS`.
[Step 4](step-4-service.md)'s `--allowed-ips` writes that list into the service; run it again to change the list:

```bash
sudo bash scripts/setup_system.sh --allowed-ips "192.168.0.42,192.168.0.43"
sudo systemctl restart autorun.service
```

`--allowed-ips "*"` switches the address check off, so that any machine that reaches port 29000 can command the arm:
on an isolated network only. The real-time stream needs no entry: it follows the address of the PC's command
connection.

To send the telemetry to one PC instead of the whole subnet, set `TELEMETRY_DESTINATION` in the runtime's
`config/networking.py` to that PC's address.

!!! success "Check"
    On the control PC, the dashboard opens at `http://<robot address>:8081`, and a client connects
    ([`connect()`](../../programming/commands/connection/connect.md)). A PC whose address is not in the allowed list
    gets the answer `FORBIDDEN`, and the runtime logs `rejected connection from <address>`.
