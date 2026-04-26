"""Windows Dropbox rclone auto-mount helper.

Supports:
- Starting mounts immediately.
- Installing Windows services (auto start at boot) for both mounts.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

REMOTE = "dropbox:"
DRIVE_MOUNT = r"Z:"
FOLDER_MOUNT = r"C:\mount\dropbox"

SERVICE_Z = "RcloneDropboxDriveZ"
SERVICE_FOLDER = "RcloneDropboxFolder"


@dataclass(frozen=True)
class MountConfig:
    remote: str
    mountpoint: str


def build_mount_command(config: MountConfig) -> list[str]:
    """Return the rclone mount command for a mount config."""
    return ["rclone", "mount", config.remote, config.mountpoint, "--vfs-cache-mode", "writes"]


def ensure_mount_folder(path: str) -> None:
    """Create the target folder for folder mounts if needed."""
    Path(path).mkdir(parents=True, exist_ok=True)


def start_mount(config: MountConfig) -> subprocess.Popen[str]:
    """Start an rclone mount process."""
    flags = 0
    if os.name == "nt":
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return subprocess.Popen(  # noqa: S603
        build_mount_command(config),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
        text=True,
    )


def mount_dropbox() -> tuple[subprocess.Popen[str], subprocess.Popen[str]]:
    """Mount dropbox: to both Z: and C:\\mount\\dropbox right now."""
    if os.name != "nt":
        raise RuntimeError("This app is intended to run on Windows.")

    ensure_mount_folder(FOLDER_MOUNT)
    proc_drive = start_mount(MountConfig(remote=REMOTE, mountpoint=DRIVE_MOUNT))
    proc_folder = start_mount(MountConfig(remote=REMOTE, mountpoint=FOLDER_MOUNT))
    return proc_drive, proc_folder


def build_service_binpath(config: MountConfig, rclone_path: str = "rclone.exe") -> str:
    """Build `sc create` binPath value for one mount service."""
    return subprocess.list2cmdline([rclone_path, "mount", config.remote, config.mountpoint, "--vfs-cache-mode", "writes"])


def install_windows_service(service_name: str, config: MountConfig, rclone_path: str = "rclone.exe") -> None:
    """Install or update a Windows service with auto-start startup type."""
    if os.name != "nt":
        raise RuntimeError("Service installation is only supported on Windows.")

    binpath = build_service_binpath(config, rclone_path=rclone_path)

    subprocess.run(["sc.exe", "stop", service_name], check=False)  # noqa: S603
    subprocess.run(["sc.exe", "delete", service_name], check=False)  # noqa: S603

    create_cmd = [
        "sc.exe",
        "create",
        service_name,
        f"binPath= {binpath}",
        "start= auto",
        "DisplayName= Rclone Dropbox Mount",
    ]
    subprocess.run(create_cmd, check=True)  # noqa: S603
    subprocess.run(["sc.exe", "description", service_name, f"Mounts {config.remote} to {config.mountpoint}"], check=True)  # noqa: S603
    subprocess.run(["sc.exe", "start", service_name], check=True)  # noqa: S603


def install_autostart_services(rclone_path: str = "rclone.exe") -> None:
    """Install and start both Dropbox mount services."""
    ensure_mount_folder(FOLDER_MOUNT)
    install_windows_service(SERVICE_Z, MountConfig(remote=REMOTE, mountpoint=DRIVE_MOUNT), rclone_path=rclone_path)
    install_windows_service(
        SERVICE_FOLDER,
        MountConfig(remote=REMOTE, mountpoint=FOLDER_MOUNT),
        rclone_path=rclone_path,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dropbox rclone mounter")
    parser.add_argument("--headless", action="store_true", help="Start the two mounts immediately")
    parser.add_argument(
        "--install-service",
        action="store_true",
        help="Install two auto-start Windows services and start them now",
    )
    parser.add_argument(
        "--rclone-path",
        default="rclone.exe",
        help="Path to rclone executable (used for service installation)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.install_service:
        install_autostart_services(rclone_path=args.rclone_path)
        print("Installed and started auto-start services for Z: and C:\\mount\\dropbox.")
        return 0

    if args.headless:
        mount_dropbox()
        print("Started both rclone mount processes.")
        return 0

    print("No action selected. Use --install-service or --headless.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
