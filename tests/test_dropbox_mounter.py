from dropbox_mounter import (
    DRIVE_MOUNT,
    FOLDER_MOUNT,
    REMOTE,
    MountConfig,
    build_mount_command,
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
