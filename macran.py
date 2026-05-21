#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                        MacRan v1.0                           ║
║              MAC Address Randomizer & Changer                ║
║                                                              ║
║  Author : Monish Kanna S P                                   ║
║  GitHub : https://github.com/TENETx0                         ║
║  License: MIT                                                ║
╚══════════════════════════════════════════════════════════════╝

A production-ready MAC address changer utility for Linux.
Supports random, vendor-specific, and manual MAC address changes.
"""

import argparse
import os
import re
import random
import subprocess
import sys
import time
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# ANSI colour helpers
# ─────────────────────────────────────────────────────────────────────────────

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
MAGENTA= "\033[95m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def red(s):     return f"{RED}{s}{RESET}"
def green(s):   return f"{GREEN}{s}{RESET}"
def yellow(s):  return f"{YELLOW}{s}{RESET}"
def cyan(s):    return f"{CYAN}{s}{RESET}"
def blue(s):    return f"{BLUE}{s}{RESET}"
def magenta(s): return f"{MAGENTA}{s}{RESET}"
def bold(s):    return f"{BOLD}{s}{RESET}"
def dim(s):     return f"{DIM}{s}{RESET}"

# ─────────────────────────────────────────────────────────────────────────────
# Vendor database  (OUI prefix → vendor name)
# ─────────────────────────────────────────────────────────────────────────────

VENDOR_DB: dict[str, str] = {
    # Apple
    "00:03:93": "Apple",
    "00:0A:27": "Apple",
    "00:0A:95": "Apple",
    "00:1C:B3": "Apple",
    "00:1E:C2": "Apple",
    "00:23:32": "Apple",
    "00:26:B9": "Apple",
    "04:54:53": "Apple",
    "AC:DE:48": "Apple",
    # Intel
    "00:02:B3": "Intel",
    "00:03:47": "Intel",
    "00:07:E9": "Intel",
    "00:0C:F1": "Intel",
    "00:13:02": "Intel",
    "00:15:17": "Intel",
    "00:19:D1": "Intel",
    "00:1B:21": "Intel",
    "8C:EC:4B": "Intel",
    # Cisco
    "00:00:0C": "Cisco",
    "00:01:42": "Cisco",
    "00:01:43": "Cisco",
    "00:01:64": "Cisco",
    "00:01:96": "Cisco",
    "00:01:97": "Cisco",
    "00:03:6B": "Cisco",
    "00:04:6D": "Cisco",
    "00:07:0D": "Cisco",
    # Broadcom
    "00:10:18": "Broadcom",
    "00:90:4C": "Broadcom",
    "04:BD:88": "Broadcom",
    "74:E5:F9": "Broadcom",
    "A4:BA:DB": "Broadcom",
    # Qualcomm / Atheros
    "00:03:7F": "Qualcomm/Atheros",
    "00:17:F2": "Qualcomm/Atheros",
    "00:1C:BF": "Qualcomm/Atheros",
    "20:02:AF": "Qualcomm/Atheros",
    "E0:91:F5": "Qualcomm/Atheros",
    # Dell
    "00:06:5B": "Dell",
    "00:08:74": "Dell",
    "00:0B:DB": "Dell",
    "00:11:43": "Dell",
    "18:66:DA": "Dell",
    "F4:8E:38": "Dell",
    # Lenovo
    "00:09:2D": "Lenovo",
    "00:1A:6B": "Lenovo",
    "28:D2:44": "Lenovo",
    "54:EE:75": "Lenovo",
    "E8:B4:C8": "Lenovo",
    # Samsung
    "00:12:FB": "Samsung",
    "00:16:32": "Samsung",
    "00:17:C9": "Samsung",
    "8C:77:12": "Samsung",
    "D4:E8:B2": "Samsung",
    # TP-Link
    "00:27:19": "TP-Link",
    "14:CF:92": "TP-Link",
    "50:C7:BF": "TP-Link",
    "54:AF:97": "TP-Link",
    "D8:07:B6": "TP-Link",
    # Realtek
    "00:01:6C": "Realtek",
    "00:E0:4C": "Realtek",
    "52:54:00": "Realtek",
    "B4:2E:99": "Realtek",
    "D8:CB:8A": "Realtek",
    # VMware (useful for VMs)
    "00:0C:29": "VMware",
    "00:50:56": "VMware",
    "00:05:69": "VMware",
    # Microsoft
    "00:03:FF": "Microsoft",
    "00:0D:3A": "Microsoft",
    "00:50:F2": "Microsoft",
    "28:18:78": "Microsoft",
    "60:45:BD": "Microsoft",
    # ASUS
    "00:1A:92": "ASUS",
    "00:1D:60": "ASUS",
    "04:92:26": "ASUS",
    "10:BF:48": "ASUS",
    "2C:FD:A1": "ASUS",
    "74:D0:2B": "ASUS",
    # Huawei
    "00:18:82": "Huawei",
    "00:25:9E": "Huawei",
    "04:BD:70": "Huawei",
    "24:DF:6A": "Huawei",
    "54:89:98": "Huawei",
    "70:72:3C": "Huawei",
    # Ralink / MediaTek
    "00:0C:43": "Ralink/MediaTek",
    "00:17:C5": "Ralink/MediaTek",
    "00:1D:AA": "Ralink/MediaTek",
    "D4:6E:0E": "Ralink/MediaTek",
    "E8:4E:06": "Ralink/MediaTek",
    # Netgear
    "00:09:5B": "Netgear",
    "00:14:6C": "Netgear",
    "00:1B:2F": "Netgear",
    "20:4E:7F": "Netgear",
    "A0:40:A0": "Netgear",
    "C0:FF:D4": "Netgear",
    # Hewlett-Packard (HP)
    "00:01:E6": "HP",
    "00:0B:CD": "HP",
    "00:11:0A": "HP",
    "00:17:A4": "HP",
    "18:A9:05": "HP",
    "3C:D9:2B": "HP",
    # NVIDIA
    "00:04:4B": "NVIDIA",
    "00:1A:BA": "NVIDIA",
    "04:4B:ED": "NVIDIA",
    "2C:CB:39": "NVIDIA",
    "58:8A:5A": "NVIDIA",
}

# Build a name → list-of-prefixes reverse index for vendor lookup
_VENDOR_BY_NAME: dict[str, list[str]] = {}
for _prefix, _name in VENDOR_DB.items():
    _VENDOR_BY_NAME.setdefault(_name.lower(), []).append(_prefix)


# ─────────────────────────────────────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────────────────────────────────────

BANNER = f"""
{CYAN}
  ╔══════════════════════════════════════════════════════════════════╗
  ║                                                                  ║
  ║   {BOLD}███╗   ███╗ █████╗  ██████╗{RESET}{CYAN} ██████╗  █████╗ ███╗   ██╗      ║
  ║   {BOLD}████╗ ████║██╔══██╗██╔════╝{RESET}{CYAN}██╔══██╗██╔══██╗████╗  ██║      ║
  ║   {BOLD}██╔████╔██║███████║██║{RESET}{CYAN}     ██████╔╝███████║██╔██╗ ██║      ║
  ║   {BOLD}██║╚██╔╝██║██╔══██║██║{RESET}{CYAN}     ██╔══██╗██╔══██║██║╚██╗██║      ║
  ║   {BOLD}██║ ╚═╝ ██║██║  ██║╚██████╗{RESET}{CYAN}██║  ██║██║  ██║██║ ╚████║      ║
  ║   {BOLD}╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝{RESET}{CYAN}╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝      ║
  ║                                                                  ║
  ║{DIM}   MAC Address Randomizer & Changer                    v1.0  {RESET}{CYAN}  ║
  ║{DIM}   ─────────────────────────────────────────────────────────{RESET}{CYAN}   ║
  ║{DIM}   Author  :  Monish Kanna S P                              {RESET}{CYAN}   ║
  ║{DIM}   GitHub  :  https://github.com/TENETx0                   {RESET}{CYAN}   ║
  ║{DIM}   License :  MIT                                          {RESET}{CYAN}   ║
  ║                                                                  ║
  ╚══════════════════════════════════════════════════════════════════╝
{RESET}"""


# ─────────────────────────────────────────────────────────────────────────────
# Privilege check
# ─────────────────────────────────────────────────────────────────────────────

def require_root() -> None:
    """Abort if the script is not running as root."""
    if os.geteuid() != 0:
        print(red("[!] MacRan must be run as root (use sudo)."))
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Network interface helpers
# ─────────────────────────────────────────────────────────────────────────────

def list_interfaces() -> list[str]:
    """Return a list of available network interfaces (excluding loopback)."""
    interfaces: list[str] = []
    net_path = "/sys/class/net"
    if os.path.isdir(net_path):
        for iface in sorted(os.listdir(net_path)):
            if iface != "lo":
                interfaces.append(iface)
    return interfaces


def get_current_mac(interface: str) -> Optional[str]:
    """
    Retrieve the current MAC address for *interface*.

    Returns the MAC string (xx:xx:xx:xx:xx:xx) or None on failure.
    """
    # Prefer reading directly from sysfs — no external tool needed
    sysfs_path = f"/sys/class/net/{interface}/address"
    if os.path.isfile(sysfs_path):
        try:
            with open(sysfs_path) as fh:
                return fh.read().strip()
        except OSError:
            pass

    # Fallback: parse ip link show output
    try:
        result = subprocess.run(
            ["ip", "link", "show", interface],
            capture_output=True, text=True, check=True
        )
        match = re.search(r"link/ether\s+([0-9a-f:]{17})", result.stdout)
        if match:
            return match.group(1)
    except subprocess.CalledProcessError:
        pass

    return None


def get_permanent_mac(interface: str) -> Optional[str]:
    """
    Retrieve the hardware-burned-in (permanent) MAC address via ethtool.
    Falls back to the value stored in /sys/.../permaddr if ethtool is absent.
    """
    # Try ethtool first
    try:
        result = subprocess.run(
            ["ethtool", "-P", interface],
            capture_output=True, text=True, check=True
        )
        match = re.search(r"Permanent address:\s+([0-9a-fA-F:]{17})", result.stdout)
        if match:
            return match.group(1).lower()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try sysfs permaddr (kernel 4.12+)
    permaddr_path = f"/sys/class/net/{interface}/permaddr"
    if os.path.isfile(permaddr_path):
        try:
            with open(permaddr_path) as fh:
                addr = fh.read().strip()
                if addr and addr != "00:00:00:00:00:00":
                    return addr
        except OSError:
            pass

    return None


def validate_mac(mac: str) -> bool:
    """Return True if *mac* matches the standard xx:xx:xx:xx:xx:xx pattern."""
    pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
    return bool(re.match(pattern, mac))


# ─────────────────────────────────────────────────────────────────────────────
# MAC generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_random_mac(vendor_prefix: Optional[str] = None) -> str:
    """
    Generate a random unicast, locally administered MAC address.

    If *vendor_prefix* is supplied (e.g. "00:1A:2B") it is used as the
    first three octets; otherwise a random locally-administered OUI is
    generated (bit 1 of first octet set to 1, bit 0 set to 0).
    """
    if vendor_prefix:
        parts = vendor_prefix.split(":")
        suffix = [random.randint(0x00, 0xFF) for _ in range(3)]
        octets = [int(p, 16) for p in parts] + suffix
    else:
        # Locally administered (bit 1 = 1), unicast (bit 0 = 0)
        first = (random.randint(0x00, 0xFF) & 0xFE) | 0x02
        rest  = [random.randint(0x00, 0xFF) for _ in range(5)]
        octets = [first] + rest

    return ":".join(f"{o:02x}" for o in octets)


def prefix_for_vendor(vendor_name: str) -> Optional[str]:
    """
    Look up a vendor OUI prefix by name (case-insensitive).

    Returns a randomly chosen prefix from VENDOR_DB or None if unknown.
    """
    key = vendor_name.strip().lower()
    # Exact match first
    if key in _VENDOR_BY_NAME:
        return random.choice(_VENDOR_BY_NAME[key])
    # Partial match
    for name, prefixes in _VENDOR_BY_NAME.items():
        if key in name:
            return random.choice(prefixes)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Core MAC-change logic
# ─────────────────────────────────────────────────────────────────────────────

def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run a command, raise RuntimeError with stderr on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    return result


def set_mac(interface: str, new_mac: str) -> bool:
    """
    Apply *new_mac* to *interface* using `ip link`.

    Brings the interface down, sets the address, brings it back up.
    Returns True on success, False on failure.
    """
    print(dim(f"  → Bringing {interface} down..."))
    try:
        _run(["ip", "link", "set", interface, "down"])
        print(dim(f"  → Setting MAC to {new_mac}..."))
        _run(["ip", "link", "set", interface, "address", new_mac])
        print(dim(f"  → Bringing {interface} up..."))
        _run(["ip", "link", "set", interface, "up"])
    except RuntimeError as exc:
        print(red(f"[!] Failed to change MAC: {exc}"))
        return False

    # Brief pause so the OS can settle
    time.sleep(0.4)

    # Verify the change was applied
    applied = get_current_mac(interface)
    if applied and applied.lower() == new_mac.lower():
        return True

    print(yellow(f"[~] Warning: expected {new_mac} but interface shows {applied}"))
    return False


# ─────────────────────────────────────────────────────────────────────────────
# High-level operations
# ─────────────────────────────────────────────────────────────────────────────

def op_show(interface: str) -> None:
    """Print the current MAC address (and permanent MAC if available)."""
    mac = get_current_mac(interface)
    if not mac:
        print(red(f"[!] Could not read MAC for interface '{interface}'."))
        return

    # Vendor lookup
    prefix = mac[:8].upper()
    vendor = VENDOR_DB.get(prefix, "Unknown vendor")

    print(f"\n  {bold('Interface :')} {cyan(interface)}")
    print(f"  {bold('Current MAC:')} {green(mac)}  {dim(f'({vendor})')}")

    perm = get_permanent_mac(interface)
    if perm:
        perm_vendor = VENDOR_DB.get(perm[:8].upper(), "Unknown vendor")
        print(f"  {bold('Perm MAC   :')} {yellow(perm)}  {dim(f'({perm_vendor})')}")
    print()


def op_randomize(interface: str, vendor: Optional[str] = None) -> None:
    """Randomize the MAC address of *interface*, optionally spoofing a vendor."""
    old_mac = get_current_mac(interface)
    print(f"\n  {bold('Interface :')} {cyan(interface)}")
    print(f"  {bold('Old MAC   :')} {yellow(old_mac or 'unknown')}")

    prefix = None
    if vendor:
        prefix = prefix_for_vendor(vendor)
        if not prefix:
            print(red(f"[!] Vendor '{vendor}' not found in database."))
            print(dim("    Available vendors: ") + ", ".join(sorted(_VENDOR_BY_NAME)))
            return
        print(f"  {bold('Vendor    :')} {magenta(vendor)}  {dim(f'(prefix {prefix})')}")

    new_mac = generate_random_mac(prefix)
    print(f"  {bold('New MAC   :')} {green(new_mac)}")

    if set_mac(interface, new_mac):
        print(green(f"\n  [✓] MAC address changed successfully!"))
    else:
        print(red(f"\n  [✗] MAC address change may have failed — check manually."))
    print()


def op_set(interface: str, mac: str) -> None:
    """Set a specific MAC address on *interface*."""
    if not validate_mac(mac):
        print(red(f"[!] '{mac}' is not a valid MAC address (expected xx:xx:xx:xx:xx:xx)."))
        return

    old_mac = get_current_mac(interface)
    print(f"\n  {bold('Interface :')} {cyan(interface)}")
    print(f"  {bold('Old MAC   :')} {yellow(old_mac or 'unknown')}")
    print(f"  {bold('New MAC   :')} {green(mac)}")

    if set_mac(interface, mac):
        print(green(f"\n  [✓] MAC address changed successfully!"))
    else:
        print(red(f"\n  [✗] MAC address change may have failed — check manually."))
    print()


def op_reset(interface: str) -> None:
    """Restore the hardware-burned-in (permanent) MAC address."""
    print(f"\n  {bold('Interface :')} {cyan(interface)}")

    perm = get_permanent_mac(interface)
    if not perm:
        print(red("  [!] Could not determine permanent MAC address."))
        print(dim("      Try installing ethtool:  sudo apt install ethtool"))
        return

    current = get_current_mac(interface)
    if current and current.lower() == perm.lower():
        print(green("  [✓] MAC is already set to its permanent address. Nothing to do."))
        print(f"      {bold('MAC:')} {green(perm)}")
        print()
        return

    print(f"  {bold('Current   :')} {yellow(current or 'unknown')}")
    print(f"  {bold('Restoring :')} {green(perm)}")

    if set_mac(interface, perm):
        print(green(f"\n  [✓] MAC restored to permanent address!"))
    else:
        print(red(f"\n  [✗] Reset may have failed — check manually."))
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Interface selector (interactive)
# ─────────────────────────────────────────────────────────────────────────────

def pick_interface() -> Optional[str]:
    """Present the user with a numbered list of interfaces and return their choice."""
    interfaces = list_interfaces()
    if not interfaces:
        print(red("[!] No network interfaces found."))
        return None

    print(f"\n  {bold('Available interfaces:')}")
    for idx, iface in enumerate(interfaces, 1):
        mac = get_current_mac(iface) or "unknown"
        print(f"    {cyan(str(idx))}. {bold(iface):<14} {dim(mac)}")
    print()

    while True:
        try:
            raw = input(f"  {bold('Select interface [1-'+ str(len(interfaces)) +']:')} ").strip()
            choice = int(raw)
            if 1 <= choice <= len(interfaces):
                return interfaces[choice - 1]
        except (ValueError, EOFError):
            pass
        print(yellow("  [~] Invalid selection, try again."))


# ─────────────────────────────────────────────────────────────────────────────
# Interactive menu
# ─────────────────────────────────────────────────────────────────────────────

MENU = f"""
  {bold('─' * 46)}
  {bold(cyan('  MacRan — Main Menu'))}
  {bold('─' * 46)}
    {cyan('1.')} Show current MAC address
    {cyan('2.')} Randomize MAC address
    {cyan('3.')} Randomize MAC with vendor prefix
    {cyan('4.')} Set a specific MAC address
    {cyan('5.')} Reset to permanent (hardware) MAC
    {cyan('6.')} List available interfaces
    {cyan('7.')} List vendor database
    {cyan('0.')} Exit
  {bold('─' * 46)}
"""


def interactive_menu() -> None:
    """Run the full interactive menu loop."""
    print(BANNER)
    require_root()

    while True:
        print(MENU)
        try:
            choice = input(f"  {bold('Choose an option:')} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{dim('  Goodbye!')}")
            sys.exit(0)

        if choice == "0":
            print(f"\n{dim('  Goodbye!')}\n")
            sys.exit(0)

        elif choice == "1":
            iface = pick_interface()
            if iface:
                op_show(iface)

        elif choice == "2":
            iface = pick_interface()
            if iface:
                op_randomize(iface)

        elif choice == "3":
            # Show vendor list
            vendors = sorted(set(VENDOR_DB.values()))
            print(f"\n  {bold('Known vendors:')}")
            for v in vendors:
                print(f"    {cyan('•')} {v}")
            print()
            iface = pick_interface()
            if not iface:
                continue
            try:
                vendor = input(f"  {bold('Enter vendor name:')} ").strip()
            except (KeyboardInterrupt, EOFError):
                continue
            if vendor:
                op_randomize(iface, vendor)

        elif choice == "4":
            iface = pick_interface()
            if not iface:
                continue
            try:
                mac = input(f"  {bold('Enter MAC address (xx:xx:xx:xx:xx:xx):')} ").strip()
            except (KeyboardInterrupt, EOFError):
                continue
            if mac:
                op_set(iface, mac)

        elif choice == "5":
            iface = pick_interface()
            if iface:
                op_reset(iface)

        elif choice == "6":
            interfaces = list_interfaces()
            print(f"\n  {bold('Network interfaces:')}")
            for iface in interfaces:
                mac     = get_current_mac(iface) or "unknown"
                perm    = get_permanent_mac(iface)
                perm_s  = f"  {dim('perm:')} {yellow(perm)}" if perm else ""
                print(f"    {cyan(iface):<14} {green(mac)}{perm_s}")
            print()

        elif choice == "7":
            print(f"\n  {bold('Vendor database:')}")
            for prefix, name in sorted(VENDOR_DB.items(), key=lambda x: x[1]):
                print(f"    {cyan(prefix)}  {name}")
            print()

        else:
            print(yellow("  [~] Invalid option. Please try again."))


# ─────────────────────────────────────────────────────────────────────────────
# Argument parser
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="macran",
        description=(
            f"{bold('MacRan')} — MAC Address Randomizer & Changer\n"
            "  Author: Monish Kanna S P  |  https://github.com/TENETx0"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  sudo python3 macran.py                          # interactive menu
  sudo python3 macran.py -i eth0 -r              # randomize MAC
  sudo python3 macran.py -i eth0 -m 00:11:22:33:44:55  # set specific MAC
  sudo python3 macran.py -i eth0 -v Intel        # randomize with Intel prefix
  sudo python3 macran.py -i eth0 --show          # show current MAC
  sudo python3 macran.py -i eth0 --reset         # restore permanent MAC
  sudo python3 macran.py reset                   # reset all interfaces (alias)
  sudo python3 macran.py --list-vendors          # print vendor database
        """
    )

    parser.add_argument(
        "-i", "--interface",
        metavar="IFACE",
        help="Target network interface (e.g. eth0, wlan0)"
    )
    parser.add_argument(
        "-r", "--random",
        action="store_true",
        help="Randomize the MAC address"
    )
    parser.add_argument(
        "-m", "--mac",
        metavar="MAC",
        help="Set a specific MAC address (xx:xx:xx:xx:xx:xx)"
    )
    parser.add_argument(
        "-v", "--vendor",
        metavar="VENDOR",
        help="Randomize MAC using a specific vendor prefix (e.g. Intel, Apple)"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the current MAC address of the interface"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Restore the permanent (hardware) MAC address"
    )
    parser.add_argument(
        "--list-interfaces",
        action="store_true",
        help="List all available network interfaces"
    )
    parser.add_argument(
        "--list-vendors",
        action="store_true",
        help="Print the built-in vendor database"
    )

    # Positional "reset" alias: `macran.py reset` or `macran.py reset -i eth0`
    parser.add_argument(
        "command",
        nargs="?",
        choices=["reset"],
        help="Shorthand command (currently: reset)"
    )

    return parser


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    # ── No arguments → interactive menu ─────────────────────────────────────
    no_flags = not any([
        args.interface, args.random, args.mac, args.vendor,
        args.show, args.reset, args.list_interfaces, args.list_vendors,
        args.command
    ])
    if no_flags:
        interactive_menu()
        return

    # ── Informational flags (do NOT need root) ───────────────────────────────
    if args.list_vendors:
        print(f"\n  {bold('Vendor database:')}")
        for prefix, name in sorted(VENDOR_DB.items(), key=lambda x: x[1]):
            print(f"    {cyan(prefix)}  {name}")
        print()
        return

    if args.list_interfaces:
        require_root()
        interfaces = list_interfaces()
        print(f"\n  {bold('Network interfaces:')}")
        for iface in interfaces:
            mac  = get_current_mac(iface) or "unknown"
            perm = get_permanent_mac(iface)
            perm_s = f"  {dim('perm:')} {yellow(perm)}" if perm else ""
            print(f"    {cyan(iface):<14} {green(mac)}{perm_s}")
        print()
        return

    # All remaining operations require root
    require_root()

    # ── Positional "reset" command ───────────────────────────────────────────
    if args.command == "reset":
        if args.interface:
            op_reset(args.interface)
        else:
            # Reset ALL interfaces
            print(BANNER)
            interfaces = list_interfaces()
            if not interfaces:
                print(red("[!] No interfaces found."))
                return
            for iface in interfaces:
                op_reset(iface)
        return

    # ── Interface required from here on ─────────────────────────────────────
    if not args.interface:
        print(red("[!] Please specify an interface with -i / --interface."))
        parser.print_usage()
        sys.exit(1)

    iface = args.interface

    # Validate interface exists
    if not os.path.exists(f"/sys/class/net/{iface}"):
        print(red(f"[!] Interface '{iface}' does not exist."))
        sys.exit(1)

    if args.show:
        op_show(iface)

    elif args.reset:
        op_reset(iface)

    elif args.mac:
        op_set(iface, args.mac)

    elif args.random or args.vendor:
        op_randomize(iface, vendor=args.vendor)

    else:
        print(yellow("[~] No action specified. Use -r, -m, --show, or --reset."))
        parser.print_usage()


if __name__ == "__main__":
    main()
