#!/bin/bash
cd /home/owais/Desktop/DDoS-Detection-and-Mitigation/p1/website/dashboard/src
npm start &
echo $! > /tmp/react.pid
