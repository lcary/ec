#!/bin/bash
set -e
module add openmind/singularity

cd /om2/user/lcary/ec
export SINGULARITYENV_PATH="/container/pypy3.5-6.0.0-linux_x86_64-portable/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/om2/user/lcary/julia/julia-1.1.1/bin"
export SINGULARITYENV_JULIA_DEPOT_PATH=/om2/user/lcary/.julia
singularity exec --bind $(pwd)/.. --bind ~/.julia container.img bash scripts/runjuliatest1.sh
