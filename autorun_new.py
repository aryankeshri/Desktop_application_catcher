import copy
import csv
import ctypes
import os
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

filename = 'Agilent_VEE_logs.csv'
file_obj = open(os.path.join(BASE_DIR, filename), 'w', newline='')

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

old_list = []
ret_list = []


class AppListGenerater:
    def __init__(self, title):
        self.titles = title
        self.new_list = []

    def foreach_window(self, hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                valuedic = {}
                self.titles.append(valuedic)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                valuedic['App'] = buff.value
                self.new_list.append(buff.value)
        return True

    def getlist(self):
        EnumWindows(EnumWindowsProc(self.foreach_window), 0)
        return self.titles

    def filtered_list(self):
        filtered = []
        for i, dic in enumerate(self.getlist()):
            # if 'Agilent VEE' in dic['App']:
            if dic['App'] == 'AnyDesk':
                filtered.append(dic)
        return filtered

    def getnewlist(self):
        filtered = []
        EnumWindows(EnumWindowsProc(self.foreach_window), 0)
        for item in self.new_list:
            if item in ['AnyDesk']:
                filtered.append(item)
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

    def add_times(self, getnewlist):
        global old_list
        global ret_list
        valuedic = {}
        for item in getnewlist:
            if (item not in old_list) and (item in getnewlist):
                now = datetime.now()
                valuedic['App'] = item
                valuedic['stime'] = time.strftime("%b %d %Y %H:%M:%S", now.timetuple())
                ret_list.append(valuedic)
        for item in old_list:
            if (item in old_list) and (item not in getnewlist):
                for dic in ret_list:
                    if dic['App'] == item:
                        now = datetime.now()
                        dic['etime'] = time.strftime("%b %d %Y %H:%M:%S", now.timetuple())
        old_list = copy.deepcopy(getnewlist)
        return ret_list

    def modified_list(self):
        new_list = self.generated_list.getnewlist()
        return self.add_times(new_list)


def main():
    global ret_list
    while True:
        output = []
        a = AppOperations()
        # output = a.return_list()
        for i, item in enumerate(a.modified_list()):
            if 'etime' in item:
                output.append(item)
                ret_list.pop(i)

        if output:
            keys = output[0].keys()
            dict_writer = csv.DictWriter(file_obj, keys)
            dict_writer.writerows(output)
            file_obj.flush()
        # print('old:' + str(output))
        time.sleep(2)


if __name__ == "__main__":
    main()
