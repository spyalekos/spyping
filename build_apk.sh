#!/bin/bash
set -euo pipefail

APP_NAME="spyping"
APK_OUTPUT="build/apk/${APP_NAME}.apk"

VERSION="$(uv run python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"

echo "Cleaning previous Android build output..."
rm -rf build/flutter build/apk app_bundle src/build
mkdir -p build/apk

export _JAVA_OPTIONS="-Xmx1536m -Xms512m -XX:MaxMetaspaceSize=512m"
export GRADLE_OPTS="-Xmx1536m -XX:MaxMetaspaceSize=512m -Dorg.gradle.daemon=false -Dorg.gradle.parallel=false -Dorg.gradle.workers.max=1 -Dorg.gradle.vfs.watch=false -Dkotlin.incremental=false"
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
export SERIOUS_PYTHON_SITE_PACKAGES="$(pwd)/build/site-packages"
export PATH="/home/user/flutter/3.41.4/bin:$PATH"

echo "Building Android APK for ${APP_NAME} ${VERSION}..."
uv run flet build apk src     -o build/flutter     --project "$APP_NAME"     --artifact "$APP_NAME"     --product "$APP_NAME"     --description "Configurable Android ping monitor"     --org "gr.spyalekos"     --bundle-id "gr.spyalekos.spyping"     --company "spyalekos"     --copyright "Copyright (C) 2026 by Spyalekos"     --arch arm64-v8a     --build-version "$VERSION"     --build-number 1     --android-permissions "android.permission.INTERNET=true" "android.permission.ACCESS_NETWORK_STATE=true" "android.permission.WAKE_LOCK=true"     --flutter-build-args=--target-platform=android-arm64     --cleanup-app     --yes

SOURCE_APK=""
for CANDIDATE in     "build/flutter/${APP_NAME}.apk"     "build/flutter/app-release.apk"     "$(find build/flutter -path '*outputs/flutter-apk/app-release.apk' -print -quit)"; do
    if [ -n "$CANDIDATE" ] && [ -f "$CANDIDATE" ]; then
        SOURCE_APK="$CANDIDATE"
        break
    fi
done
if [ -z "$SOURCE_APK" ]; then
    echo "ERROR: APK artifact was not found under build/flutter." >&2
    exit 1
fi

cp "$SOURCE_APK" "$APK_OUTPUT"
ls -lh "$APK_OUTPUT"
echo "APK ready: $APK_OUTPUT"
