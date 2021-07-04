import sys
import socket
import time
import os
from subprocess import check_output

# * * * * * python watchdog.py 127.0.0.1:27015 MYSCREEN /home/server

def socket_query(ip, port):
    response = None

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)
    try:
        s.connect((ip,port))
    except:
        response = None
    else:
        s.send(b'\xFF\xFF\xFF\xFFTSource Engine Query\0')
    try:
        response = s.recv(1024)
    except socket.error:
        response = None
    s.close()

    return response

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(1)

    if not "."+sys.argv[2]+"\t(" in check_output(["screen -ls; true"],shell=True).decode('utf-8'):
        sys.exit(1)

    ics = sys.argv[1]
    ip,port = ics.split(":")
    result = None
    req = 0

    while True:
        result = socket_query(ip, int(port))
        req += 1
        if result is None and req < 5:
            if not "."+sys.argv[2]+"\t(" in check_output(["screen -ls; true"],shell=True).decode('utf-8'):
                sys.exit(1)

            time.sleep(10)
        else:
            break

    if result is None:
        file = open("watchdog.log", "a")
        file.write("[{}] {} server did not respond {} times\n".format(time.ctime(), ics, req))
        file.close()
        os.system("screen -S {} -X quit".format(sys.argv[2]))
        os.system("cd {} && ./start.sh".format(sys.argv[3]))