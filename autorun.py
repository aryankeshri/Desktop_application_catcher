import copy
import csv
import ctypes
import os
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible


filename = 'Agilent_VEE_logs.csv'
path = os.path.join(*[os.getenv('USERPROFILE'), 'Documents', filename])
file_obj = open(path, 'a', newline='')

old_list = []
ret_list = []


class AppListGenerater:
    def __init__(self):
        self.new_list = []

    def foreach_window(self, hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                self.new_list.append(buff.value)
        return True

    def filter_list(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                lines = f.read().splitlines()
        else:
            with open(path, "w+") as f:
                lines = []
        return lines

    def getnewlist(self):
        filtered = []
        filter_list = self.filter_list(os.path.join(BASE_DIR, 'filter.txt'))
        EnumWindows(EnumWindowsProc(self.foreach_window), 0)
        for item in self.new_list:
            for fil in filter_list:
                if fil in item:
                    filtered.append(item)
        return filtered


class AppOperations:
    def __init__(self):
        self.generated_list = AppListGenerater()
        self.datetime_format = "%b %d %Y %H:%M:%S"

    def add_times(self, getnewlist):
        global old_list
        global ret_list
        valuedic = {}
        for item in getnewlist:
            if (item not in old_list) and (item in getnewlist):
                now = datetime.now()
                valuedic['App'] = item
                valuedic['stime'] = time.strftime(self.datetime_format, now.timetuple())
                ret_list.append(valuedic)
        for item in old_list:
            if (item in old_list) and (item not in getnewlist):
                for dic in ret_list:
                    if dic['App'] == item:
                        now = datetime.now()
                        dic['etime'] = time.strftime(self.datetime_format, now.timetuple())
                        timedelta = (
                                datetime.strptime(dic['etime'], self.datetime_format) -
                                datetime.strptime(dic['stime'], self.datetime_format)
                        )
                        dic['execution_time'] = str(timedelta)
        old_list = copy.deepcopy(getnewlist)
        return ret_list

    def modified_list(self):
        new_list = self.generated_list.getnewlist()
        return self.add_times(new_list)


def main():
    global ret_list
    output = []
    a = AppOperations()
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
    time.sleep(5*60)
    main()


if __name__ == "__main__":
    main()
