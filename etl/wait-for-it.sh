#!/usr/bin/env bash
#   Use this script to test if a given TCP host/port are available

WAITFORIT_cmdname=${0##*/}

echoerr() { if [[ $WAITFORIT_QUIET -ne 1 ]]; then echo "$@" 1>&2; fi }

wait_for() {
    local host="$1"
    local port="$2"
    local timeout="$3"
    local start_time=$(date +%s)
    while :
    do
        (echo > /dev/tcp/$host/$port) >/dev/null 2>&1 && return 0
        local now=$(date +%s)
        if [[ $timeout -gt 0 && $((now - start_time)) -ge $timeout ]]; then
            return 1
        fi
        sleep 1
    done
}

TIMEOUT=30
QUIET=0
HOST=""
PORT=""
CMD=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -q|--quiet)
        QUIET=1
        ;;
        -t|--timeout)
        TIMEOUT="$2"
        shift
        ;;
        --)
        shift
        CMD="$@"
        break
        ;;
        *)
        if [[ -z "$HOST" ]]; then
            HOST="$1"
        elif [[ -z "$PORT" ]]; then
            PORT="$1"
        fi
        ;;
    esac
    shift
done

if [[ "$HOST" == "" || "$PORT" == "" ]]; then
    echoerr "Usage: $WAITFORIT_cmdname host port [-t timeout] [-- command args]"
    exit 1
fi

wait_for "$HOST" "$PORT" "$TIMEOUT"
RESULT=$?
if [[ $RESULT -ne 0 ]]; then
    echoerr "$WAITFORIT_cmdname: timeout occurred after waiting $TIMEOUT seconds for $HOST:$PORT"
    exit 1
fi
if [[ "$CMD" != "" ]]; then
    exec $CMD
else
    exit 0
fi
