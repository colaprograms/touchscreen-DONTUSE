#!/bin/bash

CHROMIUM="/usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk"
/usr/bin/xset s noblank
/usr/bin/xset s off
/usr/bin/xset -dpms
/usr/bin/unclutter -idle 1 -root&

cd /home/pi/Downloads/touchscreen
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
./server &> log/log &
/bin/sleep 1
${CHROMIUM} http://localhost:9000/
