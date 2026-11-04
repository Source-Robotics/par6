# Step 3: Installing the runtime

!!! warning "Not yet repeated on a clean machine"
    The installation follows how the reference robot was set up. A package the robot needs may still be missing from
    `requirements.txt`; [Step 4](step-4-service.md)'s check imports every package the runtime needs and names a
    missing one.

## 1. Python 3.11 as python3 { #python-311 }

Ubuntu 24.04 ships Python 3.12 as `python3`. The reference robot runs 3.11, and every version pinned in
`requirements.txt` was tested on it. The installer takes whatever `python3` is and accepts 3.12 without a word, so make
3.11 the `python3` first. It comes from the deadsnakes package archive:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --set python3 /usr/bin/python3.11
```

## 2. The runtime

The reference robot keeps the runtime in `~/Desktop/RCB-Runtime`. Any folder works: Step 4 sets the service up for
the folder you choose.

```bash
cd ~/Desktop
git clone https://github.com/Source-Robotics/RCB-Runtime.git
cd RCB-Runtime
git checkout v<!-- version: runtime -->
./scripts/install.sh
```

`git checkout` picks the release these pages describe. The installer asks before it installs packages with apt, makes
the environment `.venv` from `requirements.txt`, creates the folders `logs/` and `temp_data/`, and runs the system
check `scripts/check_system.py`. It does not set up the service; [Step 4](step-4-service.md) does.

The robot runs on `.venv`, and so do the tests and the tools. To see its packages, use
`.venv/bin/python -m pip list`; a plain `python3 -m pip list` shows the system's packages, which the robot does not
use.

!!! success "Check"
    `python3 --version` prints Python 3.11, and the installer ends with `Install finished`. In its system check, the
    Python line and every `Import` line read `OK`. Two kinds of line may still be wrong, and are put right later: the
    UART, I2C device, GPIO chip and real-time priority lines read `WARN` until [Step 4](step-4-service.md) gives your
    user those rights, and `CAN can0 up` can fail until the runtime starts and brings the bus up
    ([Step 6](step-6-system-check.md)).
