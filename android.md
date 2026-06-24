# Android APK οδηγίες για Python/Flet project

Αυτό το αρχείο κρατά γενικές οδηγίες για project γραμμένο σε Python με Flet, όπου ο τελικός στόχος είναι η παραγωγή Android APK. Απόφυγε project-specific ονόματα, paths, ιστορικό εκδόσεων και προσωρινές διαγνωστικές σημειώσεις.

## Βασική αρχή

- Χρησιμοποίησε πάντα `uv` για Python commands και dependency management.
- Μην τρέχεις γυμνά `pip` commands. Προτίμησε `uv add ...`, `uv pip install ...` ή `uv run ...`.
- Για Android build, προτίμησε ένα ελεγχόμενο script όπως `./build_apk.sh` αντί για απευθείας `flet build apk`, ειδικά σε μηχανήματα με περιορισμένη μνήμη.
- Απόφυγε εντολές που καταναλώνουν υπερβολική CPU/RAM στο background.

## Δομή project

- Κράτα τον κώδικα εφαρμογής και τα assets μέσα σε `src/`.
- Δήλωσε το app path στο `pyproject.toml`:

```toml
[tool.flet.app]
path = "src"
```

- Μην πακετάρεις runtime δεδομένα, downloads, cache ή μεγάλα τοπικά αρχεία στο APK. Χρησιμοποίησε `--exclude` όπου χρειάζεται.

## Dependencies

- Στα βασικά `dependencies` βάλε μόνο όσα χρειάζονται πραγματικά στο Android runtime.
- Χρησιμοποίησε `flet`, όχι `flet[all]`, στα βασικά dependencies. Το `flet[all]` τραβά desktop/build εργαλεία που μπορεί να σπάσουν Android packaging.
- Desktop-only εργαλεία, όπως `flet-cli`, `flet-desktop`, `flet-web`, `pyinstaller`, `watchdog`, `python-vlc`, μπαίνουν σε dev dependency group.

Παράδειγμα:

```toml
[project]
dependencies = [
    "flet>=0.82.2",
]

[dependency-groups]
dev = [
    "flet-cli>=0.82.2",
    "flet-desktop>=0.82.2",
    "flet-web>=0.82.2",
]
```

## Flet plugins

Τα Flet plugins πρέπει να δηλώνονται στο `pyproject.toml` κάτω από `[tool.flet.plugins]`.

Πρότυπο ονομασίας:

| Στοιχείο | Μορφή | Παράδειγμα |
| :--- | :--- | :--- |
| Package name | Dash-case | `flet-audio` |
| Python import | Underscore case | `flet_audio` |
| Plugin key | Underscore case | `flet_audio` |
| Plugin value | PascalCase | `"Audio"` |
| Control/class | PascalCase | `Audio()` |

Παράδειγμα:

```toml
[tool.flet.plugins]
flet_audio = "Audio"
flet_permission_handler = "PermissionHandler"
```

## Services και mounting

- Service plugins όπως `Audio`, `PermissionHandler` και παρόμοια δεν μπαίνουν στο `page.overlay`.
- Πρόσθεσέ τα στο `page.services`:

```python
page.services.append(audio_player)
page.services.append(permission_handler)
```

- Μην χρησιμοποιείς `page.services.clear()`, γιατί μπορεί να αποσυνδέσει plugins από το Flutter runtime.
- Μην κάνεις monkeypatch στο `_c` των controls/services. Χρησιμοποίησε τα default control names της βιβλιοθήκης.

## Audio σε Android

- Σε νεότερα Flet projects, το audio είναι ξεχωριστό plugin και όχι `ft.Audio`.
- Χρησιμοποίησε:

```python
import flet_audio as fta

audio = fta.Audio(src=audio_url, autoplay=False)
page.services.append(audio)
```

- Οι μέθοδοι όπως `play`, `pause`, `resume` και `seek` είναι async. Κάλεσέ τις με `await` μέσα σε async handler ή μέσω `page.run_task(...)`.
- Για events χρησιμοποίησε τα ονόματα που δίνει το plugin, π.χ. `on_position_change` και `on_state_change`.
- Σε handlers, διάβαζε ειδικά attributes όπως `e.position`, `e.state`, `e.duration` όταν υπάρχουν.
- Απόφυγε desktop-only audio λύσεις στο Android runtime, όπως `python-vlc`.

## Android permissions

- Δήλωσε Android permissions στο `pyproject.toml` μόνο όταν χρειάζονται.
- Παράδειγμα:

```toml
[tool.flet.android.permission]
"android.permission.INTERNET" = true
"android.permission.ACCESS_NETWORK_STATE" = true
```

- Για runtime permissions, χρησιμοποίησε plugin όπως `flet-permission-handler` και κάλεσε τις μεθόδους του async.
- Μην ζητάς άσχετα permissions. Κράτα τα permissions όσο πιο περιορισμένα γίνεται.

## Paths και αποθήκευση

- Μην γράφεις μέσα στον packaged app/assets φάκελο.
- Για runtime δεδομένα σε Android, προτίμησε app storage paths που παρέχει το Flet/περιβάλλον, όπως `FLET_APP_STORAGE_DATA` όταν είναι διαθέσιμο.
- Αν χρειάζεται fallback, χρησιμοποίησε ασφαλές user/app data path και όχι hardcoded desktop paths.
- Κράτα cache και downloads έξω από το `src/`, ώστε να μην μπουν κατά λάθος στο APK.

## Εκκίνηση εφαρμογής

- Στο Android, φρόντισε η Flet εφαρμογή να ξεκινά ανεξάρτητα από το αν το module φορτώνεται ως `__main__` ή ως app module από το runtime.
- Απόφυγε βαριά top-level imports που μπορεί να καθυστερήσουν ή να μπλοκάρουν το πρώτο render.
- Κάνε early render: πρόσθεσε ένα βασικό UI με `page.add(...)` όσο νωρίς γίνεται και μετά φόρτωσε ακριβότερη λογική.
- Βάλε try/except γύρω από το βασικό initialization και εμφάνισε ορατό σφάλμα στο UI, ώστε να μη μένει η εφαρμογή σε λευκή ή μαύρη οθόνη χωρίς πληροφορία.

## Build script

Το `build_apk.sh` πρέπει να:

- Ορίζει σωστό `JAVA_HOME`.
- Βάζει την επιθυμητή έκδοση Flutter πρώτη στο `PATH`, αν το project εξαρτάται από συγκεκριμένη έκδοση.
- Περιορίζει Java/Gradle μνήμη σε μηχανήματα με λίγους πόρους.
- Καλεί `uv run flet build apk`.
- Περνά architecture και excludes όπου χρειάζεται.
- Αντιγράφει το τελικό APK σε σταθερό output path, π.χ. `build/apk/AppName.apk`.

Ενδεικτικές ρυθμίσεις μνήμης:

```bash
export _JAVA_OPTIONS="-Xmx1536m -Xms512m -XX:MaxMetaspaceSize=512m"
export GRADLE_OPTS="-Xmx1536m -XX:MaxMetaspaceSize=512m -Dorg.gradle.daemon=false -Dorg.gradle.parallel=false -Dorg.gradle.workers.max=1 -Dorg.gradle.vfs.watch=false -Dkotlin.incremental=false"
```

Ενδεικτική build εντολή:

```bash
uv run flet build apk --arch arm64-v8a --flutter-build-args=--target-platform=android-arm64
```

Αν υπάρχουν φάκελοι runtime δεδομένων:

```bash
uv run flet build apk --arch arm64-v8a --exclude storage
```

## Έλεγχος APK

Μετά από build:

- Έλεγξε ότι δημιουργήθηκε APK στο αναμενόμενο path.
- Έλεγξε το μέγεθος του APK.
- Άνοιξε το APK archive και δες τα μεγαλύτερα αρχεία, ώστε να εντοπιστούν κατά λάθος πακεταρισμένα downloads/cache.
- Εγκατέστησε σε πραγματική Android συσκευή ή emulator.
- Έλεγξε startup, permissions, βασικές ροές και `adb logcat` για Python/Flet/Flutter errors.

Χρήσιμες εντολές:

```bash
ls -lh build/apk/*.apk
unzip -l build/apk/*.apk | sort -nk1 -r | head
adb install -r build/apk/AppName.apk
adb logcat -d
```

## Versioning

- Όταν αλλάζει έκδοση, ενημέρωσε όλες τις πηγές έκδοσης του project, π.χ. `pyproject.toml`, αρχείο `version.py`, README ή about screen.
- Χρησιμοποίησε συνεπές versioning και μην αφήνεις διαφορετικά σημεία του project με διαφορετική έκδοση.

## Πριν θεωρηθεί έτοιμο

- Το Python code κάνει compile.
- Το build script περνά `bash -n`.
- Το APK παράγεται.
- Το APK εγκαθίσταται.
- Η εφαρμογή ανοίγει χωρίς λευκή/μαύρη οθόνη.
- Τα κρίσιμα plugins δουλεύουν σε Android συσκευή.
- Δεν υπάρχουν εμφανή fatal errors στο `adb logcat`.
