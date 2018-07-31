import datetime
import ftplib
import os
import shutil
import tempfile
import time
import logging


handler = logging.FileHandler("backup_app.log")
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', style='%')
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)

HOST = ''
USERNAME = ''
PASSWORD = ''


class ClientOperation:

    def __init__(self):
        pass

    def make_temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        return tmpdir

    def remove_dir_file(self, path):
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    def compress(self, path, output_filename):
        compressed_file_path = shutil.make_archive(output_filename, 'zip', path)
        return compressed_file_path

    def copy_paste_files_dirs(self, src, dst, symlinks=False, ignore=None):
        dst_filename = os.path.split(src)[-1]
        shutil.copytree(src, os.path.join(dst, dst_filename), symlinks, ignore)
        return True

    def paths_list(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                lines = f.read().splitlines()
        else:
            with open(path, "w+") as f:
                lines = []
        return lines


class FileTransfer:

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.ftp = None

    def connect(self):
        self.ftp = ftplib.FTP(self.host, self.username, self.password)
        return self.ftp

    def close(self):
        self.ftp.quit()

    def upload(self, file, server_path):
        filename = os.path.split(file)[-1]
        with open(file, 'rb') as fileObj:
            self.ftp.storbinary('STOR ' + server_path + '/' + filename, fileObj)
        return True

    # def delete(self, server_path, file_path):
    #     filename = os.path.split(file_path)[-1]
    #     self.ftp.cwd(server_path)
    #     self.ftp.delete(filename)
    #     self.ftp.cwd('/')

    def check_make(self, destination):
        ff_list = []
        try:
            self.ftp.cwd(destination)
            file_list = self.ftp.nlst()
            for file in file_list:
                if file.endswith('.zip'):
                    file_name, ext = file.split('.')
                    ff_list.append(file_name)
            if len(ff_list) >= 3:
                ff_list.sort(key=lambda x: time.mktime(time.strptime(x, "%Y-%m-%d")))
                delete_filename = ff_list[0] + '.zip'
                self.ftp.delete(delete_filename)
                self.check_make(destination)
            path = destination
        except ftplib.error_perm:
            path = self.ftp.mkd(destination)
        return path


def main():
    current_dir = os.getcwd()
    current_date = datetime.date.today()
    client = ClientOperation()
    temp_path = client.make_temp_dir()
    path_list = client.paths_list(os.path.join(current_dir, 'backup_paths.txt'))
    for path in path_list:
        if os.path.exists(path):
            client.copy_paste_files_dirs(path, temp_path)
    filename = current_date.strftime("%Y-%m-%d")
    outputfile = os.path.join(*[os.getenv('USERPROFILE'), 'Documents', filename])
    compressed_file = client.compress(temp_path, outputfile)
    client.remove_dir_file(temp_path)
    ftp_obj = FileTransfer(HOST, USERNAME, PASSWORD)
    connection = ftp_obj.connect()
    if connection is not None:
        server_path = '/genIP/tarFiles/Aryan'
        server_path = ftp_obj.check_make(server_path)
        ftp_obj.upload(compressed_file, server_path)
        # ftp_obj.delete(server_path, compressed_file)
        ftp_obj.close()
    # print(compressed_file)
    client.remove_dir_file(compressed_file)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logging.exception(error)
        exit(1)
