"# Desktop_application_catcher"

**INTRODUCTION**

    This application only for Win system
    This application track your activities and make a log for later use.

**HOW TO USE**

    Enter your filter application name inside the 'filter.txt'
    Run the autorun.exe

    It will run on your back ground and accourding to your filter list it will filter the
    application and make a csv file in your Documents directory(Win).

**Make Exe for Win 32**

    Open cmd
    Types given commands

    'set CONDA_FORCE_32BIT=1'
    'conda create -n <env_name> python=<version>'
    'activate <env_name>'
    'pip install pyinstaller'

    Go to your main file directory (Where 'if __name__ == "__main__"' is present)

    'pyinstaller --onefile --windowed --icon=<icon_name.ico> <main_file_name>'

    Go inside of dist folder and there you can find .exe file

    Reset you system to 64bit
    'set CONDA_FORCE_32BIT='

**Run Application when system restart/reboot Win System**
    
    In windows 
    1. run
    2. type 'shell:startup'
    3. create shortcut of your application
    4. copy and past inside shortcut directory.

**Reference**

    Image converter to .ico
    https://redketchup.io/icon/convert