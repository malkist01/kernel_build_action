#!/usr/bin/env python3
"""
Clean up build artifacts and temporary files after kernel build.
Supports both Debian-based and ArchLinux-based systems.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command."""
    try:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {e.stderr}", file=sys.stderr)
        raise


def detect_package_manager() -> str:
    """Detect the package manager (apt or pacman)."""
    if Path("/bin/apt").exists() or Path("/usr/bin/apt").exists():
        return "apt"
    if Path("/bin/pacman").exists() or Path("/usr/bin/pacman").exists():
        return "pacman"
    return "unknown"


def clean_kernel_source(kernel_dir: Path) -> None:
    """Clean kernel source directory."""
    if kernel_dir.exists():
        print(f"Removing kernel directory: {kernel_dir}")
        shutil.rmtree(kernel_dir)


def clean_build_artifacts(build_dir: Path) -> None:
    """Clean build artifacts."""
    if build_dir.exists():
        print(f"Removing build directory: {build_dir}")
        shutil.rmtree(build_dir)


def clean_toolchains() -> None:
    """Clean downloaded toolchains."""
    home = Path.home()
    toolchains = [
        home / "clang",
        home / "gcc-64",
        home / "gcc-32",
    ]
    for toolchain in toolchains:
        if toolchain.exists():
            print(f"Removing toolchain: {toolchain}")
            shutil.rmtree(toolchain)


def clean_anykernel3() -> None:
    """Clean AnyKernel3 directory."""
    anykernel_dir = Path("AnyKernel3")
    if anykernel_dir.exists():
        print(f"Removing AnyKernel3 directory: {anykernel_dir}")
        shutil.rmtree(anykernel_dir)


def clean_ccache() -> None:
    """Clean ccache."""
    result = run_command(["ccache", "-C"], check=False)
    if result.returncode == 0:
        print("Ccache cleared")


def clean_env_vars() -> None:
    """Clean build-related environment variables.

    Note: This function prints unset commands to stdout for shell evaluation.
    Use: eval $(python3 clean.py --env)
    """
    env_vars = [
        "CMD_PATH", "CMD_CC", "CMD_CLANG_TRIPLE", "CMD_CROSS_COMPILE",
        "CMD_CROSS_COMPILE_ARM32", "USE_CCACHE", "CLANG_PATH", "HOMES",
        "KVER", "SWAP_FILE", "SUBLEVEL", "PATCHLEVEL", "VERSION", "GCC_DIR",
        "FILE", "FILE_NAME", "MATCHED_DIR", "FOLDER", "FOLDER_NAME",
        "GCC64", "GCC32", "NEED_GCC", "AOSP_CLANG_URL", "OTHER_CLANG_URL",
        "AOSP_GCC64_URL", "AOSP_GCC32_URL", "AOSP_GCC_BRANCH",
        "OTHER_GCC64_URL", "OTHER_GCC32_URL", "EXTRA_ARGS", "make_args",
        "SAFE_EXTRA_ARGS", "EXTRA_CMD", "FMT", "HOST_ARCH"
    ]
    for var in env_vars:
        if var in os.environ:
            print(f"unset {var}")


def clean_temp_files() -> None:
    """Clean temporary files."""
    temp_files = [
        Path("boot.img"),
        Path("magiskboot"),
        Path("nohup.out"),
    ]
    for file in temp_files:
        if file.exists():
            print(f"Removing temporary file: {file}")
            if file.is_dir():
                shutil.rmtree(file)
            else:
                file.unlink()


def clean_all(kernel_dir: str = "kernel", build_dir: str = "build") -> None:
    """Clean all build artifacts."""
    print("Cleaning all build artifacts...")
    clean_kernel_source(Path(kernel_dir))
    clean_build_artifacts(Path(build_dir))
    clean_toolchains()
    clean_anykernel3()
    clean_temp_files()
    clean_env_vars()
    print("Clean completed!")


def main() -> None:
    """Main entry point for the cleanup script."""
    parser = argparse.ArgumentParser(
        description="Clean up build artifacts and temporary files"
    )
    parser.add_argument(
        "--kernel-dir",
        default="kernel",
        help="Kernel source directory (default: kernel)",
    )
    parser.add_argument(
        "--build-dir",
        default="build",
        help="Build output directory (default: build)",
    )
    parser.add_argument(
        "--toolchains",
        action="store_true",
        help="Clean downloaded toolchains",
    )
    parser.add_argument(
        "--ccache",
        action="store_true",
        help="Clean ccache",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Clean everything including toolchains and ccache",
    )
    parser.add_argument(
        "--env",
        action="store_true",
        help="Clean build-related environment variables",
    )

    args = parser.parse_args()

    if args.all:
        clean_all(args.kernel_dir, args.build_dir)
        clean_ccache()
    else:
        clean_kernel_source(Path(args.kernel_dir))
        clean_build_artifacts(Path(args.build_dir))
        clean_anykernel3()
        clean_temp_files()

        if args.toolchains:
            clean_toolchains()

        if args.ccache:
            clean_ccache()

        if args.env:
            print("# Run: eval $(python3 clean.py --env)", file=sys.stderr)
            clean_env_vars()
            return  # Exit early to avoid extra output when sourcing

    # Detect package manager for info
    pkg_mgr = detect_package_manager()
    print(f"Detected package manager: {pkg_mgr}")


if __name__ == "__main__":
    main()
