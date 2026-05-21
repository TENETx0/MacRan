# MacRan — MAC Address Randomizer & Changer

**MacRan** is a command-line utility for Linux that lets you randomize, spoof, or restore the MAC address of any network interface. It supports fully random MAC generation, vendor-prefix spoofing from a built-in OUI database, manual address assignment, and hardware MAC restoration — all from a single script with no external Python dependencies.

---

## Features

- Randomize a MAC address with a single command
- Spoof a vendor-specific MAC using a built-in OUI database (18 vendors, 105+ prefixes)
- Set a specific MAC address manually
- Restore the hardware-burned-in (permanent) MAC address
- Interactive menu for guided operation
- Full CLI argument support for scripting and automation
- Validates MAC format before applying any change
- Verifies the change was applied and reports back
- Generates locally-administered, unicast-safe random MACs

---

## Requirements

**Python:** 3.9+

**System dependencies** (standard on all modern Linux distributions):

| Package    | Purpose                        | Install (Debian/Ubuntu)         |
|------------|--------------------------------|---------------------------------|
| `iproute2` | `ip link` — applies MAC change | usually pre-installed           |
| `ethtool`  | reads permanent MAC address    | `sudo apt install ethtool`      |

No third-party Python packages are required.

---

## Installation

```bash
git clone https://github.com/TENETx0/macran.git
cd macran
chmod +x macran.py
```

To run it as a system-wide command:

```bash
sudo cp macran.py /usr/local/bin/macran
sudo chmod +x /usr/local/bin/macran
# Then use: sudo macran -i eth0 -r
```

---

## Usage

### Interactive menu

Launch with no arguments to enter the guided interactive menu:

```bash
sudo python3 macran.py
```

### Command-line mode

```
usage: macran [-h] [-i IFACE] [-r] [-m MAC] [-v VENDOR]
              [--show] [--reset] [--list-interfaces] [--list-vendors]
              [{reset}]
```

| Flag / Command              | Description                                          |
|-----------------------------|------------------------------------------------------|
| `-i IFACE`                  | Target interface (e.g. `eth0`, `wlan0`)              |
| `-r`, `--random`            | Assign a fully random MAC address                    |
| `-m MAC`                    | Set a specific MAC (`xx:xx:xx:xx:xx:xx`)             |
| `-v VENDOR`                 | Randomize with a vendor OUI prefix (e.g. `Intel`)    |
| `--show`                    | Display the current (and permanent) MAC              |
| `--reset`                   | Restore the permanent hardware MAC                   |
| `reset` *(positional)*      | Reset all interfaces to their permanent MACs         |
| `--list-interfaces`         | List all available network interfaces                |
| `--list-vendors`            | Print the built-in vendor OUI database               |

---

## Examples

```bash
# Randomize the MAC address of wlan0
sudo python3 macran.py -i wlan0 -r

# Set a specific MAC address
sudo python3 macran.py -i eth0 -m 00:11:22:33:44:55

# Spoof an Intel vendor MAC on wlan0
sudo python3 macran.py -i wlan0 -v Intel

# Spoof an Apple vendor MAC on eth0
sudo python3 macran.py -i eth0 -v Apple

# Show current and permanent MAC for eth0
sudo python3 macran.py -i eth0 --show

# Restore the hardware MAC for a single interface
sudo python3 macran.py -i wlan0 --reset

# Restore hardware MACs on ALL interfaces at once
sudo python3 macran.py reset

# List available interfaces with current MACs
sudo python3 macran.py --list-interfaces

# Print the vendor database (no root needed)
python3 macran.py --list-vendors
```

---

## Vendor Database

MacRan ships with a built-in OUI database covering 18 vendors and 105+ registered prefixes.

| Vendor            | Vendor           | Vendor           |
|-------------------|------------------|------------------|
| Apple             | Intel            | Cisco            |
| Broadcom          | Qualcomm/Atheros | Dell             |
| Lenovo            | Samsung          | TP-Link          |
| Realtek           | VMware           | Microsoft        |
| ASUS              | Huawei           | Ralink/MediaTek  |
| Netgear           | HP               | NVIDIA           |

Run `python3 macran.py --list-vendors` for the full prefix listing.

---

## How It Works

1. **Reading** — MAC is read directly from `/sys/class/net/<iface>/address` (no external tools).
2. **Changing** — Uses `ip link set <iface> down / address <mac> / up` from iproute2.
3. **Permanent MAC** — Retrieved via `ethtool -P` or `/sys/class/net/<iface>/permaddr` (kernel 4.12+).
4. **Validation** — Regex validates `xx:xx:xx:xx:xx:xx` format before any system call.
5. **Verification** — Re-reads the interface after change to confirm it was applied.
6. **Random generation** — First octet always has bit 1 set (locally administered) and bit 0 cleared (unicast).

---

## Notes

- Root privileges (`sudo`) are required for all operations that modify interface state.
- Changes made by MacRan are **not persistent** across reboots. The hardware MAC is restored on each system restart unless the change is written to a network config file.
- On some wireless adapters, the driver may reject MAC changes while the interface is associated. Disconnect from the network first if you encounter errors.
- `ethtool` is optional but recommended. Without it, `--reset` falls back to the sysfs `permaddr` file, which is not available on all drivers.

---

## Legal Disclaimer

This tool is intended for use in authorized penetration testing, security research, privacy protection, and network administration. Do not use MacRan on networks or systems you do not own or have explicit permission to test. The author assumes no responsibility for misuse.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Monish Kanna S P**  
[github.com/TENETx0](https://github.com/TENETx0)
