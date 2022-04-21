import os
import datetime
import ftplib
import zipfile
import zlib

demos_directory = '/home/game/l4d2_ds/left4dead2'

ftp_host = ''
ftp_user = ''
ftp_pass = ''
ftp_dir = '.'

dt = datetime.datetime.now()
now = dt.timestamp()

def zipcompress():
    for filename in os.listdir(demos_directory):
        if filename.endswith('.dem'):
            filePath = os.path.join(demos_directory, filename)
            if (now - os.path.getmtime(filePath) > 180):
                zf = zipfile.ZipFile(filename + '.zip', 'w', zipfile.ZIP_DEFLATED)
                zf.write(filePath, filename)
                zf.close()
                os.remove(filePath)

if __name__ == '__main__':
    zipcompress()

    session = None

    for filename in os.listdir('.'):
        if filename.endswith('.zip'):
            if session is None:
                session = ftplib.FTP(ftp_host,ftp_user,ftp_pass)
                if ftp_dir in session.nlst():
                    session.cwd(ftp_dir)
                else:
                    session.mkd(ftp_dir)
                    session.cwd(ftp_dir)
            zipFile = open(filename, 'rb')
            session.storbinary(f"STOR {filename}", zipFile)
            zipFile.close()
            os.remove(filename)

    if not (session is None):
        for item in session.mlsd('/' + ftp_dir, facts=['modify']):
            if item[0].endswith('.zip'):
                if (now - datetime.datetime.strptime(item[1].get('modify'), "%Y%m%d%H%M%S").timestamp() > 86400):
                    session.delete(item[0])
        session.quit()
