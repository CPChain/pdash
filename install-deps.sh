#!/bin/bash

cd "$(dirname $0)"

######### PIP PACKAGES
market_pkgs="
djangorestframework==3.7.3
django-rest-elasticsearch==0.4
django==2.0.3
psycopg2
toml==0.9.4
eth-keyfile
cryptography
web3
apscheduler
pytest-django
"

chain_pkgs="
eth-keyfile
web3
toml==0.9.4
cryptography
twisted
"

proxy_pkgs="
toml==0.9.4
ipfsapi
eth-keyfile
google-cloud
twisted
service_identity
treq
protobuf
cryptography
sqlalchemy
boto3
pyopenssl
web3
msgpack
kademlia
"

wallet_pkgs="
pyqt5==5.10.1
eth-keyfile
web3
qt5reactor
toml==0.9.4
"

pkgs="
pytest
pytest-cov
pylint
"

if test $# -eq 0; then
   echo "Usage: install-deps.sh {all|market|wallet|proxy|chain|...}"
   exit 1
fi

while test $# -gt 0
do
    case "$1" in
        market) pkgs="${pkgs}${market_pkgs}"
                ;;
        chain) pkgs="${pkgs}${chain_pkgs}"
               ;;
        proxy) pkgs="${pkgs}${proxy_pkgs}"
               ;;
        wallet) pkgs="${pkgs}${wallet_pkgs}"
                ;;
        all) set -- market chain proxy wallet
             ;;
    esac
    shift
done


if [ -n "$pkgs" ]; then
    printf "%s\n" $pkgs | xargs pip3 install
fi


# DEBIAN PACKAGES
# sudo apt install -y python3-pyqt5

# sudo apt install -y python3-twisted python3-treq

# sudo apt install -y python3-protobuf
# # compiler is only needed for dev.
# # sudo apt install -y protobuf-compiler python3-protobuf

# sudo apt install -y python3-cryptography python3-sqlalchemy python3-toml python3-boto3

# sudo apt install -y python3-flake8

# pip3 install pyopenssl

# pip3 install -r requirements-dev.txt

# openssl
# libssl-dev
