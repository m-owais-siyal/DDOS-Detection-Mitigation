#!/bin/bash
cd /home/owais/Desktop/DDoS-Detection-and-Mitigation/p1/website/backend/
gunicorn --pythonpath /home/owais/Desktop/DDoS-Detection-and-Mitigation/p1/website/backend -w 4 -b 0.0.0.0:5000 server:app &
echo $! > /tmp/flask.pid
