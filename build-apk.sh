#!/bin/bash
# MEER Chip Check — build + sign APK without Gradle (aapt2 + javac + d8 + apksigner)
# Usage: build-apk.sh [index.html path]  (default: ~/workspace/chipcheck/index.html)
set -e
SDK=$HOME/workspace/chipcheck/android-sdk
BT=$SDK/build-tools/34.0.0
ANDROID_JAR=$SDK/platforms/android-34/android.jar
APP=$HOME/workspace/chipcheck/android/app
OUT=$HOME/workspace/chipcheck
BUILD=$OUT/build-apk
PAGE=${1:-$OUT/index.html}
APK=$OUT/MEERChipCheck-v1.0.apk

[ -f "$PAGE" ] || { echo "ERROR: page not found: $PAGE"; exit 1; }
[ -f "$ANDROID_JAR" ] || { echo "ERROR: android.jar missing — run setup-sdk-direct.sh first"; exit 1; }

echo "=== 1. Stage page asset ==="
cp "$PAGE" "$APP/src/main/assets/chip-check/index.html"
ls -la "$APP/src/main/assets/chip-check/index.html"

echo "=== 2. Compile resources ==="
rm -rf "$BUILD" && mkdir -p "$BUILD/obj" "$BUILD/dex" "$BUILD/apk"
"$BT/aapt2" compile --dir "$APP/src/main/res" -o "$BUILD/obj/res.zip"

echo "=== 3. Link ==="
"$BT/aapt2" link --manifest "$APP/src/main/AndroidManifest.xml" \
  -I "$ANDROID_JAR" \
  --java "$BUILD/obj" \
  --min-sdk-version 24 --target-sdk-version 34 \
  --version-code 1 --version-name 1.0 \
  --auto-add-overlay \
  -o "$BUILD/apk/app-unsigned.apk" \
  "$BUILD/obj/res.zip"

echo "=== 4. Compile Java ==="
mkdir -p "$BUILD/obj/classes"
javac -source 8 -target 8 -nowarn -cp "$ANDROID_JAR" -d "$BUILD/obj/classes" \
  "$BUILD/obj/com/albadar/chipcheck/R.java" \
  "$APP/src/main/java/com/albadar/chipcheck/MainActivity.java"

echo "=== 5. DEX ==="
( cd "$BUILD/obj/classes" && jar --create --file "$BUILD/obj/classes.jar" . )
"$BT/d8" --release --lib "$ANDROID_JAR" --output "$BUILD/dex" "$BUILD/obj/classes.jar"

echo "=== 6. Pack dex + assets ==="
( cd "$BUILD/dex" && zip -q "$BUILD/apk/app-unsigned.apk" classes.dex )
( cd "$APP/src/main" && zip -q -r "$BUILD/apk/app-unsigned.apk" assets/chip-check )

echo "=== 7. Align + sign ==="
"$BT/zipalign" -f 4 "$BUILD/apk/app-unsigned.apk" "$BUILD/apk/app-aligned.apk"
PASS=$(cat "$HOME/workspace/meer-secrets/chipcheck-signing-password.txt")
"$BT/apksigner" sign --ks "$HOME/workspace/meer-secrets/chipcheck-keystore.jks" \
  --ks-pass pass:"$PASS" --key-pass pass:"$PASS" \
  --ks-key-alias chipcheck \
  --out "$APK" "$BUILD/apk/app-aligned.apk"

echo "=== 8. Verify ==="
"$BT/apksigner" verify --verbose "$APK"
"$BT/aapt2" dump badging "$APK" | grep -E "package:|application-label|launchable-activity"
ls -la "$APK"
sha256sum "$APK"
echo "APK READY: $APK"
