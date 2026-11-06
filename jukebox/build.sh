#!/bin/bash
# Builds "Lofi Jukebox.app" into jukebox/build, pointed at ../out for its tapes.
set -euo pipefail
cd "$(dirname "$0")"

swift build -c release
BIN=.build/release/LofiJukebox
APP="build/Lofi Jukebox.app"
MUSIC="$(cd .. && pwd)/out"

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BIN" "$APP/Contents/MacOS/LofiJukebox"
cp -R .build/release/LofiJukebox_LofiJukebox.bundle "$APP/Contents/Resources/"

# The icon is drawn by the app itself, then scaled into an iconset
ICONSET=build/AppIcon.iconset
rm -rf "$ICONSET"
mkdir -p "$ICONSET"
"$BIN" --render-icon build/icon-1024.png
for size in 16 32 128 256 512; do
  sips -z $size $size build/icon-1024.png --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
  sips -z $((size * 2)) $((size * 2)) build/icon-1024.png --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$APP/Contents/Resources/AppIcon.icns"

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>아빠의 멋진 로파이 앱</string>
  <key>CFBundleDisplayName</key><string>아빠의 멋진 로파이 앱</string>
  <key>CFBundleIdentifier</key><string>com.dominicfinn.lofijukebox</string>
  <key>CFBundleExecutable</key><string>LofiJukebox</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSMinimumSystemVersion</key><string>14.0</string>
  <key>LSApplicationCategoryType</key><string>public.app-category.music</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSPrincipalClass</key><string>NSApplication</string>
  <key>LofiMusicFolder</key><string>$MUSIC</string>
</dict>
</plist>
PLIST

codesign --force --sign - "$APP" >/dev/null
echo "Built $APP"
