#!/bin/bash

mkdir -p "$HOME/tmp"
PIDFILE="$HOME/tmp/myprogram.pid"

if [ -e "${PIDFILE}" ] && (ps -u $(whoami) -opid= | ps -p $(cat ${PIDFILE}) > /dev/null); then
  echo "Already running."
  exit 99
fi

cd $HOME/aivle-slurm/aivle_worker/
. aivle_worker_venv/bin/activate
python -m aivle_worker & echo $! > "${PIDFILE}"
chmod 644 "${PIDFILE}"
