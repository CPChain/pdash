#!/usr/bin/env bash

TOP_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"/../../

config=$TOP_DIR/"cpchain/cpchain.toml"

home_dir=$(awk '$1 == "home" {print $3}' $config | tr -d "'\"")
server_key=$(awk '$1 == "server_key" {print $3}' $config | tr -d "'\"")
server_crt=$(awk '$1 == "server_crt" {print $3}' $config | tr -d "'\"")

key_dir=$(dirname $home_dir/$server_key)
eval mkdir -p $key_dir
eval cd $key_dir

if [ -f "server.key"  -a -f "server.crt" ]; then
    python3 $TOP_DIR/cpchain/proxy/server.py
    exit
fi

deploy_ssl_server() {

    echo "Deploy SSL server"

    echo -e "\n..... generate server key .....\n"
    openssl genrsa -out server.key 2048

    echo -e "\n..... generate server CSR .....\n"
    echo "Ensure the FQDN (fully qualified domain name)"
    echo "matches the hostname of the serve"
    openssl req -new -key server.key -out server.csr

    echo -e "\n..... generate server certificate .....\n"
    openssl x509 -req -days 1024 -in server.csr -signkey server.key -out server.crt

    python3 $TOP_DIR/cpchain/proxy/server.py
}

local_self_test() {
    echo "Simply run local self-test"

    eval cp $TOP_DIR/$server_key ./
    eval cp $TOP_DIR/$server_crt ./

    python3 $TOP_DIR/cpchain/proxy/server.py
}


read -r -p "Enter 'Y' to deploy your SSL server (or 'N' to simply run local self-test)? [y/N] " input

case $input in
    [yY][eE][sS]|[yY])
        deploy_ssl_server
        ;;

    [nN][oO]|[nN])
        local_self_test
        ;;

    *)
        echo "Invalid input..."
        ;;
esac
