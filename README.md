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

## Έκδοση

Τρέχουσα έκδοση: `1.0.4`

Σε αλλαγή έκδοσης συγχρονίζονται:

- `pyproject.toml`
- `src/version.py`
- `README.md`
- `ENGLISH.md`
- `uv.lock`
