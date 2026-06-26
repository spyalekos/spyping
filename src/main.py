import asyncio
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import flet as ft

from version import APP_NAME, APP_VERSION


DEFAULT_TARGET = "8.8.8.8"
DEFAULT_INTERVAL_SECONDS = 300
DEFAULT_LANGUAGE = "el"
MIN_INTERVAL_SECONDS = 5
PING_TIMEOUT_SECONDS = 3
ANDROID_PERMISSION_DENIED_MARKER = "operation not permitted"
MAX_HISTORY_ITEMS = 1000
CONFIG_FILENAME = "settings.json"

TEXT = {
    "el": {
        "starting": "Εκκίνηση...",
        "target_label": "IP ή host",
        "interval_label": "Διάστημα σε δευτερόλεπτα",
        "idle_title": "Αναμονή",
        "idle_detail": "Όρισε στόχο και ξεκίνα την παρακολούθηση.",
        "start": "Έναρξη",
        "stop": "Διακοπή",
        "ping_now": "Ping τώρα",
        "history": "Ιστορικό",
        "online": "Online",
        "no_reply": "Χωρίς απάντηση",
        "checking": "Έλεγχος",
        "config_error": "Λάθος ρύθμισης",
        "android_restriction": "Περιορισμός Android",
        "next_ping_empty": "Επόμενο ping: -",
        "next_ping_in": "Επόμενο ping σε {duration}",
        "wakelock_on": "Wakelock: ενεργό",
        "wakelock_off": "Wakelock: ανενεργό",
        "wakelock_error": "Σφάλμα wakelock: {error}",
        "pinging": "Ping στο {target}...",
        "target_required": "Συμπλήρωσε IP ή host.",
        "target_invalid": "Ο στόχος περιέχει μη υποστηριζόμενους χαρακτήρες.",
        "interval_invalid": "Το διάστημα πρέπει να είναι ακέραιος αριθμός δευτερολέπτων.",
        "interval_too_low": "Το διάστημα πρέπει να είναι τουλάχιστον {minimum} δευτερόλεπτα.",
        "ping_missing": "Δεν βρέθηκε η εντολή ping στο σύστημα.",
        "ping_timeout": "Το ping έληξε από timeout.",
        "ping_failed": "Το ping απέτυχε: {error}",
        "background_network_blocked": "Το Android μπλόκαρε το ping όταν η συσκευή ήταν κλειδωμένη. Βάλε την εφαρμογή σε Unrestricted battery ή device-idle whitelist.",
        "reply_received": "λήφθηκε απάντηση",
        "language_tooltip": "Αλλαγή γλώσσας",
        "help_tooltip": "Βοήθεια",
        "help_title": "Βοήθεια",
        "help_close": "Κλείσιμο",
        "help_lines": [
            "Συμπλήρωσε IP ή host στο πρώτο πεδίο.",
            "Στο δεύτερο πεδίο ορίζεις κάθε πόσα δευτερόλεπτα θα γίνεται ping. Η προεπιλογή είναι 300.",
            "Η Έναρξη ξεκινά περιοδικό ping και απενεργοποιεί το χειροκίνητο Ping τώρα μέχρι τη Διακοπή.",
            "Το Wakelock μένει ενεργό όσο τρέχει η παρακολούθηση, ώστε η εφαρμογή να μη σταματά λόγω idle.",
            "Για αξιόπιστο ping με κλειδωμένη συσκευή, βάλε την εφαρμογή σε Unrestricted battery ή device-idle whitelist.",
            "Το ιστορικό κρατά μέχρι 1000 αποτελέσματα και μετά αφαιρεί τα παλαιότερα.",
        ],
    },
    "en": {
        "starting": "Starting...",
        "target_label": "IP or host",
        "interval_label": "Interval seconds",
        "idle_title": "Idle",
        "idle_detail": "Set a target and start monitoring.",
        "start": "Start",
        "stop": "Stop",
        "ping_now": "Ping now",
        "history": "History",
        "online": "Online",
        "no_reply": "No reply",
        "checking": "Checking",
        "config_error": "Configuration error",
        "android_restriction": "Android restriction",
        "next_ping_empty": "Next ping: -",
        "next_ping_in": "Next ping in {duration}",
        "wakelock_on": "Wakelock: on",
        "wakelock_off": "Wakelock: off",
        "wakelock_error": "Wakelock error: {error}",
        "pinging": "Pinging {target}...",
        "target_required": "Set an IP address or host.",
        "target_invalid": "Target contains unsupported characters.",
        "interval_invalid": "Interval must be a whole number of seconds.",
        "interval_too_low": "Interval must be at least {minimum} seconds.",
        "ping_missing": "System ping command not found.",
        "ping_timeout": "Ping timed out.",
        "ping_failed": "Ping failed: {error}",
        "background_network_blocked": "Android blocked ping while the device was locked. Set the app to Unrestricted battery or add it to the device-idle whitelist.",
        "reply_received": "reply received",
        "language_tooltip": "Change language",
        "help_tooltip": "Help",
        "help_title": "Help",
        "help_close": "Close",
        "help_lines": [
            "Enter an IP address or host in the first field.",
            "Use the second field to set how often ping runs, in seconds. The default is 300.",
            "Start begins periodic pinging and disables Ping now until Stop.",
            "Wakelock stays enabled while monitoring runs so the app does not stop because of idle sleep.",
            "For reliable ping while the device is locked, set the app to Unrestricted battery or add it to the device-idle whitelist.",
            "History keeps up to 1000 results and then removes the oldest entries.",
        ],
    },
}


@dataclass
class PingResult:
    success: bool
    target: str
    latency_ms: float | None
    message_key: str | None
    message: str
    checked_at: float


def border_all(width: int | float, color: object) -> ft.Border:
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, right=side, bottom=side, left=side)


def normalize_language(value: object) -> str:
    return str(value).lower() if str(value).lower() in TEXT else DEFAULT_LANGUAGE


def tr(language: str, key: str, **kwargs: object) -> str:
    template = TEXT[normalize_language(language)][key]
    if isinstance(template, list):
        raise TypeError(f"Text key {key!r} is a list.")
    return template.format(**kwargs)


def get_storage_dir() -> Path:
    storage_root = os.environ.get("FLET_APP_STORAGE_DATA")
    if storage_root:
        path = Path(storage_root)
    else:
        home = os.environ.get("HOME")
        path = Path(home) / ".spyping" if home else Path.cwd() / ".spyping"
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_config() -> dict[str, object]:
    config_path = get_storage_dir() / CONFIG_FILENAME
    if not config_path.exists():
        return {
            "target": DEFAULT_TARGET,
            "interval_seconds": DEFAULT_INTERVAL_SECONDS,
            "language": DEFAULT_LANGUAGE,
        }
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        target = str(data.get("target") or DEFAULT_TARGET)
        interval = int(data.get("interval_seconds") or DEFAULT_INTERVAL_SECONDS)
        return {
            "target": target,
            "interval_seconds": max(MIN_INTERVAL_SECONDS, interval),
            "language": normalize_language(data.get("language", DEFAULT_LANGUAGE)),
        }
    except Exception:
        return {
            "target": DEFAULT_TARGET,
            "interval_seconds": DEFAULT_INTERVAL_SECONDS,
            "language": DEFAULT_LANGUAGE,
        }


def save_config(target: str, interval_seconds: int, language: str) -> None:
    config_path = get_storage_dir() / CONFIG_FILENAME
    payload = {
        "target": target,
        "interval_seconds": interval_seconds,
        "language": normalize_language(language),
    }
    config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def normalize_target(raw_target: str, language: str) -> str:
    target = raw_target.strip()
    target = re.sub(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", "", target)
    target = target.split("/", 1)[0].strip()
    if not target:
        raise ValueError(tr(language, "target_required"))
    if len(target) > 253 or not re.fullmatch(r"[A-Za-z0-9_.:-]+", target):
        raise ValueError(tr(language, "target_invalid"))
    return target


def normalize_interval(raw_interval: str, language: str) -> int:
    try:
        interval = int(str(raw_interval).strip())
    except ValueError as exc:
        raise ValueError(tr(language, "interval_invalid")) from exc
    if interval < MIN_INTERVAL_SECONDS:
        raise ValueError(tr(language, "interval_too_low", minimum=MIN_INTERVAL_SECONDS))
    return interval


def format_duration(seconds: int, language: str) -> str:
    minutes, remaining_seconds = divmod(max(0, seconds), 60)
    if normalize_language(language) == "el":
        if minutes:
            return f"{minutes}λ {remaining_seconds:02d}δ"
        return f"{remaining_seconds}δ"
    if minutes:
        return f"{minutes}m {remaining_seconds:02d}s"
    return f"{remaining_seconds}s"


def format_checked_at(timestamp: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(timestamp))


def _run_system_ping(target: str) -> PingResult:
    started_at = time.monotonic()
    checked_at = time.time()
    command = ["ping", "-c", "1", "-W", str(PING_TIMEOUT_SECONDS), target]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=PING_TIMEOUT_SECONDS + 2,
            check=False,
        )
    except FileNotFoundError:
        return PingResult(False, target, None, "ping_missing", "", checked_at)
    except subprocess.TimeoutExpired:
        return PingResult(False, target, None, "ping_timeout", "", checked_at)
    except Exception as exc:
        return PingResult(False, target, None, "ping_failed", str(exc), checked_at)

    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    latency_match = re.search(r"time[=<]([0-9.]+)\s*ms", output)
    latency_ms = float(latency_match.group(1)) if latency_match else None
    if latency_ms is None and completed.returncode == 0:
        latency_ms = (time.monotonic() - started_at) * 1000

    if completed.returncode == 0:
        latency_text = f"{latency_ms:.1f} ms" if latency_ms is not None else ""
        return PingResult(True, target, latency_ms, "reply_received" if not latency_text else None, latency_text, checked_at)

    if ANDROID_PERMISSION_DENIED_MARKER in output.lower():
        return PingResult(False, target, latency_ms, "background_network_blocked", "", checked_at)

    summary = output.splitlines()[-1] if output else "No reply."
    return PingResult(False, target, latency_ms, None, summary, checked_at)


async def run_ping(target: str) -> PingResult:
    return await asyncio.to_thread(_run_system_ping, target)


def result_message(result: PingResult, language: str) -> str:
    if result.message_key == "ping_failed":
        return tr(language, "ping_failed", error=result.message)
    if result.message_key:
        return tr(language, result.message_key)
    return result.message


def make_history_row(result: PingResult, language: str) -> ft.Control:
    icon = ft.Icons.CHECK_CIRCLE if result.success else ft.Icons.ERROR
    color = ft.Colors.GREEN_700 if result.success else ft.Colors.RED_700
    title = tr(language, "online") if result.success else tr(language, "android_restriction" if result.message_key == "background_network_blocked" else "no_reply")
    detail = result_message(result, language)
    if len(detail) > 120:
        detail = f"{detail[:117]}..."
    return ft.Container(
        padding=ft.Padding(12, 10, 12, 10),
        border=border_all(1, ft.Colors.BLACK_12),
        border_radius=8,
        content=ft.Row(
            controls=[
                ft.Icon(icon, color=color, size=22),
                ft.Column(
                    controls=[
                        ft.Text(f"{format_checked_at(result.checked_at)}  {title}", weight=ft.FontWeight.W_600),
                        ft.Text(detail, size=12, color=ft.Colors.BLACK_54, selectable=True),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
    )


def main(page: ft.Page) -> None:
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = ft.Colors.WHITE

    startup_status = ft.Text(tr(DEFAULT_LANGUAGE, "starting"), color=ft.Colors.BLACK_54)
    root = ft.SafeArea(
        ft.Container(
            expand=True,
            padding=16,
            content=ft.Column(
                controls=[
                    ft.Text(f"{APP_NAME} {APP_VERSION}", size=24, weight=ft.FontWeight.BOLD),
                    startup_status,
                ],
                spacing=12,
            ),
        ),
        expand=True,
    )
    page.add(root)

    try:
        wakelock = ft.Wakelock()
        page.services.append(wakelock)

        config = load_config()
        language_state = {"code": normalize_language(config["language"])}
        monitor_state = {
            "running": False,
            "token": 0,
            "last_target": str(config["target"]),
            "last_interval": int(config["interval_seconds"]),
        }
        status_state: dict[str, object] = {
            "kind": "idle",
            "message": None,
            "result": None,
            "next_remaining": None,
            "wakelock_enabled": False,
            "wakelock_error": None,
        }
        history_results: list[PingResult] = []

        target_field = ft.TextField(
            value=str(config["target"]),
            dense=True,
            autocorrect=False,
            capitalization=ft.TextCapitalization.NONE,
        )
        interval_field = ft.TextField(
            value=str(config["interval_seconds"]),
            dense=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        status_icon = ft.Icon(ft.Icons.RADIO_BUTTON_UNCHECKED, color=ft.Colors.BLUE_GREY_500, size=38)
        status_title = ft.Text(size=20, weight=ft.FontWeight.W_600)
        status_detail = ft.Text(color=ft.Colors.BLACK_54, selectable=True)
        next_ping_text = ft.Text(color=ft.Colors.BLACK_54)
        wakelock_text = ft.Text(color=ft.Colors.BLACK_54)
        start_button = ft.Button(icon=ft.Icons.PLAY_ARROW)
        ping_now_button = ft.OutlinedButton(icon=ft.Icons.NETWORK_PING)
        language_button = ft.IconButton(icon=ft.Icons.LANGUAGE, icon_size=26)
        help_button = ft.IconButton(icon=ft.Icons.HELP_OUTLINE, icon_size=26)
        history_title = ft.Text(size=16, weight=ft.FontWeight.W_600)
        history_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        def current_language() -> str:
            return normalize_language(language_state["code"])

        def rebuild_history() -> None:
            history_column.controls = [make_history_row(result, current_language()) for result in history_results]

        def update_next_ping_text() -> None:
            language = current_language()
            remaining = status_state["next_remaining"]
            if isinstance(remaining, int) and remaining > 0:
                next_ping_text.value = tr(language, "next_ping_in", duration=format_duration(remaining, language))
            else:
                next_ping_text.value = tr(language, "next_ping_empty")

        def update_wakelock_text() -> None:
            language = current_language()
            wakelock_error = status_state["wakelock_error"]
            if wakelock_error:
                wakelock_text.value = tr(language, "wakelock_error", error=wakelock_error)
            elif status_state["wakelock_enabled"]:
                wakelock_text.value = tr(language, "wakelock_on")
            else:
                wakelock_text.value = tr(language, "wakelock_off")

        def update_status_text() -> None:
            language = current_language()
            kind = status_state["kind"]
            if kind == "checking":
                status_icon.name = ft.Icons.HOURGLASS_TOP
                status_icon.color = ft.Colors.AMBER_700
                status_title.value = tr(language, "checking")
                status_detail.value = str(status_state["message"] or "")
            elif kind == "config_error":
                status_icon.name = ft.Icons.ERROR
                status_icon.color = ft.Colors.RED_700
                status_title.value = tr(language, "config_error")
                status_detail.value = str(status_state["message"] or "")
            elif kind == "result" and isinstance(status_state["result"], PingResult):
                result = status_state["result"]
                status_icon.name = ft.Icons.CHECK_CIRCLE if result.success else ft.Icons.ERROR
                status_icon.color = ft.Colors.GREEN_700 if result.success else ft.Colors.RED_700
                status_title.value = tr(language, "online") if result.success else tr(language, "android_restriction" if result.message_key == "background_network_blocked" else "no_reply")
                status_detail.value = f"{result.target} - {result_message(result, language)}"
            else:
                status_icon.name = ft.Icons.RADIO_BUTTON_UNCHECKED
                status_icon.color = ft.Colors.BLUE_GREY_500
                status_title.value = tr(language, "idle_title")
                status_detail.value = tr(language, "idle_detail")

        def update_static_texts() -> None:
            language = current_language()
            target_field.label = tr(language, "target_label")
            interval_field.label = tr(language, "interval_label")
            start_button.content = tr(language, "stop" if monitor_state["running"] else "start")
            ping_now_button.content = tr(language, "ping_now")
            language_button.tooltip = tr(language, "language_tooltip")
            help_button.tooltip = tr(language, "help_tooltip")
            history_title.value = tr(language, "history")
            update_status_text()
            update_next_ping_text()
            update_wakelock_text()
            rebuild_history()

        def persist_current_settings() -> None:
            try:
                interval = int(str(interval_field.value or DEFAULT_INTERVAL_SECONDS).strip())
            except ValueError:
                interval = int(monitor_state["last_interval"])
            save_config(str(target_field.value or DEFAULT_TARGET), max(MIN_INTERVAL_SECONDS, interval), current_language())

        def read_settings() -> tuple[str, int]:
            language = current_language()
            target = normalize_target(target_field.value or "", language)
            interval = normalize_interval(interval_field.value or "", language)
            target_field.value = target
            interval_field.value = str(interval)
            save_config(target, interval, language)
            monitor_state["last_target"] = target
            monitor_state["last_interval"] = interval
            return target, interval

        async def set_wakelock(enabled: bool) -> None:
            try:
                if enabled:
                    await wakelock.enable()
                    status_state["wakelock_enabled"] = True
                else:
                    await wakelock.disable()
                    status_state["wakelock_enabled"] = False
                status_state["wakelock_error"] = None
            except Exception as exc:
                status_state["wakelock_error"] = str(exc)
            update_wakelock_text()
            page.update()

        def set_status_waiting(target: str) -> None:
            status_state["kind"] = "checking"
            status_state["message"] = tr(current_language(), "pinging", target=target)
            status_state["result"] = None
            update_status_text()
            page.update()

        def set_status_error(message: str) -> None:
            status_state["kind"] = "config_error"
            status_state["message"] = message
            status_state["result"] = None
            update_status_text()
            page.update()

        def apply_result(result: PingResult) -> None:
            status_state["kind"] = "result"
            status_state["message"] = None
            status_state["result"] = result
            history_results.insert(0, result)
            del history_results[MAX_HISTORY_ITEMS:]
            update_status_text()
            rebuild_history()
            page.update()

        async def execute_ping() -> bool:
            try:
                target, _interval = read_settings()
            except ValueError as exc:
                set_status_error(str(exc))
                return False
            set_status_waiting(target)
            result = await run_ping(target)
            apply_result(result)
            return result.success

        async def monitor_loop(token: int) -> None:
            await set_wakelock(True)
            try:
                while monitor_state["running"] and monitor_state["token"] == token:
                    await execute_ping()
                    interval = int(monitor_state["last_interval"])
                    for remaining in range(interval, 0, -1):
                        if not monitor_state["running"] or monitor_state["token"] != token:
                            status_state["next_remaining"] = None
                            update_next_ping_text()
                            page.update()
                            return
                        status_state["next_remaining"] = remaining
                        update_next_ping_text()
                        page.update()
                        await asyncio.sleep(1)
            finally:
                if monitor_state["token"] == token:
                    await set_wakelock(False)

        def set_running(running: bool) -> None:
            monitor_state["running"] = running
            start_button.icon = ft.Icons.STOP if running else ft.Icons.PLAY_ARROW
            ping_now_button.disabled = running
            if not running:
                status_state["next_remaining"] = None
            update_static_texts()
            page.update()

        def toggle_monitoring(_event: ft.ControlEvent) -> None:
            if monitor_state["running"]:
                monitor_state["token"] += 1
                set_running(False)
                page.run_task(set_wakelock, False)
                return
            try:
                read_settings()
            except ValueError as exc:
                set_status_error(str(exc))
                return
            monitor_state["token"] += 1
            set_running(True)
            page.run_task(monitor_loop, monitor_state["token"])

        def ping_now(_event: ft.ControlEvent) -> None:
            page.run_task(execute_ping)

        def toggle_language(_event: ft.ControlEvent) -> None:
            language_state["code"] = "en" if current_language() == "el" else "el"
            persist_current_settings()
            update_static_texts()
            page.update()

        def close_dialog(dialog: ft.AlertDialog) -> None:
            dialog.open = False
            page.update()

        def show_help(_event: ft.ControlEvent) -> None:
            language = current_language()
            lines = TEXT[language]["help_lines"]
            assert isinstance(lines, list)
            help_dialog = ft.AlertDialog(
                modal=True,
                title=tr(language, "help_title"),
                content=ft.Column(
                    controls=[ft.Text(str(line), selectable=True) for line in lines],
                    spacing=10,
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[ft.TextButton(content=tr(language, "help_close"))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            help_dialog.actions[0].on_click = lambda _event: close_dialog(help_dialog)
            page.show_dialog(help_dialog)

        start_button.on_click = toggle_monitoring
        ping_now_button.on_click = ping_now
        language_button.on_click = toggle_language
        help_button.on_click = show_help

        root.content = ft.Container(
            expand=True,
            padding=16,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Image(src="/icon.png", width=32, height=32, border_radius=8),
                            ft.Text(APP_NAME, size=24, weight=ft.FontWeight.BOLD),
                            ft.Text(APP_VERSION, size=12, color=ft.Colors.BLACK_54),
                            ft.Container(expand=True),
                            language_button,
                            help_button,
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        padding=12,
                        border=border_all(1, ft.Colors.BLACK_12),
                        border_radius=8,
                        content=ft.Column(
                            controls=[
                                target_field,
                                interval_field,
                                ft.Row(
                                    controls=[start_button, ping_now_button],
                                    spacing=10,
                                    wrap=True,
                                ),
                            ],
                            spacing=10,
                        ),
                    ),
                    ft.Container(
                        padding=12,
                        border=border_all(1, ft.Colors.BLACK_12),
                        border_radius=8,
                        content=ft.Row(
                            controls=[
                                status_icon,
                                ft.Column(
                                    controls=[status_title, status_detail, next_ping_text, wakelock_text],
                                    spacing=4,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                    ),
                    history_title,
                    history_column,
                ],
                spacing=12,
                expand=True,
            ),
        )
        update_static_texts()
        page.update()
    except Exception as exc:
        startup_status.value = f"Fatal startup error: {exc}"
        startup_status.color = ft.Colors.RED_700
        page.update()


ft.run(main, assets_dir="assets")
