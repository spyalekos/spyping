# spyping 1.0.9

`spyping` is a small Android app, written with Python/Flet, that periodically pings an IP address or host configured inside the app.

Greek documentation: [README.md](README.md)

## What It Does

- Pings an IP address or host entered in the UI.
- Lets you configure the ping interval in seconds.
- Defaults to `8.8.8.8` every `300` seconds.
- Supports manual `Ping now`.
- Keeps up to the latest `1000` results in history.
- Keeps an Android wakelock while monitoring is running so the app does not stop because of idle sleep.
- Detects Android `Operation not permitted` when a locked device blocks ping and shows a clear instruction for Unrestricted battery/device-idle whitelist.
- Stores target, interval, and language in app storage.
- Starts in Greek by default and includes a Greek/English language toggle icon.
- Includes a help icon with short in-app instructions.

## Android

Package/activity:

```text
gr.spyalekos.spyping/.MainActivity
```

Permissions:

- `android.permission.INTERNET`
- `android.permission.ACCESS_NETWORK_STATE`
- `android.permission.WAKE_LOCK`
- `android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`

## Development

Requirements:

- Python 3.10+
- `uv`
- Flet/Flet CLI through the project dependencies
- Android SDK/ADB for device deployment

Install dependencies:

```bash
uv sync
```

Desktop/dev run:

```bash
uv run flet run
```

Web/dev run:

```bash
uv run flet run --web
```

## Version

Current version: `1.0.9`

When the version changes, keep these files synchronized:

- `pyproject.toml`
- `src/version.py`
- `README.md`
- `ENGLISH.md`
- `uv.lock`
