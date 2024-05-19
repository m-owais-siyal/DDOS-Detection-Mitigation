#!/bin/bash
if [ -f /tmp/react.pid ]; then
    pid=$(cat /tmp/react.pid)
    if kill -0 $pid 2>/dev/null; then
        kill -9 $pid
        rm /tmp/react.pid
        echo "React process killed successfully."
    else
        echo "React process not running or PID is incorrect."
    fi
else
    echo "React process not running."
fi