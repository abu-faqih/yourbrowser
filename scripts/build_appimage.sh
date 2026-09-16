#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

VERSION="1.0.0"
APP_DIR="$ROOT_DIR/build/appimage/YourBrowser.AppDir"
DIST_DIR="$ROOT_DIR/dist"
OUTPUT_APPIMAGE="$DIST_DIR/YourBrowser-${VERSION}-x86_64.AppImage"
RUNTIME="$ROOT_DIR/bin/tools/runtime-x86_64"

echo "=========================================================="
echo " Building YourBrowser Desktop Portable AppImage v${VERSION} "
echo "=========================================================="

if [ ! -f "$RUNTIME" ]; then
    echo "[-] AppImage runtime not found at $RUNTIME"
    exit 1
fi

# Clean and prepare directory structure
rm -rf "$ROOT_DIR/build/appimage"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/yourbrowser"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$DIST_DIR"

# Copy source code and assets into AppDir
cp -r "$ROOT_DIR/src" "$APP_DIR/usr/share/yourbrowser/"
cp -r "$ROOT_DIR/assets" "$APP_DIR/usr/share/yourbrowser/"
if [ -d "$ROOT_DIR/config" ]; then
    cp -r "$ROOT_DIR/config" "$APP_DIR/usr/share/yourbrowser/"
fi

# Copy icon and desktop entry to root of AppDir and hicolor icons
cp "$ROOT_DIR/assets/icons/yourbrowser.svg" "$APP_DIR/yourbrowser.svg"
cp "$ROOT_DIR/assets/icons/yourbrowser.svg" "$APP_DIR/usr/share/icons/hicolor/scalable/apps/yourbrowser.svg"
cp "$ROOT_DIR/desktop/yourbrowser.desktop" "$APP_DIR/yourbrowser.desktop"

# Create AppRun entrypoint
cat << 'EORUN' > "$APP_DIR/AppRun"
#!/bin/bash
set -e

# Resolve AppDir location
HERE="$(dirname "$(readlink -f "${0}")")"

# -------------------------------------------------------------
# Portable Mode Enforcement
# If executed as an AppImage, store all configuration, profiles,
# bookmarks, and browser cache directly alongside the AppImage binary.
# -------------------------------------------------------------
if [ -n "$APPIMAGE" ]; then
    APPIMAGE_DIR="$(dirname "$APPIMAGE")"
    
    # Check if standard .home directory exists or default to yourbrowser_data
    if [ -d "${APPIMAGE}.home" ]; then
        PORTABLE_DATA="${APPIMAGE}.home/.config/yourbrowser"
        export HOME="${APPIMAGE}.home"
    else
        PORTABLE_DATA="$APPIMAGE_DIR/yourbrowser_data"
    fi

    mkdir -p "$PORTABLE_DATA"
    export YOURBROWSER_DATA_DIR="$PORTABLE_DATA"
    export XDG_CONFIG_HOME="$PORTABLE_DATA"
    export XDG_DATA_HOME="$PORTABLE_DATA/local"
    export XDG_CACHE_HOME="$PORTABLE_DATA/cache"
fi

# Chromium sandbox flag for QtWebEngine
if [ -z "$QTWEBENGINE_CHROMIUM_FLAGS" ]; then
    export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox"
else
    export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox ${QTWEBENGINE_CHROMIUM_FLAGS}"
fi

export PYTHONPATH="$HERE/usr/share/yourbrowser:${PYTHONPATH:-}"

exec python3 "$HERE/usr/share/yourbrowser/src/app.py" "$@"
EORUN
chmod +x "$APP_DIR/AppRun"

# Create symlink launcher in usr/bin
cat << 'EOLAUNCH' > "$APP_DIR/usr/bin/yourbrowser"
#!/bin/bash
exec "$(dirname "$(readlink -f "${0}")")/../../AppRun" "$@"
EOLAUNCH
chmod +x "$APP_DIR/usr/bin/yourbrowser"

# Generate SquashFS filesystem
SQUASHFS_IMG="$ROOT_DIR/build/appimage/root.squashfs"
echo "[+] Creating SquashFS image..."
mksquashfs "$APP_DIR" "$SQUASHFS_IMG" -root-owned -noappend -comp xz

# Concatenate runtime and squashfs to create the AppImage
echo "[+] Generating final AppImage: $OUTPUT_APPIMAGE..."
cat "$RUNTIME" "$SQUASHFS_IMG" > "$OUTPUT_APPIMAGE"
chmod +x "$OUTPUT_APPIMAGE"

echo "[✓] AppImage built successfully!"
ls -lh "$OUTPUT_APPIMAGE"
