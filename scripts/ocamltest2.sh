#!/bin/bash
module add openmind/singularity
cd /om2/user/lcary/ec
singularity exec --bind /om2/user/lcary/ec/ /om2/user/lcary/ec/container.img python bin/list.py -t 360 -g -i 1 -c 1 --dataset less-list-tasks --solver ocaml
