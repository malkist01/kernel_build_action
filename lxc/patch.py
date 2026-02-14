#!/usr/bin/env python3
"""
Apply LXC patches using sed to kernel source files.
"""

import subprocess
import sys
from pathlib import Path


def find_cgroup_file() -> str:
    """Determine the cgroup file path based on kernel version."""
    if Path("kernel/cgroup.c").exists():
        # Check if it contains the function signature
        content = Path("kernel/cgroup.c").read_text(encoding='utf-8')
        if "int cgroup_add_file" in content:
            return "kernel/cgroup.c"
    return "kernel/cgroup/cgroup.c"


def check_already_patched(file_path: str, patch_type: str) -> bool:
    """Check if the file already contains LXC patches."""
    content = Path(file_path).read_text(encoding='utf-8')

    if patch_type == "cgroup":
        return 'snprintf(name, CGROUP_FILE_NAME_MAX' in content
    if patch_type == "netfilter":
        return "struct rtnl_link_stats64 *stats" in content
    return False


def apply_cgroup_patch(cgroup_file: str) -> None:
    """Apply the cgroup patch using sed."""
    sed_script = r'''/int cgroup_add_file/,/return 0;/{
        /return 0;/i\
    \tif (cft->ss && (cgrp->root->flags & CGRP_ROOT_NOPREFIX) && !(cft->flags & CFTYPE_NO_PREFIX)) {\
        \tsnprintf(name, CGROUP_FILE_NAME_MAX, "%s.%s", cft->ss->name, cft->name);\
        \tkernfs_create_link(cgrp->kn, name, kn);\
    \t}
}'''

    try:
        subprocess.run(
            ["sed", "-i", sed_script, cgroup_file],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Patch applied successfully to {cgroup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error applying cgroup patch: {e}", file=sys.stderr)
        sys.exit(1)


def apply_netfilter_patch() -> None:
    """Apply the xt_qtaguid patch using sed."""
    netfilter_file = "net/netfilter/xt_qtaguid.c"

    # This is a complex sed script that:
    # 1. Changes 'struct rtnl_link_stats64 dev_stats, *stats' to 'struct rtnl_link_stats64 *stats'
    # 2. Adds 'stats = &no_dev_stats;' before the active check
    # 3. Deletes the if block and its next 5 lines
    sed_script = r'''/int iface_stat_fmt_proc_show/,/^}/ {
    s/struct rtnl_link_stats64 dev_stats, \*stats/struct rtnl_link_stats64 *stats/
    /if (iface_entry->active)/i\
    \tstats = \&no_dev_stats;
    /if (iface_entry->active)/,+5d
}'''

    try:
        subprocess.run(
            ["sed", "-i", sed_script, netfilter_file],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Patch applied successfully to {netfilter_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error applying netfilter patch: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    cgroup = find_cgroup_file()

    patch_files = [
        (cgroup, "cgroup"),
        ("net/netfilter/xt_qtaguid.c", "netfilter")
    ]

    for file_path, patch_type in patch_files:
        if not Path(file_path).exists():
            print(f"Warning: {file_path} not found, skipping", file=sys.stderr)
            continue

        if check_already_patched(file_path, patch_type):
            print(f"Warning: {file_path} contains LXC")
            continue

        if patch_type == "cgroup":
            apply_cgroup_patch(file_path)
        elif patch_type == "netfilter":
            apply_netfilter_patch()


if __name__ == "__main__":
    main()
