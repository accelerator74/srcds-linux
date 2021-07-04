# l4d2-ds
Preparing a Linux System (Ubuntu/Debian) for Left 4 Dead 2 Dedicated Server

# Install required packages
* `apt update && apt full-upgrade -y`
* `apt install sudo screen vsftpd wget lib32gcc1 lib32stdc++6 lib32z1 python htop -y`

# Remove old linux kernels
* `apt-get purge $(dpkg -l 'linux-*' | sed '/^ii/!d;/'"$(uname -r | sed "s/\(.*\)-\([^0-9]\+\)/\1/")"'/d;s/^[^ ]* [^ ]* \([^ ]*\).*/\1/;/[0-9]/!d' | head -n -1)`

# System cleanup
* `journalctl --vacuum-size=1M`
* `apt autoclean`
* `apt --purge autoremove`

# Settings vsftpd
* `systemctl stop vsftpd`
* `rm -rf /etc/vsftpd.conf`
* `nano /etc/vsftpd.conf`
```
anonymous_enable=NO
chroot_local_user=YES
pam_service_name=vsftpd
local_enable=YES
write_enable=YES
xferlog_enable=YES
xferlog_file=/var/log/vsftpd.log
chroot_list_enable=NO
allow_writeable_chroot=YES
local_umask=022
pasv_min_port=49000
pasv_max_port=55000
listen_ipv6=YES
```
* `systemctl enable vsftpd`
* `systemctl start vsftpd`

# Set localtime
* `rm /etc/localtime`
* `ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime`

# Create user
* `adduser game`
* `su game && cd ~`

# Download steamcmd & dedicated server
* `mkdir ~/steamcmd && cd ~/steamcmd`
* `wget https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz`
* `tar -xvzf steamcmd_linux.tar.gz`
* `./l4d2_update.sh`
* `cd ~/.steam && mkdir sdk32`
* `ln -s ~/steamcmd/linux32/steamclient.so ~/.steam/sdk32/steamclient.so`

# Crontab
* `crontab -e`
* `@reboot sleep 10;cd /home/game/l4d2_ds/ && ./start.sh`
* `* * * * * python watchdog.py 127.0.0.1:27015 L4D2_DS /home/game/l4d2_ds`
* `30 06 * * * screen -S L4D2_DS -X quit; cd /home/game/l4d2_ds/ && ./start.sh`

# Start server
* `cd ~/l4d2_ds && ./start.sh`

# Enable coredump
* Add `ulimit -c unlimited` in `start.sh` before start screen session.

# GDB debugging
* `gdb ~/l4d2_ds/srcds_linux core`
* `bt` (backtrace), `disassemble` (assembler code), `info registers` print info about registers
