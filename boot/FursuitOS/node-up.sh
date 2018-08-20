#!/bin/bash

# Do DHCP ourselves.
ip -4 addr flush dev wlan0
dhclient -1 -v wlan0

# Correct hostname 
hostname `cat /boot/FursuitOS/hostname`

# Get IP
X=`ip -4 addr list dev wlan0 | grep "scope global wlan0" | cut -d' ' -f6`

# Mutilate IP to get one matching our node number.
X0=`echo $X | cut -d'.' -f1-3`
X2=`echo $X | cut -d'/' -f2`
X1=`echo "$X0.$(cat /boot/FursuitOS/fursuit.yaml | shyaml get-value node)/$X2"`
echo "Transforming $X to $X1"
ip -4 addr add ${X1} broadcast + dev wlan0
ip -4 addr del ${X} broadcast + dev wlan0
ip -4 addr add ${X} broadcast + dev wlan0

# SHOW US WHAT YOU GOT
ip -4 addr show dev wlan0

# Add ourselves to the host file.
cat >/boot/FursuitOS/hosts <<EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF
echo "127.0.1.1       $(cat /boot/FursuitOS/hostname)" >> /boot/FursuitOS/hosts
