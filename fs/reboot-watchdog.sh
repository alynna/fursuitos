#!/bin/bash

# Reboot using http://<the address of this node>/reboot?<PW>
PW=<your password here>

read INP
X=`echo $INP | cut -d' ' -f1-2`
if [ "$X" = "GET /reboot?$PW" ]; then
 pkill -TERM -f python
 sleep 2
 pkill -9 -f python
 python3 /fs/hw/rpi_ws281x/all-off.py
 sync
 reboot
fi

