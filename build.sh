PATH=$WORKSSPACE/venv/bin:/usr/local/bin:$PATH

which python3
which pip3
which virtualenv

python3 --version

if [ ! -d "~/.pip" ]; then
    echo "create .pip"
    mkdir ~/.pip
fi

if [ ! -f "~/.pip/pip.conf" ]; then
    echo "pip not exist"
    cat > ~/.pip/pip.conf <<EOF
[global]
index-url=https://pypi.tuna.tsinghua.edu.cn/simple
EOF
    echo "pip updated"
fi

if [ ! -d "venv" ]; then
  virtualenv -p /usr/bin/python3 venv
fi

echo "activate"
. venv/bin/activate

echo "install dependency"
pip3 install -r requirements-dev.txt
# pip3 install -r requirement.txt
