#!/usr/bin/python

import sys

"""Load an NEI ID map dump into a dictionary of unlocalized name -> numeric ID"""
def readNEIDump(fn):
    m = {}
    # based on ModAnalyzer
    for line in file(fn).readlines():
        line = line.replace("\n", "")

        if line.startswith("Block. Name: ") or line.startswith("Item. Name: "):
            kind, info = line.split(": ", 1)
            unlocalizedName, id = info.split(". ID: ")
            m[unlocalizedName] = int(id)

    return m
 
def main():
    if len(sys.argv) < 3:
        print "usage: %s first-nei-dump second-nei-dump" % (sys.argv[0],)
        sys.exit(1)

    print readNEIDump(sys.argv[1])
    print readNEIDump(sys.argv[2])

if __name__ == "__main__":
    main()
