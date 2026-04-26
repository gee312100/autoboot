"""Simple Windows app to mount Dropbox via rclone.

Mount targets:
- Z:
- C:\\mount\\dropbox
"""

from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox

REMOTE = "dropbox:"
DRIVE_MOUNT = r"Z:"
FOLDER_MOUNT = r"C:\mount\dropbox"


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
    """Mount dropbox: to both Z: and C:\\mount\\dropbox."""
    if os.name != "nt":
        raise RuntimeError("This app is intended to run on Windows.")

    ensure_mount_folder(FOLDER_MOUNT)
    proc_drive = start_mount(MountConfig(remote=REMOTE, mountpoint=DRIVE_MOUNT))
    proc_folder = start_mount(MountConfig(remote=REMOTE, mountpoint=FOLDER_MOUNT))
    return proc_drive, proc_folder


class DropboxMounterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Dropbox Rclone Mounter")
        root.geometry("420x170")

        tk.Label(
            root,
            text="Mount dropbox: to Z: and C:\\mount\\dropbox",
            padx=10,
            pady=20,
        ).pack()

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var).pack(pady=(0, 10))

        tk.Button(root, text="Mount Dropbox", command=self.on_mount_click, width=20).pack()

    def on_mount_click(self) -> None:
        try:
            mount_dropbox()
        except FileNotFoundError:
            messagebox.showerror("Error", "rclone was not found in PATH.")
            self.status_var.set("Failed: rclone not found")
            return
        except RuntimeError as exc:
            messagebox.showerror("Error", str(exc))
            self.status_var.set("Failed: not on Windows")
            return
        except OSError as exc:
            messagebox.showerror("Error", f"Failed to start mount: {exc}")
            self.status_var.set("Failed to start mounts")
            return

        self.status_var.set("Mount processes started for Z: and C:\\mount\\dropbox")
        messagebox.showinfo("Success", "Started both rclone mount processes.")


def main() -> int:
    if "--headless" in sys.argv:
        mount_dropbox()
        print("Started both rclone mount processes.")
        return 0

    root = tk.Tk()
    DropboxMounterApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
