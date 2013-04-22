#!/usr/bin/python

import sys
import os
import re

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

def matchAll(before, after, configsBefore, configsAfter):
    mapping = {}

    for oldName, oldID in before.iteritems():
        # check NEI dumps first
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

        # search configs for likely configuration names, by ID
        possibleOldNames = []
        for config, keys in configsBefore.iteritems():
            for key, id in keys.iteritems():
                if id == oldID:
                    possibleOldNames.append(key)

                if id > 4095 and id - 256 == oldID:
                    possibleOldNames.append(key)

        # .. then try to match with new configs by name
        possibleNewNames = []
        for possibleOldName in possibleOldNames:
            for config, keys in configsAfter.iteritems():
                for key, id in keys.iteritems():
                    if key == possibleOldName:
                        possibleNewNames.append((config, key, id))
        

        print oldID,possibleOldNames,possibleNewNames

        mapping[oldID] = (None, oldName, None, "no match")

    return mapping

def scanConfigs(dirname):
    configKeys = {}
    for root, dirs, files in os.walk(dirname):
        for f in files:
            path = os.path.join(root, f)
            configKeys[path] = scanConfig(path)

    return configKeys

"""Get key/value pairs for approximately-read configuration file."""
def scanConfig(fn):
    keys = {}

    for line in file(fn, "rt").readlines():
        line = line.replace("\n", "")
        line = line.strip()

        match = re.match(r"(\w+)=(\d+)", line)
        if match:
            key = match.group(1)
            id = int(match.group(2))

            keys[key] = id

    return keys

def main():
    if len(sys.argv) < 5:
        print "usage: %s first-nei-dump second-nei-dump first-configs-dir second-configs-dir" % (sys.argv[0],)
        sys.exit(1)

    before = readNEIDump(sys.argv[1])
    after = readNEIDump(sys.argv[2])

    configsBefore = scanConfigs(sys.argv[3])
    configsAfter = scanConfigs(sys.argv[4])

    mapping = matchAll(before, after, configsBefore, configsAfter)

    for k, v in mapping.iteritems():
        if v[0] is not None:
            print "%s -> %s # %s " % (k, v[0], v[1:])
        else:
            print "# %s -> %s" % (k, v)
 

if __name__ == "__main__":
    main()
