#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

APPS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor"

mkdir -p "$APPS_DIR"
mkdir -p "$ICONS_DIR/scalable/apps"

cp "$PROJECT_ROOT/assets/icons/yourbrowser.svg" "$ICONS_DIR/scalable/apps/yourbrowser.svg"

# Copy pre-rendered PNG icon sizes
for sz in 16 24 32 48 64 128 256 512; do
    if [ -f "$PROJECT_ROOT/assets/icons/${sz}x${sz}/yourbrowser.png" ]; then
        mkdir -p "$ICONS_DIR/${sz}x${sz}/apps"
        cp "$PROJECT_ROOT/assets/icons/${sz}x${sz}/yourbrowser.png" "$ICONS_DIR/${sz}x${sz}/apps/yourbrowser.png"
    fi
done

BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
ln -sf "$PROJECT_ROOT/bin/yourbrowser" "$BIN_DIR/yourbrowser"

# Substitusi path absolut dinamis sesuai PROJECT_ROOT saat ini
sed -e "s|/mnt/storage/aplikasi/yourbrowser|$PROJECT_ROOT|g" \
    "$PROJECT_ROOT/desktop/yourbrowser.desktop" > "$APPS_DIR/yourbrowser.desktop"

chmod +x "$APPS_DIR/yourbrowser.desktop"

if which gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$ICONS_DIR" || true
fi

if which update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" || true
fi

echo "[YourBrowser] Desktop shortcut and icon successfully registered in $APPS_DIR"
