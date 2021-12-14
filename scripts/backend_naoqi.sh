#!/bin/bash

source venv/bin/activate

port="${2:-8000}"

logSize="100000"

if [ $1 == "start" ]; then
  touch cltl-naoqi.log
  tail -n "$logSize" cltl-naoqi.log > cltl-naoqi.log.tmp && mv cltl-naoqi.log.tmp cltl-naoqi.log
  source venv/bin/activate
  nohup python -m cltl.naoqi --naoqi-ip 127.0.0.1 --port $port >> cltl-naoqi.log 2>&1 &
elif [ $1 == "run" ]; then
  source venv/bin/activate
  python -m cltl.naoqi --naoqi-ip 127.0.0.1 --port $port
elif [ $1 == "stop" ]; then
  ps aux  |  grep 'python -m cltl.naoqi'  | grep -v grep |  awk '{print $2}'  |  xargs kill
elif [ $1 == "state" ]; then
  echo "Process ID: $(ps aux  |  grep 'python -m cltl.naoqi'  | grep -v grep)"
else
    echo "Unknown command $1, use one of: start, run, stop, state"
fi
