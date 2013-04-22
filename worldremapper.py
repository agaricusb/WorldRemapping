#!/usr/bin/python

import sys
import os
import numpy
import struct
import gzip
import zlib

# based on pymclevel
SECTOR_BYTES = 4096
SECTOR_INTS = SECTOR_BYTES / 4
CHUNK_HEADER_SIZE = 5
VERSION_GZIP = 1
VERSION_DEFLATE = 2
VERSION_GZIP = 1
VERSION_DEFLATE = 2


def main():
    if len(sys.argv) < 2:
        print "usage: %s filename" % (sys.argv[0],)
        sys.exit(1)

    print "Loading",sys.argv[1]

    load(sys.argv[1])


def load(path):
    regionData = file(path, "rb").read()
    filesize = len(regionData)

    n = 0
    offsetsData = regionData[0:SECTOR_BYTES]
    modTimesData = regionData[SECTOR_BYTES:SECTOR_BYTES * 2]

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

    def getOffset(cx, cz):
        cx &= 0x1f
        cz &= 0x1f
        return offsets[cx + cz * 32]

    def readChunk(cx, cz):
        cx &= 0x1f
        cz &= 0x1f
        offset = getOffset(cx, cz)
        assert offset != 0, "chunk not present: (%s, %s)" % (cx, cz)

        sectorStart = offset >> 8
        numSectors = offset & 0xff
        assert numSectors != 0, "chunk not present 2: (%s, %s)" % (cx, cz)

        assert sectorStart + numSectors <= len(freeSectors), "chunk not present 3: (%s, %s)" % (cx, cz)

        start = sectorStart * SECTOR_BYTES
        chunkData = regionData[start:start + numSectors * SECTOR_BYTES]
        assert len(chunkData) >= 5, "Chunk data is only %d bytes long (expected 5) at (%s, %s)" % (len(chunkData), cx, cz)

        length = struct.unpack_from(">I", chunkData)[0]
        format = struct.unpack_from("B", chunkData, 4)[0]
        chunkData = chunkData[5:length + 5]

        # decompress
        if format == VERSION_GZIP:
            return gzip.GzipFile(fileobj=StringIO(chunkData)).read()
        if format == VERSION_DEFLATE:
            return zlib.decompress(chunkData)

        assert False, "unsupported chunk compression format: %s at (%s, %s)" % (format, cx, cz)

    print [readChunk(0,0)]

if __name__ == "__main__":
    main()

