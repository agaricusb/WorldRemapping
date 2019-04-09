#!/usr/bin/python
# Convert Journeymap waypoints to Dynmap markers
# https://github.com/webbukkit/dynmap/wiki/Using-markers
import subprocess
import json
import os

root = "/Applications/MultiMC.app/Contents/MacOS/instances/1.7.10s/minecraft/journeymap/data/mp/172~16~2~2~25567/waypoints"

files = os.listdir(root)

for fn in files:
    #if not fn.startswith("[152]") and not fn.startswith("hcsmp"): continue
    #if not (not fn.startswith("[152]") and not fn.startswith("hcsmp")): continue

    if fn.startswith('.') or fn.endswith('.zip'): continue

    path = os.path.join(root, fn)
    j = json.load(file(path))

    name = j["name"]
    x = j["x"]
    y = j["y"]
    z = j["z"]

    id = name.lower().replace(" ","_")
    for c in "[]:-": id = id.replace(c, "")  # TODO: why not .translate?
    if len(id) > 25: id = id[:25]

    if "Spawn: " in name:
        icon = "shield"
    elif "Logout: " in name:
        icon = "walk"
    elif "Base" in name:
        icon = "house"
    else:
        icon = "pin"

    cmd = 'dmarker add %s "%s" x:%s y:%s z:%s world:world icon:%s' % (
            id,
            name,
            x, y, z,
            icon)
    print cmd
