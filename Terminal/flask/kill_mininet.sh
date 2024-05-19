#!/bin/bash
if [ -f /tmp/mininet.pid ]; then
    sudo kill -9 $(cat /tmp/mininet.pid)
    rm /tmp/mininet.pid
else
    echo "Mininet process not running"
fi
