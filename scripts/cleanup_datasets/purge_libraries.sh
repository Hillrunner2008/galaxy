#!/bin/sh

cd `dirname $0`/../..
#python ./scripts/cleanup_datasets/cleanup_datasets.py ./universe_wsgi.ini -d 10 -4 -r $@ >> ./scripts/cleanup_datasets/purge_libraries.log
python ./scripts/cleanup_datasets/cleanup_datasets.py ./universe_wsgi.ini -d 2 -4 -r $@ >> ./scripts/cleanup_datasets/purge_libraries.log
