#!/bin/sh
echo "module name:$1"
echo "jenkins:$2"
curdir=`pwd`
echo "start build $1"
cd ../
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

echo "install dependency for $1"
./install-deps.sh $*

ROOT_PATH=`pwd`
export PYTHONPATH=$PYTHONPATH:$ROOT_PATH

while test $# -gt 0
do
    case "$1" in
        market) testcase="'not test_1 and not test_2'"
                ;;
        chain) testcase="'not SSLServerTestCase'"
               ;;
        proxy) testcase="'not test_dispute and not test_normal_process and not test_timeout and not test_withdraw_order'"
               ;;
        wallet) testcase="'not test_dispute and test_normal_process and test_timeout and test_withdraw_order'"
                ;;
    esac
    shift
done

if [ -n "$testcase" ]; then
    echo "=== unit test param:$testcase ==="
    py.test tests/$module_name  --junitxml=test_report.xml --cov-report=xml --cov=./ -k  $testcase
fi
