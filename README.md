# Dropbox Rclone Mounter (Windows Service + Boot Auto-Mount)

This project mounts the same `dropbox:` rclone remote to both:

- `Z:`
- `C:\mount\dropbox`

It now supports **Windows service installation** so mounts start automatically on boot.

## Requirements

- Windows
- [rclone](https://rclone.org/) installed
- A configured remote named `dropbox`
- Run install command from an elevated shell (Administrator)

## Install as auto-start Windows services

```bash
python dropbox_mounter.py --install-service --rclone-path "C:\Program Files\rclone\rclone.exe"
```

What this does:

- creates `C:\mount\dropbox` if needed
- installs two Windows services:
  - `RcloneDropboxDriveZ` (mounts to `Z:`)
  - `RcloneDropboxFolder` (mounts to `C:\mount\dropbox`)
- configures both services as `start= auto`
- starts both services immediately

After this, both mounts are re-established on system boot automatically.

## One-time immediate mounts (no service install)

```bash
python dropbox_mounter.py --headless
```
