#!/bin/bash
if [ -f /tmp/flask.pid ]; then
    kill -9 $(cat /tmp/flask.pid)
    rm /tmp/flask.pid
else
    echo "Flask process not running"
fi
