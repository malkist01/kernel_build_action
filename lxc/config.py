#!/usr/bin/env python3
"""
Check and configure kernel config options for LXC/Docker support.
"""

import argparse
import re
import sys
from pathlib import Path


CONFIGS_ON = """
CONFIG_NAMESPACES
CONFIG_MULTIUSER
CONFIG_NET
CONFIG_NET_NS
CONFIG_PID_NS
CONFIG_POSIX_MQUEUE
CONFIG_IPC_NS
CONFIG_UTS_NS
CONFIG_CGROUPS
CONFIG_SCHED_AUTOGROUP
CONFIG_CGROUP_CPUACCT
CONFIG_CGROUP_DEVICE
CONFIG_CGROUP_FREEZER
CONFIG_CGROUP_SCHED
CONFIG_DEBUG_BLK_CGROUP
CONFIG_NETFILTER_XT_MATCH_BPF
CONFIG_CPUSETS
CONFIG_MEMCG
CONFIG_KEYS
CONFIG_NETDEVICES
CONFIG_NET_CORE
CONFIG_VETH
CONFIG_IPV6
CONFIG_IP6_NF_NAT
CONFIG_IP6_NF_TARGET_MASQUERADE
CONFIG_BRIDGE
CONFIG_NETFILTER
CONFIG_INET
CONFIG_NETFILTER_ADVANCED
CONFIG_BRIDGE_NETFILTER
CONFIG_IP_NF_FILTER
CONFIG_IP_NF_IPTABLES
CONFIG_IP_NF_NAT
CONFIG_IP_NF_TARGET_MASQUERADE
CONFIG_NETFILTER_XTABLES
CONFIG_NETFILTER_XT_MATCH_ADDRTYPE
CONFIG_NETFILTER_XT_MATCH_CONNTRACK
CONFIG_NF_CONNTRACK
CONFIG_NETFILTER_XT_MATCH_IPVS
CONFIG_IP_VS
CONFIG_NETFILTER_XT_MARK
CONFIG_NF_NAT
CONFIG_POSIX_MQUEUE
CONFIG_NF_NAT_IPV6
CONFIG_NF_NAT_IPV4
CONFIG_NF_CONNTRACK_IPV4
CONFIG_NF_CONNTRACK_IPV6
CONFIG_NF_NAT_NEEDED
CONFIG_BPF
CONFIG_CGROUP_BPF
CONFIG_BPF_SYSCALL
CONFIG_USER_NS
CONFIG_SECCOMP
CONFIG_SECCOMP_FILTER
CONFIG_CGROUP_PIDS
CONFIG_CGROUP_DEBUG
CONFIG_SWAP
CONFIG_MEMCG_SWAP
CONFIG_MEMCG_SWAP_ENABLED
CONFIG_BLOCK
CONFIG_IOSCHED_CFQ
CONFIG_BLK_CGROUP
CONFIG_CFQ_GROUP_IOSCHED
CONFIG_BLK_DEV_THROTTLING
CONFIG_PERF_EVENTS
CONFIG_CGROUP_PERF
CONFIG_HUGETLBFS
CONFIG_HUGETLB_PAGE
CONFIG_CGROUP_HUGETLB
CONFIG_NET_SCHED
CONFIG_NET_CLS_CGROUP
CONFIG_CGROUP_NET_PRIO
CONFIG_FAIR_GROUP_SCHED
CONFIG_RT_GROUP_SCHED
CONFIG_IP_NF_TARGET_REDIRECT
CONFIG_IP_VS_NFCT
CONFIG_IP_VS_PROTO_TCP
CONFIG_IP_VS_PROTO_UDP
CONFIG_IP_VS_RR
CONFIG_SECURITY
CONFIG_SECURITY_SELINUX
CONFIG_SECURITY_APPARMOR
CONFIG_EXT3_FS
CONFIG_EXT3_FS_POSIX_ACL
CONFIG_EXT3_FS_SECURITY
CONFIG_EXT4_FS
CONFIG_EXT4_FS_POSIX_ACL
CONFIG_EXT4_FS_SECURITY
CONFIG_VXLAN
CONFIG_BRIDGE
CONFIG_BRIDGE_VLAN_FILTERING
CONFIG_VLAN_8021Q
CONFIG_CRYPTO
CONFIG_CRYPTO_AEAD
CONFIG_CRYPTO_GCM
CONFIG_CRYPTO_SEQIV
CONFIG_CRYPTO_GHASH
CONFIG_CHECKPOINT_RESTORE
CONFIG_XFRM
CONFIG_XFRM_USER
CONFIG_XFRM_ALGO
CONFIG_INET_ESP
CONFIG_INET_XFRM_MODE_TRANSPORT
CONFIG_IPVLAN
CONFIG_MACVLAN
CONFIG_NET_L3_MASTER_DEV
CONFIG_DUMMY
CONFIG_NF_NAT_FTP
CONFIG_NF_CONNTRACK_FTP
CONFIG_NF_NAT_TFTP
CONFIG_NF_CONNTRACK_TFTP
CONFIG_AUFS_FS
CONFIG_BTRFS_FS
CONFIG_BTRFS_FS_POSIX_ACL
CONFIG_MD
CONFIG_BLK_DEV_DM
CONFIG_DM_THIN_PROVISIONING
CONFIG_OVERLAY_FS
CONFIG_PACKET
CONFIG_PACKET_DIAG
CONFIG_NETLINK_DIAG
CONFIG_FHANDLE
CONFIG_UNIX
CONFIG_UNIX_DIAG
CONFIG_NETFILTER_XT_TARGET_CHECKSUM
CONFIG_CFS_BANDWIDTH
"""

CONFIGS_OFF = """
CONFIG_ANDROID_PARANOID_NETWORK
CONFIG_SCHED_WALT
"""

CONFIGS_EQ = ""


def color_red(text: str) -> str:
    """Return text wrapped in red ANSI color codes."""
    return f"\033[31m{text}\033[0m"


def color_green(text: str) -> str:
    """Return text wrapped in green ANSI color codes."""
    return f"\033[32m{text}\033[0m"


def color_white(text: str) -> str:
    """Return text wrapped in white ANSI color codes."""
    return f"\033[37m{text}\033[0m"


def parse_configs(config_text: str) -> list[str]:
    """Parse config list into individual items."""
    return [line.strip() for line in config_text.strip().split('\n') if line.strip()]


def count_config_occurrences(config_file: Path, config: str) -> int:
    """Count how many times a config appears in the file."""
    content = config_file.read_text(encoding='utf-8')
    # Use word boundary matching
    pattern = r'\b' + re.escape(config) + r'\b'
    return len(re.findall(pattern, content))


def is_config_enabled(config_file: Path, config: str) -> bool:
    """Check if a config is enabled (=y or =m)."""
    content = config_file.read_text(encoding='utf-8')
    pattern = rf'^{re.escape(config)}=(y|m)$'
    return bool(re.search(pattern, content, re.MULTILINE))


def is_config_set(config_file: Path, config: str) -> bool:
    """Check if a config line exists in the file."""
    content = config_file.read_text(encoding='utf-8')
    pattern = rf'^{re.escape(config)}=.*$'
    return bool(re.search(pattern, content, re.MULTILINE))


def add_config_not_set(config_file: Path, config: str) -> None:
    """Add '# CONFIG_XXX is not set' to the file."""
    with open(config_file, 'a', encoding='utf-8') as f:
        f.write(f"# {config} is not set\n")


def enable_config(config_file: Path, config: str) -> None:
    """Enable a config by replacing '# CONFIG_XXX is not set' with 'CONFIG_XXX=y'."""
    content = config_file.read_text(encoding='utf-8')
    pattern = rf'^# {re.escape(config)} is not set$'
    replacement = f'{config}=y'
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    config_file.write_text(new_content, encoding='utf-8')


def disable_config(config_file: Path, config: str) -> None:
    """Disable a config by replacing 'CONFIG_XXX=...' with '# CONFIG_XXX is not set'."""
    content = config_file.read_text(encoding='utf-8')
    pattern = rf'^{re.escape(config)}=.*$'
    replacement = f'# {config} is not set'
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    config_file.write_text(new_content, encoding='utf-8')


def get_config_value(config_file: Path, config: str) -> str | None:
    """Get the current value of a config."""
    content = config_file.read_text(encoding='utf-8')
    pattern = rf'^{re.escape(config)}=(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1) if match else None


def main() -> None:
    """Main entry point for checking and configuring LXC/Docker kernel options."""
    parser = argparse.ArgumentParser(description='Check and configure kernel for LXC/Docker')
    parser.add_argument('config_file', help='Path to kernel config file')
    parser.add_argument('-w', action='store_true', help='Write changes to config file')
    args = parser.parse_args()

    config_file = Path(args.config_file).resolve()
    write_mode = args.w

    if not config_file.is_relative_to(Path.cwd()):
        print("Error: Config file must be within the current directory")
        sys.exit(1)

    if not config_file.exists():
        print("Provide a config file as argument")
        sys.exit(1)

    configs_on = parse_configs(CONFIGS_ON)
    configs_off = parse_configs(CONFIGS_OFF)
    configs_eq = parse_configs(CONFIGS_EQ)

    print("\n\nChecking config file for https://github.com/wu17481748/lxc-docker specific config options.\n\n")

    errors = 0
    fixes = 0

    # Check all configs exist
    for config in configs_on + configs_off:
        count = count_config_occurrences(config_file, config)
        if count > 1:
            print(color_red(f"{config} appears more than once in the config file, fix this"))
            errors += 1

        if count == 0:
            if write_mode:
                print(color_white(f"Creating {config}"))
                add_config_not_set(config_file, config)
                fixes += 1
            else:
                print(color_red(f"{config} is neither enabled nor disabled in the config file"))
                errors += 1

    # Enable configs that should be on
    for config in configs_on:
        if is_config_enabled(config_file, config):
            print(color_green(f"{config} is already set"))
        else:
            if write_mode:
                print(color_white(f"Setting {config}"))
                enable_config(config_file, config)
                fixes += 1
            else:
                print(color_red(f"{config} is not set, set it"))
                errors += 1

    # Handle CONFIGS_EQ (equality checks)
    for config in configs_eq:
        if '=' not in config:
            continue
        lhs, rhs = config.split('=', 1)

        if is_config_set(config_file, config):
            print(color_green(f"{config} is already set correctly."))
            continue

        if is_config_set(config_file, lhs):
            cur = get_config_value(config_file, lhs)
            print(color_red(f"{lhs} is set, but to {cur} not {rhs}."))
            if write_mode:
                print(color_green(f"Setting {config} correctly"))
                content = config_file.read_text(encoding='utf-8')
                pattern = rf'^{re.escape(lhs)}=.*$'
                replacement = f'# {lhs} was {cur}\n{config}'
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                config_file.write_text(new_content, encoding='utf-8')
                fixes += 1
        else:
            if write_mode:
                print(color_white(f"Setting {config}"))
                with open(config_file, 'a', encoding='utf-8') as f:
                    f.write(f"{config}\n")
                fixes += 1
            else:
                print(color_red(f"{config} is not set"))
                errors += 1

    # Disable configs that should be off
    for config in configs_off:
        if is_config_enabled(config_file, config):
            if write_mode:
                print(color_white(f"Unsetting {config}"))
                disable_config(config_file, config)
                fixes += 1
            else:
                print(color_red(f"{config} is set, unset it"))
                errors += 1
        else:
            print(color_green(f"{config} is already unset"))

    if errors == 0:
        print(color_green(f"\n\nConfig file checked, found no errors.\n\n"))
    else:
        print(color_red(f"\n\nConfig file checked, found {errors} errors that I did not fix.\n\n"))

    if fixes > 0:
        print(color_green(f"开启docker-lxc配置 {fixes} 项.\n\n"))


if __name__ == "__main__":
    main()
