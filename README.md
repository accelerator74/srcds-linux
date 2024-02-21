# srcds
Preparing a Linux System (Ubuntu/Debian) for Source Dedicated Server

# Install required packages
* `apt update && apt full-upgrade -y`
* `apt install sudo screen vsftpd wget lib32gcc-s1 lib32stdc++6 lib32z1 python3 htop psmisc -y`

# Remove old linux kernels
* `dpkg --list | grep linux-image`
* `apt-get --purge remove linux-image-XXXX`

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
pasv_min_port=10090
pasv_max_port=10099
listen_ipv6=YES
```
* `systemctl enable vsftpd`
* `systemctl start vsftpd`

# Set localtime
* `rm /etc/localtime`
* `ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime`

# Create user
* `adduser game`
* `su game`
* `cd ~`

# Download steamcmd & dedicated server
* `mkdir ~/steamcmd && cd ~/steamcmd`
* `wget https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz`
* `tar -xvzf steamcmd_linux.tar.gz`
* `./update.sh`
* `cd ~/.steam && mkdir sdk32`
* `ln -s ~/steamcmd/linux32/steamclient.so ~/.steam/sdk32/steamclient.so`

# Crontab
* `crontab -e`
* `@reboot sleep 10;cd ~/srcds && ./start.sh`
* `* * * * * python3 watchdog.py`
* `30 02 * * * screen -S SRCDS -X quit; cd ~/srcds && ./start.sh`
* `*/15 * * * * python3 demupload.py`

# Start server
* `cd ~/srcds && ./start.sh`

# Enable coredump
* Add `ulimit -c unlimited` in `start.sh` before start screen session.

# GDB debugging
* `gdb ~/srcds/srcds_linux core`
* `bt` (backtrace), `disassemble` (assembler code), `info registers` print info about registers

# Performance
* `nano /etc/default/grub`
* `GRUB_CMDLINE_LINUX="mitigations=off"`
* `update-grub`

# Swap
* `fallocate -l 512M /swapfile`
* `chmod 600 /swapfile`
* `mkswap /swapfile`
* `swapon /swapfile`
* `echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab`
* `sysctl -w vm.swappiness=10`
* `sysctl -w vm.vfs_cache_pressure=50`
