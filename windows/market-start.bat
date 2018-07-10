set PYTHONPATH=%CD%\..\;%CD%\Python\Python36\python36.zip;%CD%\Python\Python36\DLLs;%CD%\Python\Python36\DLLs\lib;%CD%\Python\Python36;%CD%\Python\Python36\lib;%CD%\Python\Python36;%CD%\Python\Python36\lib\site-packages;%CD%\Python\Python36\lib\site-packages\win32;%CD%\Python\Python36\lib\site-packages\win32\lib;%CD%\Python\Python36\lib\site-packages\Pythonwin

set CPCHAIN_HOME_CONFIG_PATH=%CD%\.cpchain\cpchain.toml

set PATH=%CD%\Python\Python36;%PATH%

python.exe ..\cpchain\market\manage.py runserver 0.0.0.0:8083
