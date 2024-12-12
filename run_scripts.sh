#!/bin/bash
/usr/bin/python3 /home/pi/Desktop/server/bell.py &
/usr/bin/python3 /home/pi/Desktop/server/processing.py &
/usr/bin/python3 /home/pi/Desktop/server/Schedulerfinal.py &
wait
