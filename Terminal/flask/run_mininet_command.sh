#!/bin/bash

command="$@"

tmux send-keys -t mininet_session "$command" Enter
