from dropbox_mounter import (
    DRIVE_MOUNT,
    FOLDER_MOUNT,
    REMOTE,
    MountConfig,
    build_mount_command,
    build_service_binpath,
)


def test_build_mount_command_drive() -> None:
    cmd = build_mount_command(MountConfig(remote=REMOTE, mountpoint=DRIVE_MOUNT))
    assert cmd == ["rclone", "mount", "dropbox:", r"Z:", "--vfs-cache-mode", "writes"]


def test_build_mount_command_folder() -> None:
    cmd = build_mount_command(MountConfig(remote=REMOTE, mountpoint=FOLDER_MOUNT))
    assert cmd == [
        "rclone",
        "mount",
        "dropbox:",
        r"C:\mount\dropbox",
        "--vfs-cache-mode",
        "writes",
    ]


def test_build_service_binpath_uses_rclone_path() -> None:
    cmdline = build_service_binpath(
        MountConfig(remote=REMOTE, mountpoint=DRIVE_MOUNT),
        rclone_path=r"C:\Program Files\rclone\rclone.exe",
    )
    assert "C:\\Program Files\\rclone\\rclone.exe" in cmdline
    assert "mount dropbox:" in cmdline
    assert "Z:" in cmdline
