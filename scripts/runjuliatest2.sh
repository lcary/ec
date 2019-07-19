#!/bin/bash
source venv/bin/activate
cd /om2/user/lcary/ec
python bin/list.py -t 360 -g -i 1 -c 1 --dataset less-list-tasks --solver julia
