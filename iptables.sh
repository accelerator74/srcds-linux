#!/bin/bash
LANG=C; LC_ALL=C; export LANG LC_ALL
/sbin/iptables -F; /sbin/iptables -X

# Always allow loopback
/sbin/iptables -A INPUT -i lo -j ACCEPT

# Limit ICMP packets
/sbin/iptables -A INPUT -p icmp -m hashlimit --hashlimit-upto 6/sec --hashlimit-burst 4 --hashlimit-name icmp -j ACCEPT
/sbin/iptables -A INPUT -p icmp -m icmp --icmp-type 8 -j DROP

# Allow public services. (SSH, FTP, etc.).
/sbin/iptables -A INPUT -p tcp --dport 21:22 --source 127.0.0.1/32 -j ACCEPT

/sbin/iptables -A INPUT -p tcp --dport 21:22 -j DROP
/sbin/iptables -A INPUT -p tcp --dport 27015 -j DROP

# Restore:
# iptables-save -f ~/iptables_rules.ipv4
# cron @reboot /sbin/iptables-restore < ~/iptables_rules.ipv4

# Always end a script the right way
exit 0
