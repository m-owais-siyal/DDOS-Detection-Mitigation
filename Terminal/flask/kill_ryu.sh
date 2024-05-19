#!/bin/bash
if [ -f /tmp/ryu.pid ]; then
    kill -9 $(cat /tmp/ryu.pid)
    rm /tmp/ryu.pid
else
    echo "Ryu process not running"
fi
