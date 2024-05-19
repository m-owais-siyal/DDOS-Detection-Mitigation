#!/bin/bash
gnome-terminal -- bash -c "sudo python /home/owais/Desktop/DDoS-Detection-and-Mitigation/p1/mininet/topology.py; exec bash" &
tmux_pid=$(tmux list-panes -t mininet_session -F "#{pane_pid}")
echo $tmux_pid > /tmp/mininet.pid
echo "Mininet started in tmux session 'mininet_session' with PID $tmux_pid"
