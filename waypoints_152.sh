#!/bin/sh
# Shift waypoints from Rei Minimap and prepend tag
#grep -v '^Death Point:' /Applications/MultiMC.app/Contents/MacOS/instances/1.5.2AA/minecraft/mods/rei_minimap/172.16.0.2.DIM0.points|more
cat /Applications/MultiMC.app/Contents/MacOS/instances/1.5.2AA\ \(Migrated\)1/minecraft/mods/rei_minimap/172.16.0.2.DIM0.points | grep -v '^Death Point:' | awk -F: '{print "[152] "$1":"($2 - 25600)":"$3":"$4":"$5":"$6}'
