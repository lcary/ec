#!/bin/bash
source venv/bin/activate
cd /om2/user/lcary/ec
python bin/list.py -t 360 -g -i 10 -c 1 --dataset more-list-tasks --solver julia
