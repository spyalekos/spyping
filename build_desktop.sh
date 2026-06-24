#!/bin/bash
set -euo pipefail

VERSION="$(uv run python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"

uv run flet pack src/main.py     --name spyping     --product-name spyping     --file-description spyping     --product-version "$VERSION"     --file-version "$VERSION.0"     --company-name spyalekos     --copyright "Copyright (C) 2026 by Spyalekos"     --add-data src/assets:assets     --yes
