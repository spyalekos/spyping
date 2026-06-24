# Repository Guidelines

## Project Structure & Module Organization

spyping is a small Python/Flet Android app. Main code lives in `src/`: `src/main.py` contains the app flow and periodic ping loop, `src/version.py` stores app metadata, and packaged assets belong in `src/assets/`. Android packaging is driven by `pyproject.toml` with `[tool.flet.app] path = "src"` and by `build_apk.sh`.

## Build, Test, and Development Commands

- `uv run flet run` runs the desktop app.
- `uv run flet run --web` runs the web target.
- `uv run flet run --android src/main.py` starts Android live debugging when needed.
- `uv run python -m compileall src` performs the baseline Python compile check.
- `bash -n build_apk.sh` validates APK build script syntax.
- `./build_apk.sh` is the only approved APK build path.

Do not run `flet build apk` directly; the script applies required Android build metadata and memory limits.

## Coding Style & Naming Conventions

Use Python 3.10+ and the existing Flet style: 4-space indentation, descriptive snake_case functions/variables, PascalCase classes, and concise comments only where behavior is non-obvious. Keep the app name as `spyping`. Manage dependencies only with `uv`; do not use bare `pip`. Desktop-only dependencies belong in `[dependency-groups] dev`, not base `dependencies`.

Flet services must be mounted only through `page.services`; never clear `page.services` or monkeypatch `_c`.

## Testing Guidelines

There is no dedicated test suite currently. For code changes, run `uv run python -m compileall src`. For build-script edits, also run `bash -n build_apk.sh`. If Android behavior changes, smoke test on a device when available: build with `./build_apk.sh`, install `build/apk/spyping.apk`, launch the app, and check logcat for tracebacks, fatal errors, ANRs, `Unknown control`, and `RangeError`.

## Commit & Pull Request Guidelines

Keep commits focused and use short imperative summaries. Pull requests should describe the behavior change, list validation, Android/Desktop impact, and screenshots or device notes for visible UI changes.

## Agent-Specific Instructions

Read `AI-Instructions.md` before substantial work. Do not revert existing uncommitted changes unless explicitly asked. Keep Android runtime storage out of packaged assets. The monitoring wakelock is a Flet service and must stay in `page.services`.
