#!/usr/bin/env bash
s=$BASH_SOURCE ; s=$(dirname "$s") ; s=$(cd "$s" && pwd) ; SCRIPT_HOME="$s"

env="$SCRIPT_HOME/.env"

# check existing .env file
if [[ -f ${env} ]]; then source ${env}; fi

# check existing api ports
if [[ -z ${API_PORT1} ]]; then API_PORT1=5555; fi
if [[ -z ${API_PORT2} ]]; then API_PORT2=5556; fi

function start1 () {
    pipenv run gunicorn -b 0.0.0.0:${API_PORT1} --reload blockchain:api
}

function start2 () {
    pipenv run gunicorn -b 0.0.0.0:${API_PORT2} --reload blockchain:api
}

function stop () {
    ps -ef | grep gunicorn | awk '{print $2}' | xargs kill -9
}

case "$1" in
    start1)
        start1
        ;;
    start2)
        start2
        ;;
    stop)
        stop
        ;;
    *)
    echo "
    Usage: run.sh {start1|start2|stop}
    Explain:
    start1 -> server will run on 0.0.0.0:$API_PORT1
    start2 -> server will run on 0.0.0.0:$API_PORT2
    stop   -> stop all server.
    "
    exit 1
esac