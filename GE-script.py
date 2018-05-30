import csv
import ctypes
import os
import time
import threading
from datetime import datetime
from __init__ import BASE_DIR

filename = 'GElog.csv'
file_obj = open(os.path.join(BASE_DIR, filename), 'w')

value = False


class AppListGenerater:
    def __init__(self, title):
        self.titles = title
        self.EnumWindows = ctypes.windll.user32.EnumWindows
        self.EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
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
        #    if 'Agilent VEE' in dic['App']:
            if dic['App'] == 'AnyDesk':
                filtered.append(dic)
        return filtered


class AppOperations:
    def __init__(self):
        self.titles = []
        self.generated_list = AppListGenerater(self.titles)

    def add_time(self, getflist):
        for dic in getflist:
            # print(datetime.now().strftime("%Y-%M-%D %h:%m:%s"))
            dic['time'] = str(datetime.now())
        return getflist

    def return_list(self):
        new_list = self.generated_list.filtered_list()
        return self.add_time(new_list)       


def main():
    global value
    try:
        a = AppOperations()
        output = a.return_list()
        if output:
            keys = output[0].keys()
            dict_writer = csv.DictWriter(file_obj, keys)
            dict_writer.writerows(output)
            file_obj.flush()
        print('old:' + str(output))
        time.sleep(2)
        if not value:
            main()
    except KeyboardInterrupt:
        print('Exit')
    finally:
        file_obj.close()


def report_excl(file_path):
    appsMap = {}
    with open(file_path, 'r') as logf:
        reader = csv.reader(logf, delimiter="\t")
        for i, line in enumerate(reader):
            if line:
                line_value = line[0].split(',')
                if line_value[0] not in appsMap:
                    appsMap[line_value[0]] = [line_value[1]]
                else:
                    appsMap[line_value[0]].append(line_value[1])

    with open(os.path.join(BASE_DIR, 'report.csv'), 'w') as report_csv:
        writer = csv.DictWriter(report_csv, fieldnames=["Application", "Starting Time", "End Time", "Execution Time"])
        writer.writeheader()

        for key, value in appsMap.items():
            print(key, value)
            writer.writerow({"Application": key, "Starting Time": value[0],
                             "End Time": value[-1], "Execution Time": ''})


def run_script():
    main()


def run_exe():
    os.system(os.path.join(BASE_DIR, os.path.join('exe', "AnyDesk.exe")))


if __name__ == "__main__":
    t1 = threading.Thread(target=run_script)
    t2 = threading.Thread(target=run_exe)
    t1.start()
    t2.start()
    exe = t2.join()
    if exe is None:
        value = True
        report_excl(os.path.join(BASE_DIR, filename))

    print('end')
