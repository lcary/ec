#!/bin/bash
python bin/list.py -t 5 -RS 1 -i 1 -c 2 -g --taskBatchSize 10 --taskReranker randomShuffle --solver python
#python bin/list.py -t 1 -RS 1 -i 1 -c 2 -g --taskBatchSize 10 --solver python
#python bin/list.py -t 1 -RS 1 -i 1 -c 2 -g --taskBatchSize 10 --taskReranker randomShuffle --solver python --primitives tiny
python select_states.py
python check_depths.py
