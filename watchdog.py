import sys
import socket
import time
import os
import urllib.request
import urllib.parse
import json
import subprocess
from pathlib import Path

HOME = Path.home()
LOCK_FILE = HOME / ".watchdog.lock"

steamcmd_login = "anonymous"
steamcmd_dir = HOME / "steamcmd"
servers = [
    {
        "server_adr": "127.0.0.1:27015",
        "server_dir": HOME / "srcds",
        "screen_name": "SRCDS",
        "start_dir": ".",
        "game_dir": "left4dead2",
        "app_id": 222860,
        "auto_update": True
    }
]

def log_message(message):
    log_file = HOME / "watchdog.log"
    with open(log_file, "a") as log:
        log.write(f"[{time.ctime()}] {message}\n")

def socket_query(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(3)
            s.sendto(b'\xFF\xFF\xFF\xFFTSource Engine Query\0', (ip, port))
            data = s.recv(1024)
            return len(data) > 0
    except:
        return False

def run(cmd, timeout=5, cwd=None):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        cwd=cwd
    )

def screen_exists(name):
    r = run(["screen", "-ls"])
    return f".{name}\t(" in r.stdout

def steamcmd_running():
    try:
        result = run(["pgrep", "-f", "steamcmd"])
        return result.returncode == 0 and result.stdout.strip() != ""
    except:
        return False

def up_to_date_check(dir, subdir):
    appid = 0
    patch_version = 0
    up_to_date = True
    try:
        with (dir / 'steam_appid.txt').open('r') as file:
            appid = int(file.readline().strip())
        with (dir / subdir / 'steam.inf').open('r') as file:
            for line in file:
                key_value_pair = line.strip().split("=")
                if len(key_value_pair) == 2 and key_value_pair[0] == "PatchVersion":
                    patch_version = int(key_value_pair[1].replace(".", ""))
                    break
        if appid == 0 or patch_version == 0:
            return up_to_date
        params = {
            "appid": appid,
            "version": patch_version
        }
        url = "https://api.steampowered.com/ISteamApps/UpToDateCheck/v0001/?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                json_data = json.loads(response.read().decode())
                up_to_date = json_data.get("response", {}).get("up_to_date", True)
        except urllib.error.URLError as e:
            up_to_date = True
    except Exception as e:
        print(f"Error checking update status: {e}")
        up_to_date = True
    return up_to_date

def find_servers_for_update(target_dir):
    dir_servers = []
    for server in servers:
        if server["server_dir"] == target_dir:
            dir_servers.append(server)
    return dir_servers

def check_server(server_config):
    server_adr = server_config["server_adr"]
    screen_name = server_config["screen_name"]
    start_path = server_config["server_dir"] / server_config["start_dir"]

    if not screen_exists(screen_name):
        return

    if server_config["auto_update"]:
        if steamcmd_running():
            return
        if not up_to_date_check(server_config["server_dir"], server_config["game_dir"]):
            upd_servers = find_servers_for_update(server_config["server_dir"])
            for server in upd_servers:
                server_adr = server["server_adr"]
                screen_name = server["screen_name"]
                if screen_exists(screen_name):
                    log_message(f"{server_adr} server stopped for update")
                    run(["screen", "-S", screen_name, "-X", "quit"])
            time.sleep(3)
            run([
                    str(steamcmd_dir / "steamcmd.sh"),
                    "+force_install_dir", str(server_config["server_dir"]),
                    "+login", steamcmd_login,
                    "+app_update", str(server_config["app_id"]),
                    "+quit"
                ], timeout=600)
            for server in upd_servers:
                start_path = server["server_dir"] / server["start_dir"]
                run(["./start.sh"], timeout=15, cwd=start_path)
                time.sleep(3)
            return

    ip, port = server_adr.split(":")
    result = False

    for _ in range(5):
        result = socket_query(ip, int(port))
        if result:
            break
        if not screen_exists(screen_name):
            return
        time.sleep(3)

    if not result:
        log_message(f"{server_adr} server did not respond 5 times")
        run(["screen", "-S", screen_name, "-X", "quit"])
        run(
            ["./start.sh"],
            timeout=15,
            cwd=start_path
        )

if __name__ == '__main__':
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text().strip())
            os.kill(old_pid, 0)
            sys.exit(0)
        except (OSError, ValueError):
            LOCK_FILE.unlink(missing_ok=True)
    try:
        LOCK_FILE.write_text(str(os.getpid()))
        for server in servers:
            check_server(server)
            time.sleep(1)
    finally:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()