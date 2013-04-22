#!/usr/bin/python

import sys

sys.path.append("..")
import pymclevel  # https://github.com/mcedit/pymclevel
from pymclevel import *

if len(sys.argv) < 2:
    print "usage: %s filename" % (sys.argv[0],)
    sys.exit(1)

print "Loading",sys.argv[1]
region = regionfile.MCRegionFile(sys.argv[1], (0,0))

data = region.readChunk(0, 0)
chunkTag = nbt.load(buf=data)
print chunkTag

print chunkTag["Level"]["TileEntities"]
