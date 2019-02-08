#!/usr/bin/python

# Lookup missing mappings in patchfile for the user to fix

patchfile = file("patchfile.txt").readlines()
match_ids = __import__("match-ids")

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

dump152 = match_ids.readNEIDump("IDMap_dump-AA152-28-1-2019 at 17.38.21.625.txt")
dump125 = match_ids.readNEIDump("IDMap_dump-125.txt")

rdump152 = {v: k for k, v in dump152.items()}
rdump125 = {v: k for k, v in dump125.items()}

for id in sorted(ids):
    count = ids[id]

    found = findPatchfile(id)
    if found is None:
        maybe125 = rdump125.get(id)
    else:
        maybe125 = ""

    print id, count, found, rdump152.get(id), maybe125
