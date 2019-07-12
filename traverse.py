import sys

filename = sys.argv[1]
import json

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


path = []
log = []
explore_children(d["stacks"], path, log)
