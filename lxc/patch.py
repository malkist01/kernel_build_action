#!/usr/bin/env python3
"""
Apply LXC patches to kernel source files using pure Python.
"""

import sys
from pathlib import Path


def find_cgroup_file() -> str:
    """Determine the cgroup file path based on kernel version."""
    cgroup_path = Path("kernel/cgroup.c")
    if cgroup_path.exists():
        content = cgroup_path.read_text(encoding='utf-8')
        if "int cgroup_add_file" in content:
            return "kernel/cgroup.c"
    return "kernel/cgroup/cgroup.c"


def check_already_patched(file_path: str, patch_type: str) -> bool:
    """Check if the file already contains LXC patches."""
    path = Path(file_path)
    if not path.exists():
        return False

    content = path.read_text(encoding='utf-8')

    if patch_type == "cgroup":
        return 'snprintf(name, CGROUP_FILE_NAME_MAX' in content
    if patch_type == "netfilter":
        return "struct rtnl_link_stats64 *stats" in content
    return False


def apply_cgroup_patch(cgroup_file: str) -> None:
    """Apply the cgroup patch using pure Python."""
    path = Path(cgroup_file)
    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Find the cgroup_add_file function and insert the patch before return 0;
    new_lines = []
    in_function = False
    brace_count = 0
    inserted = False

    for line in lines:
        stripped = line.strip()

        # Check if we're entering the cgroup_add_file function
        if "int cgroup_add_file" in stripped:
            in_function = True

        if in_function and not inserted:
            # Count braces to track function scope
            brace_count += stripped.count('{')
            brace_count -= stripped.count('}')

            # Look for "return 0;" within the function
            if stripped == "return 0;" and brace_count > 0:
                # Insert the patch before return 0;
                indent = len(line) - len(line.lstrip())
                base_indent = ' ' * indent

                patch_code = [
                    f"{base_indent}if (cft->ss && (cgrp->root->flags & CGRP_ROOT_NOPREFIX) && !(cft->flags & CFTYPE_NO_PREFIX)) {{",
                    f"{base_indent}    snprintf(name, CGROUP_FILE_NAME_MAX, \"%s.%s\", cft->ss->name, cft->name);",
                    f"{base_indent}    kernfs_create_link(cgrp->kn, name, kn);",
                    f"{base_indent}}}",
                ]
                new_lines.extend(patch_code)
                inserted = True

        new_lines.append(line)

    if not inserted:
        print(f"Warning: Could not find insertion point in {cgroup_file}", file=sys.stderr)
        return

    path.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"Patch applied successfully to {cgroup_file}")


def apply_netfilter_patch() -> None:
    """Apply the xt_qtaguid patch using pure Python."""
    netfilter_file = Path("net/netfilter/xt_qtaguid.c")

    if not netfilter_file.exists():
        print(f"Error: {netfilter_file} not found", file=sys.stderr)
        return

    content = netfilter_file.read_text(encoding='utf-8')
    lines = content.split('\n')

    new_lines = []
    in_function = False
    brace_count = 0
    modified = False
    skip_lines = 0

    for line in lines:
        if skip_lines > 0:
            skip_lines -= 1
            continue

        stripped = line.strip()

        # Check if we're entering iface_stat_fmt_proc_show function
        if "int iface_stat_fmt_proc_show" in stripped:
            in_function = True

        if in_function and not modified:
            # Track braces within the function
            brace_count += stripped.count('{')
            brace_count -= stripped.count('}')

            # Replace variable declaration
            if "struct rtnl_link_stats64 dev_stats, *stats" in line:
                line = line.replace(
                    "struct rtnl_link_stats64 dev_stats, *stats",
                    "struct rtnl_link_stats64 *stats"
                )

            # Insert stats assignment before the active check
            if "if (iface_entry->active)" in line:
                indent = len(line) - len(line.lstrip())
                base_indent = ' ' * indent
                new_lines.append(f"{base_indent}stats = &no_dev_stats;")

                # Skip the if block and next 5 lines
                skip_lines = 5
                modified = True
                continue

        new_lines.append(line)

    if not modified:
        print(f"Warning: Could not apply netfilter patch", file=sys.stderr)
        return

    netfilter_file.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"Patch applied successfully to {netfilter_file}")


def main() -> None:
    """Main function"""
    cgroup = find_cgroup_file()

    patch_files = [
        (cgroup, "cgroup"),
        ("net/netfilter/xt_qtaguid.c", "netfilter")
    ]

    for file_path, patch_type in patch_files:
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: {file_path} not found, skipping", file=sys.stderr)
            continue

        if check_already_patched(file_path, patch_type):
            print(f"Warning: {file_path} already contains LXC patches, skipping")
            continue

        if patch_type == "cgroup":
            apply_cgroup_patch(file_path)
        elif patch_type == "netfilter":
            apply_netfilter_patch()


if __name__ == "__main__":
    main()
