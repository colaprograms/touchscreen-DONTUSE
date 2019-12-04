#!/bin/bash

/usr/bin/xset s noblank
/usr/bin/xset s off
/usr/bin/xset -dpms

/usr/bin/unclutter -idle 1 -root&
CHROMIUM="/usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk"
${CHROMIUM} ./index.html
