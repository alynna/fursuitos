#!/bin/bash

# Internet keep-alive
echo "GET /" | nc -w 1 1.1.1.1 80 >/dev/null

# Gateway connect test
GW=`cat /run/shm/gateway`
ping -c2 -w3 $GW >/dev/null 2>/dev/null
if [ $? -gt 0 ]; then
 logger "Gateway Down: $(cat /run/shm/gateway)"
 /boot/FursuitOS/node-up.sh
else
 # IP connect test
 IP=`cat /run/shm/ip`
 ping -c1 -w2 $IP >/dev/null 2>/dev/null
 if [ $? -gt 0 ]; then
  logger "IP down: $(cat /run/shm/ip)"
  /boot/FursuitOS/node-up.sh
 else
  # Everything is OK
  logger "Up $(ip -4 addr list dev wlan0 | grep inet | cut -d' ' -f6 | tr '\n' ' ') -> $(cat /run/shm/gateway)"
 fi
fi
