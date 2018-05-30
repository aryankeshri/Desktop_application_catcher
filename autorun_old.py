import csv
import ctypes
import os
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

filename = 'Agilent_VEE_logs.csv'
file_obj = open(os.path.join(BASE_DIR, filename), 'w', newline='')


class AppListGenerater:
    def __init__(self, title):
        self.titles = title
        self.EnumWindows = ctypes.windll.user32.EnumWindows
        self.EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int),
                                                  ctypes.POINTER(ctypes.c_int))
        self.GetWindowText = ctypes.windll.user32.GetWindowTextW
        self.GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        self.IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    def foreach_window(self, hwnd, lParam):
        if self.IsWindowVisible(hwnd):
            length = self.GetWindowTextLength(hwnd)
            if length > 0:
                valuedic = {}
                self.titles.append(valuedic)
                buff = ctypes.create_unicode_buffer(length + 1)
                self.GetWindowText(hwnd, buff, length + 1)
                valuedic['App'] = buff.value
        return True

    def getlist(self):
        self.EnumWindows(self.EnumWindowsProc(self.foreach_window), 0)
        return self.titles

    def filtered_list(self):
        filtered = []
        for i, dic in enumerate(self.getlist()):
            # if 'Agilent VEE' in dic['App']:
            if dic['App'] == 'AnyDesk':
                filtered.append(dic)
        return filtered


class AppOperations:
    def __init__(self):
        self.titles = []
        self.generated_list = AppListGenerater(self.titles)

    def add_time(self, getflist):
        for dic in getflist:
            now = datetime.now()
            dic['time'] = time.strftime("%b %d %Y %H:%M:%S", now.timetuple())
            dic['timestamp'] = now.timestamp()
        return getflist

    def return_list(self):
        new_list = self.generated_list.filtered_list()
        return self.add_time(new_list)


def main():
    a = AppOperations()
    output = a.return_list()
    if output:
        keys = output[0].keys()
        dict_writer = csv.DictWriter(file_obj, keys)
        dict_writer.writerows(output)
        file_obj.flush()
    print('old:' + str(output))
    time.sleep(2)
    main()


if __name__ == "__main__":
    main()
    file_obj.close()
