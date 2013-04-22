#!/usr/bin/python

import sys
import os
import numpy

# based on pymclevel
SECTOR_BYTES = 4096
SECTOR_INTS = SECTOR_BYTES / 4
CHUNK_HEADER_SIZE = 5
VERSION_GZIP = 1
VERSION_DEFLATE = 2

def main():
    if len(sys.argv) < 2:
        print "usage: %s filename" % (sys.argv[0],)
        sys.exit(1)

    print "Loading",sys.argv[1]

    load(sys.argv[1])

def load(path):
    data = file(path, "rb").read()
    filesize = len(data)

    n = 0
    offsetsData = data[0:SECTOR_BYTES]
    modTimesData = data[SECTOR_BYTES:SECTOR_BYTES * 2]

    freeSectors = [True] * (filesize / SECTOR_BYTES)
    freeSectors[0:2] = False, False

    offsets = numpy.fromstring(offsetsData, dtype='>u4')
    modTimes = numpy.fromstring(modTimesData, dtype='>u4')

    print offsets,modTimes

    for offset in offsets:
        sector = offset >> 8
        count = offset & 0xff

        for i in xrange(sector, sector + count):
            assert i < len(freeSectors), "Region file offset table points to sector {0} (past the end of the file)".format(i)
            assert freeSectors[i], "Unexpected free sector: {0}".format(i)

            freeSectors[i] = False

    def getOffset(self, cx, cz):
        cx &= 0x1f
        cz &= 0x1f
        return offsets[cx + cz * 32]

    print 

if __name__ == "__main__":
    main()

