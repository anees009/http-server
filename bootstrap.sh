#!/bin/sh
if [[ -z "$SERVE_PORT" ]]; then
    echo "Must provide PORT in environment" 1>&2
    exit 1
fi
export FLASK_APP=./restapi/main.py
python -m flask --debug run -h 0.0.0.0 --port=$SERVE_PORT

