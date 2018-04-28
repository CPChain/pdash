#!/bin/sh
echo "all:$@"
echo "module name:$1"
echo "jenkins:$2"
curdir=`pwd`
echo "start build $1"
modulename="$1"
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
sudo /bin/sh install-deps.sh $@

ROOT_PATH=`pwd`
export PYTHONPATH=$PYTHONPATH:$ROOT_PATH


while test $# -gt 0
do
    case "$1" in
        market) testcase=""
                ;;
        chain) testcase="-k 'test_* and not SSLServerTestCase'"
               ;;
        proxy) testcase="-k 'test_*'"
               ;;
        wallet) testcase="-k 'test_* and not test_dispute and test_normal_process and test_timeout and test_withdraw_order'"
                ;;
    esac
    shift
done

echo "testcase modulename:$modulename, param:$testcase"
if [ -n "$testcase" ]; then
    echo "=== unit test param:$testcase ==="
    py.test tests/$modulename  --junitxml=test_report.xml --cov-report=xml --cov=./  $testcase
fi
