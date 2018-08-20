#!/bin/bash
GW=`ip -4 route | grep default | cut -d' ' -f3`
ping -c2 -w3 $GW >/dev/null 2>/dev/null
if [ $? -gt 0 ]; then
 echo Down
 ifdown wlan0; ifup wlan0
 /boot/FursuitOS/node-up.sh >/dev/null 2>/dev/null
else
 echo Up
fi
