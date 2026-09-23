#!/bin/bash
# Render the real Home, Enrolment and lock screens on a connected device or emulator and
# turn them into the website's phone screens. Run from website/.
#
# The screens are rendered by app/src/androidTest/.../ui/WebsiteScreenshots.kt with
# captureToImage(), so MainActivity's FLAG_SECURE (which blanks adb screencap) does
# not apply. Needs adb, a running emulator, and cwebp.
set -euo pipefail
cd "$(dirname "$0")/../.."
./gradlew -q installDebug installDebugAndroidTest
adb shell am instrument -w -e websiteShots true \
  -e class com.camlock.ui.WebsiteScreenshots com.camlock.debug.test/com.camlock.CamLockTestRunner
tmp=$(mktemp -d)
adb pull /sdcard/Android/data/com.camlock.debug/files/website "$tmp" >/dev/null
# 600px wide is 2x the 284px phone screen, enough for sharp text on retina.
for n in home enrol lock; do
  python3 -c "from PIL import Image; im=Image.open('$tmp/website/$n.png'); w=600; im.resize((w, round(im.height*w/im.width)), Image.LANCZOS).save('$tmp/$n-600.png')"
  cwebp -quiet -q 90 "$tmp/$n-600.png" -o "website/public/img/app-$n.webp"
  echo "website/public/img/app-$n.webp"
done
rm -rf "$tmp"
