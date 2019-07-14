import sys, time, os
import json

filename = sys.argv[1]

try:
    filter_mode = sys.argv[2]
except IndexError:
    filter_mode = False

with open(filename) as f:
    d = json.load(f)

def explore_children(n, path, log):
    if isinstance(n, list):
        for i in n:
            explore_children(i, path, log)
        return
    else:
        # print(n)
        # return
        try:
            name = n["name"]
        except KeyError:
            name = "node({})".format(n["capture_point"])
        except KeyError:
            name = -1

        children = n.get("children", [])

        path = path + [name]

        if "yields:" in n:
            log = log + [
                {
                    "capture_point": n["capture_point"],
                    "method": n["method"],
                    "yields": n["yields:"],
                }
            ]
        elif "note" in n:
            log = log + [
                {
                    "capture_point": n["capture_point"],
                    "method": n["method"],
                    "note": n["note"],
                }
            ]
        elif "capture_point" in n:
            log = log + [{"capture_point": n["capture_point"], "method": n["method"]}]

        if not children:
            pstr = " -> ".join(list(map(str, path)))
            print(pstr)
            print("-" * len(pstr))
            if log:
                for msg in log:
                    print(msg)
            print()
            return
        else:
            for c in children:
                explore_children(c, path, log)
            return


def filter_explore_children(n, path, log, filter_list):
    if isinstance(n, list):
        for i in n:
            filter_explore_children(i, path, log, filter_list)
        return
    else:
        # print(n)
        # return
        try:
            name = n["name"]
        except KeyError:
            name = "node({})".format(n["capture_point"])
        except KeyError:
            name = -1

        children = n.get("children", [])

        path = path + [name]
        log = log + [{i:n[i] for i in n if i!='children'}]

        if not children:
            if filter_list == 'any' or n.get("capture_point") in filter_list:
                fname = 'filter_explore_children_{}'.format(time.time())
                fname = os.path.join('messages', 'traverse', fname)
                with open(fname, 'w') as f:
                    json.dump(log, f, indent=2)
                print('wrote ', fname)
        else:
            for c in children:
                filter_explore_children(c, path, log, filter_list)
            return


if filter_mode:
    try:
        filter_list = list(map(int, filter_mode.split(',')))
    except Exception as e1:
        try:
            assert filter_mode.strip().lower() == 'any'
        except AssertionError:
            raise e1
        else:
            filter_list = 'any'
    path = []
    log = []
    filter_explore_children(d["stacks"], path, log, filter_list)
else:
    path = []
    log = []
    explore_children(d["stacks"], path, log)
