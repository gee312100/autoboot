# Dropbox Rclone Mounter (Windows)

This app starts two `rclone mount` processes for the same Dropbox remote:

- `dropbox:` -> `Z:`
- `dropbox:` -> `C:\mount\dropbox`

## Requirements

- Windows
- [rclone](https://rclone.org/) installed and available in `PATH`
- A configured Dropbox remote named `dropbox`

## Run (GUI)

```bash
python dropbox_mounter.py
```

Click **Mount Dropbox**.

## Run (headless)

```bash
python dropbox_mounter.py --headless
```

## Notes

- The app creates `C:\mount\dropbox` if it does not exist.
- It launches two background `rclone mount` processes.
