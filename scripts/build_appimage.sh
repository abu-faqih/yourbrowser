#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

VERSION="1.1.0"
APP_DIR="$ROOT_DIR/build/appimage/YourBrowser.AppDir"
DIST_DIR="$ROOT_DIR/dist"
OUTPUT_APPIMAGE="$DIST_DIR/YourBrowser-${VERSION}-x86_64.AppImage"
RUNTIME="$ROOT_DIR/bin/tools/runtime-x86_64"

COMPRESSION="gzip"
FORCE_CLEAN=false

for arg in "$@"; do
    case "$arg" in
        --clean|-c)
            FORCE_CLEAN=true
            ;;
        --xz)
            COMPRESSION="xz"
            ;;
        --gzip)
            COMPRESSION="gzip"
            ;;
    esac
done

CORES=$(nproc 2>/dev/null || echo 4)

echo "=========================================================="
echo " Building YourBrowser Standalone Portable AppImage v${VERSION} "
echo " Compression: ${COMPRESSION} | CPU Cores: ${CORES}"
echo "=========================================================="

if [ ! -f "$RUNTIME" ]; then
    echo "[-] AppImage runtime not found at $RUNTIME"
    exit 1
fi

# Locate PyInstaller
PYINSTALLER_CMD=()
if command -v pyinstaller &>/dev/null; then
    PYINSTALLER_CMD=("$(command -v pyinstaller)")
elif [ -x "$HOME/.local/bin/pyinstaller" ]; then
    PYINSTALLER_CMD=("$HOME/.local/bin/pyinstaller")
elif python3 -m PyInstaller --version &>/dev/null; then
    PYINSTALLER_CMD=(python3 -m PyInstaller)
else
    echo "[-] PyInstaller is required to build a standalone AppImage."
    echo "    Please run: pip3 install pyinstaller"
    exit 1
fi

echo "[+] Using PyInstaller: ${PYINSTALLER_CMD[*]}"

# Clean previous AppDir structure
rm -rf "$ROOT_DIR/build/appimage"
mkdir -p "$ROOT_DIR/build/appimage"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/lib/yourbrowser"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$DIST_DIR"

PYINSTALLER_OUTPUT="$ROOT_DIR/build/pyinstaller_dist/yourbrowser"

# Check if we need to build PyInstaller bundle
NEED_BUNDLE=false
if [ "$FORCE_CLEAN" = true ] || [ ! -f "$PYINSTALLER_OUTPUT/yourbrowser" ]; then
    NEED_BUNDLE=true
else
    # Check if any python file in src/ is newer than the bundled executable
    if [ -n "$(find "$ROOT_DIR/src" -type f -newer "$PYINSTALLER_OUTPUT/yourbrowser" 2>/dev/null | head -n 1)" ]; then
        echo "[*] Source code changes detected in src/. Re-bundling..."
        NEED_BUNDLE=true
    fi
fi

if [ "$NEED_BUNDLE" = true ]; then
    echo "[+] Bundling Python interpreter, PyQt6, and Chromium WebEngine core..."
    CLEAN_FLAG=()
    if [ "$FORCE_CLEAN" = true ]; then
        CLEAN_FLAG=("--clean")
    fi

    "${PYINSTALLER_CMD[@]}" \
        --name yourbrowser \
        --onedir \
        --noconfirm \
        "${CLEAN_FLAG[@]}" \
        --specpath "$ROOT_DIR/build" \
        --paths "$ROOT_DIR" \
        --add-data "$ROOT_DIR/assets:assets" \
        --add-data "$ROOT_DIR/config:config" \
        --add-data "$ROOT_DIR/src:src" \
        --collect-all PyQt6 \
        --collect-submodules src \
        "$ROOT_DIR/src/app.py" \
        --distpath "$ROOT_DIR/build/pyinstaller_dist" \
        --workpath "$ROOT_DIR/build/pyinstaller_build"
else
    echo "[+] Reusing compiled bundle at $PYINSTALLER_OUTPUT (pass --clean to force full recompile)"
fi

# Copy PyInstaller bundle into AppDir usr/lib/yourbrowser
echo "[+] Assembling AppDir structure..."
cp -a "$PYINSTALLER_OUTPUT/"* "$APP_DIR/usr/lib/yourbrowser/"

# 2. Copy Icons
cp "$ROOT_DIR/assets/icons/yourbrowser.svg" "$APP_DIR/yourbrowser.svg"
cp "$ROOT_DIR/assets/icons/yourbrowser.svg" "$APP_DIR/usr/share/icons/hicolor/scalable/apps/yourbrowser.svg"

for res in 16x16 32x32 48x48 64x64 128x128 256x256 512x512; do
    if [ -f "$ROOT_DIR/assets/icons/$res/yourbrowser.png" ]; then
        mkdir -p "$APP_DIR/usr/share/icons/hicolor/$res/apps"
        cp "$ROOT_DIR/assets/icons/$res/yourbrowser.png" "$APP_DIR/usr/share/icons/hicolor/$res/apps/yourbrowser.png"
    fi
done
if [ -f "$ROOT_DIR/assets/icons/256x256/yourbrowser.png" ]; then
    cp "$ROOT_DIR/assets/icons/256x256/yourbrowser.png" "$APP_DIR/yourbrowser.png"
fi

# 3. Create portable desktop entry
cat << 'EODESK' > "$APP_DIR/yourbrowser.desktop"
[Desktop Entry]
Version=1.0
Name=YourBrowser
GenericName=Web Browser
Comment=Access the Internet with Ultimate Privacy and Zero Ads
Exec=yourbrowser %U
StartupNotify=true
Terminal=false
Icon=yourbrowser
Type=Application
Categories=Network;WebBrowser;
MimeType=application/pdf;application/rdf+xml;application/rss+xml;application/xhtml+xml;application/xhtml_xml;application/xml;image/gif;image/jpeg;image/png;image/webp;text/html;text/xml;x-scheme-handler/http;x-scheme-handler/https;
Actions=new-window;new-private-window;

[Desktop Action new-window]
Name=New Window
Exec=yourbrowser

[Desktop Action new-private-window]
Name=New Incognito Window
Exec=yourbrowser --incognito
EODESK
cp "$APP_DIR/yourbrowser.desktop" "$APP_DIR/usr/share/applications/yourbrowser.desktop"

# 4. Create AppRun entrypoint
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

export QT_QPA_PLATFORMTHEME="${QT_QPA_PLATFORMTHEME:-gtk3}"

# Execute self-contained YourBrowser binary
exec "$HERE/usr/lib/yourbrowser/yourbrowser" "$@"
EORUN
chmod +x "$APP_DIR/AppRun"

# 5. Create symlink launcher in usr/bin
cat << 'EOLAUNCH' > "$APP_DIR/usr/bin/yourbrowser"
#!/bin/bash
exec "$(dirname "$(readlink -f "${0}")")/../../AppRun" "$@"
EOLAUNCH
chmod +x "$APP_DIR/usr/bin/yourbrowser"

# 6. Generate SquashFS filesystem
SQUASHFS_IMG="$ROOT_DIR/build/appimage/root.squashfs"
echo "[+] Creating compressed SquashFS image (${COMPRESSION}) using ${CORES} processors..."
mksquashfs "$APP_DIR" "$SQUASHFS_IMG" \
    -root-owned \
    -noappend \
    -comp "$COMPRESSION" \
    -processors "$CORES"

# 7. Concatenate runtime and squashfs to create the AppImage
echo "[+] Generating final Standalone AppImage: $OUTPUT_APPIMAGE..."
cat "$RUNTIME" "$SQUASHFS_IMG" > "$OUTPUT_APPIMAGE"
chmod +x "$OUTPUT_APPIMAGE"

echo "[✓] Standalone AppImage built successfully!"
ls -lh "$OUTPUT_APPIMAGE"
