import datetime
import ftplib
import zipfile
import socket
import sys
import os
from pathlib import Path

BASE_DIR = Path("/home/game/srcds/left4dead2")
LOCK_FILE = Path(".demupload.lock")
FTP_HOST = "127.0.0.1"
FTP_USER = "demos"
FTP_PASS = "demos"
FTP_DIR = "demos"
TRANSFER_TIMEOUT = 60
DELETE_AFTER_DAYS = 2.3

def acquire_lock():
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            os.kill(pid, 0)
            sys.exit(1)
        except:
            LOCK_FILE.unlink(missing_ok=True)
    
    LOCK_FILE.write_text(str(os.getpid()))

def compress_demos():
    now = datetime.datetime.now().timestamp()
    created_zips = []

    for dem in BASE_DIR.glob("*.dem"):
        if now - dem.stat().st_mtime > 300:
            zip_path = dem.with_suffix(".dem.zip")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(dem, dem.name)
            dem.unlink()
            created_zips.append(zip_path)
    
    return created_zips

def upload_and_cleanup():
    now = datetime.datetime.now()
    files_to_upload = list(BASE_DIR.glob("*.dem.zip"))

    if not files_to_upload:
        return

    with ftplib.FTP(timeout=TRANSFER_TIMEOUT) as ftp:
        ftp.connect(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        
        try:
            ftp.cwd(FTP_DIR)
        except ftplib.error_perm:
            ftp.mkd(FTP_DIR)
            ftp.cwd(FTP_DIR)

        for zip_path in files_to_upload:
            try:
                with open(zip_path, "rb") as f:
                    ftp.storbinary(f"STOR {zip_path.name}", f)
                print(f"Uploaded: {zip_path.name}")
                zip_path.unlink()
            except Exception as e:
                print(f"Upload error {zip_path.name}: {e}")

        for name, facts in ftp.mlsd(facts=["modify"]):
            if not name.endswith(".zip"):
                continue
            try:
                mod_time = datetime.datetime.strptime(facts["modify"], "%Y%m%d%H%M%S")
                if (now - mod_time).total_seconds() > 86400 * DELETE_AFTER_DAYS:
                    ftp.delete(name)
            except Exception as e:
                print(f"Delete error {name}: {e}")

if __name__ == "__main__":
    try:
        acquire_lock()
        compress_demos()
        upload_and_cleanup()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise
    finally:
        LOCK_FILE.unlink(missing_ok=True)