#!/usr/bin/python

# Lookup missing mappings in patchfile for the user to fix

patchfile = file("patchfile.txt").readlines()

ids = {}
for line in file("un").readlines():
    line = line.strip()
    count, id = line.split()
    count = int(count)
    id = int(id)
    ids[id] = count

def findPatchfile(id):
    for line in patchfile:
        if line.startswith(str(id) + " -> "):
            return "Found already patched:" + line.strip()
            #raise SystemExit
        if line.startswith("# " + str(id) + " -> "):
            return line.strip()
    return None

for id in sorted(ids):
    count = ids[id]

    found = findPatchfile(id)

    print id, count, found
