import os, glob, json

for fname in glob.glob(os.path.join('messages', 'state_*.json')):
    with open(fname) as f:
        jdata = json.load(f)
    if not jdata['programs']:
        os.remove(fname)
    print('removed: ', fname)
