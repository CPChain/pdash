#!/usr/bin/env bash

cd "$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"/../kafka

case "$1" in
start)
	[ -f 'docker-compose' ] || wget https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m) -O docker-compose

	chmod a+x docker-compose

	./docker-compose -f docker-compose.yml up -d
	;;

stop)
	./docker-compose -f docker-compose.yml down
	;;
*)
	;;
esac
