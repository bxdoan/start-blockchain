#!/usr/bin/env bash
s=$BASH_SOURCE ; s=$(dirname "$s") ; s=$(cd "$s" && pwd) ; SCRIPT_HOME="$s"

env="$SCRIPT_HOME/.env"

# check existing .env file
if [[ -f ${env} ]]; then source ${env}; fi

# check existing api ports
if [[ -z ${API_PORT} ]]; then API_PORT=5555; fi

function start () {
    pipenv run gunicorn -b 0.0.0.0:${API_PORT} --reload blockchain:api
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
esac