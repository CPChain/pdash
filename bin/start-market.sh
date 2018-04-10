#!/bin/sh

curr_dir=`pwd`
cd ..
ROOT_PATH=`pwd`
export PYTHONPATH=$PYTHONPATH:$ROOT_PATH
nohup python cpchain/market/manage.py runserver 0.0.0.0:8000 &
cd $curr_dir
