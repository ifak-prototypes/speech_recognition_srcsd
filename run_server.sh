#!/usr/bin/env bash

if [ ! -d "./venv" ]; then
    echo No virtual environment found.
    echo You need to run "bash ./bin/prepare.sh" first.
fi

source ./venv/bin/activate

python src/srcsd/server.py