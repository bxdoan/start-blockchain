#!/usr/bin/env bash

function start () {
    pipenv run gunicorn -b 127.0.0.1:5000 --reload app:api
}

function stop () {
    ps -ef | grep gunicorn | awk '{print $2}' | xargs kill -9
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    *)
    echo "Usage: run.sh {start|stop}"
    exit 1
esac#!/usr/bin/env bash