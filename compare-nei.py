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

def matchAll(before, after):
    mapping = {}

    for oldName, oldID in before.iteritems():
        if after.has_key(oldName):
            # exact match
            newName = oldName
            newID = after[newName]
            mapping[oldID] = (newID, oldName, newName, "exact")
            del after[newName]
            continue

        newName = oldName.replace("item.", "").replace("tile.", "")
        if after.has_key(newName):
            # IC2 dropped the loc prefixes..don't know why
            newID = after[newName]
            mapping[oldID] = (newID, oldName, newName, "replace")
            del after[newName]
            continue

        fuzzyOldName = getFuzzyName(oldName)
        if fuzzyOldName is not None:
            for newName, newID in after.iteritems():
                fuzzyNewName = getFuzzyName(newName)

                found = False
                if fuzzyOldName == fuzzyNewName:
                    mapping[oldID] = (newID, oldName, newName, "fuzzy "+fuzzyNewName)
                    del after[newName]
                    found = True
                    break
                if found: break
            if found: continue

        mapping[oldID] = (None, oldName, None, "no match")

    return mapping

def getFuzzyName(name):
    try:
        import fuzzy # sudo easy_install fuzzy - fast Python phonetic algorithms: https://pypi.python.org/pypi/Fuzzy
    except ImportError:
        return None

    return fuzzy.DMetaphone()(name)[0]

def main():
    if len(sys.argv) < 3:
        print "usage: %s first-nei-dump second-nei-dump" % (sys.argv[0],)
        sys.exit(1)

    before = readNEIDump(sys.argv[1])
    after = readNEIDump(sys.argv[2])

    mapping = matchAll(before, after)

    for k, v in mapping.iteritems():
        print k,v

 

if __name__ == "__main__":
    main()
