#!/bin/bash
gnome-terminal -- bash -c "ryu-manager /home/owais/Desktop/DDoS-Detection-and-Mitigation/p1/controller/controller.py; exec bash" &
echo $ > /tmp/ryu.pid
