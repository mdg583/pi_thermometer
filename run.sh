#!/bin/bash
cd /home/pi/pi_thermo
python3 App.py > log.txt 2>&1 &
