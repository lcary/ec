#!/bin/bash
set -e
module add openmind/singularity

export SINGULARITYENV_PATH="/container/pypy3.5-6.0.0-linux_x86_64-portable/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/om2/user/lcary/julia/julia-1.1.1/bin"
singularity shell --bind $(pwd)/.. --bind ~/.julia container.img
