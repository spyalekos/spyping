# Οδηγίες & Κανόνες Ανάπτυξης AI (AI Reminders)

Αυτό το αρχείο είναι προσαρμοσμένο για το νέο project `spyping`.

**Alias χρήστη:** Όταν ο χρήστης αναφέρει `οδηγίες` ή `οδηγιες`, εννοεί αυτό το αρχείο (`AI-Instructions.md`), εκτός αν δώσει πιο συγκεκριμένο path.

**Alias χρήστη:** Όταν ο χρήστης γράφει μόνο `^` ή λέει «πάμε για ^», σημαίνει προετοιμασία για handoff / hands-off: ενημερώνουμε την Τελευταία Γνωστή Κατάσταση, καταγράφουμε τι άλλαξε, τι έχει ελεγχθεί, τι έχει εγκατασταθεί/τρέξει στη συσκευή, και αφήνουμε καθαρή σύνοψη για τον επόμενο κύκλο εργασίας.

## Βασικοί Κανόνες

1. Χρησιμοποιούμε πάντα `uv`. Δεν τρέχουμε γυμνές `pip` εντολές.
2. Το project χρησιμοποιεί Flet και στο Android χτίζεται αποκλειστικά μέσω `./build_apk.sh`.
3. Δεν τρέχουμε απευθείας `flet build apk`. Το script κρατά τα metadata και τους περιορισμούς μνήμης.
4. Όλος ο κώδικας εφαρμογής και τα packaged assets μένουν μέσα στο `src/`, με `[tool.flet.app] path = "src"` στο `pyproject.toml`.
5. Runtime δεδομένα και ρυθμίσεις γράφονται σε app storage, όχι στα packaged assets.
6. Το app λέγεται `spyping` και ξεκίνησε από έκδοση `1.0.0`.
7. Κάθε αλλαγή σε κώδικα ή build config απαιτεί version sync σε `pyproject.toml`, `src/version.py`, `README.md` και `uv.lock`, όταν η αλλαγή είναι release-facing.
8. Για Android permissions ζητάμε μόνο όσα χρειάζονται. Για το ping app χρησιμοποιούμε `INTERNET`, `ACCESS_NETWORK_STATE` και `WAKE_LOCK`.
9. Flet services μπαίνουν μόνο στο `page.services`. Δεν χρησιμοποιούμε `page.services.clear()` και δεν κάνουμε monkeypatch στο `_c`.
10. Το `ft.Wakelock` service ενεργοποιείται όσο τρέχει το monitoring, ώστε η εφαρμογή να μην αδρανοποιείται λόγω idle, και απενεργοποιείται στο Stop. Το service μπαίνει μόνο στο `page.services`.
11. Η main πρέπει να κάνει early render με `page.add()` πριν από ακριβότερη λογική και να έχει try/except για ορατό startup error αντί για μαύρη/λευκή οθόνη.

## Build, Test, Deploy

- Desktop/dev: `uv run flet run`
- Web/dev: `uv run flet run --web`
- Compile check: `uv run python -m compileall src`
- Build script syntax: `bash -n build_apk.sh`
- Android build: `./build_apk.sh`
- Το `./build_apk.sh` μπορεί φυσιολογικά να κάνει έως περίπου 18 λεπτά. Αν υπάρχει ενεργό Gradle/Kotlin/Flutter CPU, δεν το θεωρούμε hang.
- Install: `adb install -r build/apk/spyping.apk`
- Launch: `adb shell am start -n gr.spyalekos.spyping/.MainActivity`

Μετά από deploy ελέγχουμε `adb logcat` για Python/Flet/Flutter errors, fatal crashes, ANRs, `Unknown control` και `RangeError`.

## Τελευταία Γνωστή Κατάσταση

- Τρέχουσα έκδοση: `1.0.4`.
- Project reset σε νέο απλό Android app `spyping`.
- v1.0.1: Διορθώθηκε Flet 0.85 button API (`content` αντί για `text`) που προκαλούσε startup error στο Android.
- v1.0.2: Διορθώθηκε Flet 0.85 border API (`ft.Border`/`ft.BorderSide` αντί για `ft.border.all`) που εμφανίστηκε στο Android startup screenshot.
- v1.0.3: Διορθώθηκε Flet 0.85 padding API (`ft.Padding(...)` αντί για `ft.padding.symmetric(...)`) που εμφανίστηκε στο πρώτο Start/ping smoke test.
- v1.0.4: Προστέθηκε ελληνικό default UI, language icon toggle Ελληνικά/English, help icon με localized οδηγίες, αποθήκευση γλώσσας στα settings και όριο ιστορικού 1000 ping results.
- Βασική λειτουργία: target IP/host και interval από UI, περιοδικό ping μέσω system `ping`, χειροκίνητο ping, ιστορικό έως 1000 αποτελέσματα και αποθήκευση ρυθμίσεων σε app storage.
- Idle prevention: `ft.Wakelock` service mounted σε `page.services`, ενεργό όσο τρέχει το monitoring, ανενεργό στο Stop.
- Τελευταίο APK: `build/apk/spyping.apk`.
- Package/activity: `gr.spyalekos.spyping/.MainActivity`.
- Τελευταίο deploy/debug στη συσκευή `192.168.0.6:5555`: `adb install -r build/apk/spyping.apk` -> Success, `versionName=1.0.4`, permissions `INTERNET`, `ACCESS_NETWORK_STATE`, `WAKE_LOCK` granted.
- Τελευταίο UI smoke test: launch με ADB, default ελληνικό UI ορατό (`Έναρξη`, `Ping τώρα`, `Αναμονή`, `Ιστορικό`), language icon και help icon στη δεξιά πλευρά του header.
- Help dialog smoke test: tap στο help icon, ελληνικός διάλογος `Βοήθεια` άνοιξε κανονικά και αναφέρει χρήση target/interval, wakelock και όριο ιστορικού 1000 αποτελεσμάτων.
- Language toggle smoke test: tap στο language icon άλλαξε το UI σε English (`Start`, `Ping now`, `Idle`, `History`) και δεύτερο tap το επανέφερε στα ελληνικά για την τελική κατάσταση.
- Τελευταίο logcat μετά από καθαρό run και taps σε Help/Language: δεν βρέθηκαν Python traceback, fatal error, `Unknown control` ή `RangeError` για το app process.
- Captures σε `/tmp`: `spyping-104-start.png`, `spyping-104-help.png`, `spyping-104-language.png`. Αν το `view_image` ή απλά `file` χτυπήσει σε sandbox `bwrap`, χρησιμοποίησε UI dump από `uiautomator` ως primary verification.
