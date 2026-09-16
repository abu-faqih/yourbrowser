#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

APPS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

mkdir -p "$APPS_DIR"
mkdir -p "$ICONS_DIR"

cp "$PROJECT_ROOT/assets/icons/yourbrowser.svg" "$ICONS_DIR/yourbrowser.svg"
cp "$PROJECT_ROOT/desktop/yourbrowser.desktop" "$APPS_DIR/yourbrowser.desktop"

if which update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" || true
fi

echo "[YourBrowser] Desktop shortcut and icon successfully registered in $APPS_DIR"
