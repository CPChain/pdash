#!/usr/bin/env bash

TOP_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"/../../

config=$TOP_DIR/"cpchain/cpchain.toml"

home_dir=$(awk '$1 == "rc_dir" {print $3}' $config | tr -d "'\"")
server_key=$(awk '$1 == "server_key" {print $3}' $config | tr -d "'\"")
server_crt=$(awk '$1 == "server_crt" {print $3}' $config | tr -d "'\"")

key_dir=$(dirname $home_dir/$server_key)
eval mkdir -p $key_dir
eval cd $key_dir

if [ -f "server.key"  -a -f "server.crt" ]; then
    echo "find old ssl key/cert under $key_dir"
    read -r -p "generate new ssl key/cert? [y/N]" input

else
    read -r -p "generate new ssl key/cert? [y/N]" input
fi

new_ssl_key_cert() {

    echo -e "\n..... generate server key .....\n"
    openssl genrsa -out server.key 2048

    echo -e "\n..... generate server CSR .....\n"
    echo "Ensure the FQDN (fully qualified domain name)"
    echo "matches the hostname of the serve"
    openssl req -new -key server.key -out server.csr

    echo -e "\n..... generate server certificate .....\n"
    openssl x509 -req -days 1024 -in server.csr -signkey server.key -out server.crt
}

case $input in
    [yY][eE][sS]|[yY])
        new_ssl_key_cert
        ;;

esac
