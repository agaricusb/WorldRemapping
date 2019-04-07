#!/usr/bin/python
# Convert Rei Minimap waypoints to Journeymap
# Note: Journeymap apparently already has a Rei Minimap importer
import subprocess
import json
import os

output = subprocess.check_output(["./waypoints_152.sh"])
out_root = "/Applications/MultiMC.app/Contents/MacOS/instances/1.7.10s/minecraft/journeymap/data/mp/172~16~2~2~25567/waypoints"

for line in output.split("\n"):
    line = line.strip()
    if line == "": continue
    name, x, y, z, enabled, color = line.split(":")
    id = "%s_%s,%s,%s" % (name, x, y, z)
    j = {
            "id": id,
            "name": name,
            "icon": "waypoint-normal.png",
            "x": x,
            "y": y,
            "z": z,
            "r": 210,
            "g": 16,
            "b": 16,
            "enable": True,
            "type": "Normal",
            "origin": "ReiMinimap",
            "dimensions": [
                0
            ]
        }
    json_data = json.dumps(j, indent=1) 
    id = id.replace("/", "")
    path = os.path.join(out_root, "%s.json" % (id,))

    print path
    file(path, "wt").write(json_data)


