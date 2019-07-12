import os, glob, json, pprint
from collections import Counter

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


for fname in glob.glob(os.path.join('messages', 'state_*.json')):
    with open(fname) as f:
        jdata = json.load(f)
    if 'intermediates' in jdata:
        print('\nfile:', fname)
        print('-'*(5 + len(fname)))
        cap_points = Counter()
        for d in jdata['intermediates']:
            cap_points["value=%s" % d["capture_point"]] += 1
        normal = cap_points["value=2"] == len(jdata['programs'])
        if normal:
            normal = bcolors.OKGREEN + str(normal) + bcolors.ENDC
        else:
            normal = bcolors.FAIL + str(normal) + bcolors.ENDC

        try:
            deepest_search = 99 - min([d['maximumDepth'] for d in jdata['intermediates']])
        except ValueError:
            deepest_search = None

        out = {
            'deepest search depth': deepest_search,
            'total programs': len(jdata['programs']),
            'normal': normal,
            'capture points': json.dumps(cap_points, indent=2, sort_keys=True)
        }
        for k, v in out.items():
            print(k, end=": ")
            print(v)
        # pprint.pprint(out, indent=2)
    if 'stacks' in jdata:
        if jdata['programs'] and not jdata['stacks']:
            print('EMPTY STACK: ', fname)
