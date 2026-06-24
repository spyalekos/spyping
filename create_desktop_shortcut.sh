#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_EXECUTABLE="$DIR/dist/spyping"
DESKTOP_FILE_PATH="$HOME/.local/share/applications/spyping.desktop"

mkdir -p "$(dirname "$DESKTOP_FILE_PATH")"
cat > "$DESKTOP_FILE_PATH" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=spyping
Comment=Configurable ping monitor
Exec=$APP_EXECUTABLE
Terminal=false
Categories=Network;Utility;
EOF

chmod +x "$DESKTOP_FILE_PATH"
echo "spyping desktop shortcut created: $DESKTOP_FILE_PATH"
