# spyping 1.0.4

Το `spyping` είναι μια μικρή εφαρμογή Android, γραμμένη σε Python/Flet, που κάνει περιοδικό ping σε IP ή host που ορίζεται μέσα από την ίδια την εφαρμογή.

English documentation: [ENGLISH.md](ENGLISH.md)

## Τι κάνει

- Κάνει ping σε IP ή host που πληκτρολογείς στο UI.
- Το διάστημα ping είναι ρυθμιζόμενο σε δευτερόλεπτα.
- Η προεπιλογή είναι `8.8.8.8` κάθε `300` δευτερόλεπτα.
- Υποστηρίζει χειροκίνητο `Ping τώρα`.
- Κρατά ιστορικό έως `1000` τελευταία αποτελέσματα.
- Κρατά wakelock όσο τρέχει η παρακολούθηση, ώστε η εφαρμογή να μη σταματά λόγω idle.
- Αποθηκεύει target, interval και γλώσσα σε app storage.
- Ξεκινά στα ελληνικά και έχει εικονίδιο αλλαγής γλώσσας Ελληνικά/English.
- Έχει εικονίδιο βοήθειας με σύντομες οδηγίες μέσα στην εφαρμογή.

## Android

Package/activity:

```text
gr.spyalekos.spyping/.MainActivity
```

Permissions:

- `android.permission.INTERNET`
- `android.permission.ACCESS_NETWORK_STATE`
- `android.permission.WAKE_LOCK`

## Ανάπτυξη

Απαιτούνται:

- Python 3.10+
- `uv`
- Flet/Flet CLI μέσω των dependencies του project
- Android SDK/ADB για deploy σε συσκευή

Εγκατάσταση dependencies:

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

## Build APK

Το Android build γίνεται μόνο με το script του project:

```bash
./build_apk.sh
```

Το script μπορεί να χρειαστεί αρκετά λεπτά και παράγει:

```text
build/apk/spyping.apk
```

Εγκατάσταση και εκκίνηση σε συνδεδεμένη συσκευή:

```bash
adb install -r build/apk/spyping.apk
adb shell am start -n gr.spyalekos.spyping/.MainActivity
```

## Έλεγχοι

Compile check:

```bash
uv run python -m compileall src
```

Έλεγχος build script:

```bash
bash -n build_apk.sh
```

Μετά από deploy σε Android συσκευή ελέγχουμε `adb logcat` για Python/Flet/Flutter errors, fatal crashes, ANRs, `Unknown control` και `RangeError`.

## Έκδοση

Τρέχουσα έκδοση: `1.0.4`

Σε αλλαγή έκδοσης συγχρονίζονται:

- `pyproject.toml`
- `src/version.py`
- `README.md`
- `ENGLISH.md`
- `uv.lock`
