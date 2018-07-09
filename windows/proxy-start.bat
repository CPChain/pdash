set PYTHONPATH=%CD%\..\;%CD%\Python\Python36\python36.zip;%CD%\Python\Python36\DLLs;%CD%\Python\Python36\DLLs\lib;%CD%\Python\Python36;%CD%\Python\Python36\lib;%CD%\Python\Python36;%CD%\Python\Python36\lib\site-packages;%CD%\Python\Python36\lib\site-packages\win32;%CD%\Python\Python36\lib\site-packages\win32\lib;%CD%\Python\Python36\lib\site-packages\Pythonwin

set CPCHAIN_HOME_CONFIG_PATH=%CD%\.cpchain\cpchain-proxy.toml

set PATH=%CD%\Python\Python36;%PATH%

python.exe ..\bin\proxy-start --tracker 127.0.0.1:8101 --boot_node 127.0.0.1:8201
