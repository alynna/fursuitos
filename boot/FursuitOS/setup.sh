#!/bin/bash
export FURRY=/boot/FursuitOS

read -p "Password: " SSHPASS
export SSHPASS
echo "pi:$SSHPASS" | chpasswd
echo "root:$SSHPASS" | chpasswd

apt -y update
apt -y upgrade
apt -y install sshpass mc rsync git samba scons python3-pip python3-dev swig idle3 socat ntpdate
pip3 install addict camel shyaml

mkdir -p /fs
ln -nfs $FURRY/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf
ln -nfs $FURRY/interfaces /etc/network/interfaces
ln -nfs $FURRY/smb.conf /etc/samba/smb.conf
ln -nfs $FURRY/hostname /etc/hostname
ln -nfs $FURRY/hosts /etc/hosts
cp $FURRY/rc /etc/rc.local
cp $FURRY/asound.conf /etc/asound.conf
cp $FURRY/alsa.conf /usr/share/alsa/alsa.conf
chmod 755 /etc/rc.local

cat <<EOF >/boot/FursuitOS/hosts
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF
echo "127.0.1.1       $(cat /etc/hostname)" >> /etc/hosts

cat <<EOF >/tmp/crontab
# m h d mo dow  command
* * * * * /bin/bash -c "/usr/bin/logger Router: $(/boot/FursuitOS/node-stay-up.sh)"
EOF
cat /tmp/crontab | crontab -

cd /fs/hw/
git clone https://github.com/jgarff/rpi_ws281x.git
cd /fs/hw/rpi_ws281x
cp -v $FURRY/ws281x_main.c /fs/hw/rpi_ws281x/main.c
scons
cd /fs/hw/rpi_ws281x/python/
python3 setup.py build
python3 setup.py install
cd /fs
echo ">> Recommend to customize with raspi-config, then reboot!"
unset SSHPASS
