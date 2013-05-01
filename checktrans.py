#!/usr/bin/python

# Check for 'transitive' conversions in patch file:
#   a -> b -> c
# usually unintentional..

def readPatchFile(fn):
    maps = []
    for line in file(fn, "rt").readlines():
        line = line.replace("\n", "")
        if "#" in line: line = line[:line.index("#")]
        tokens = line.split(" -> ")
        if len(tokens) != 2: continue
        before, after = tokens
        before = before.strip()
        after = after.strip()
       
        maps.append((before, after))
    return maps

def main():
    maps = readPatchFile("patchfile.txt")
    converted = {}
    count = 0
    for before, after in maps:
        if converted.has_key(before): # TODO: check for metadata
            print "Transitive conversion: %s -> %s -> %s" % (converted[before], before, after)
            count += 1

        converted[after] = before
    print "Found %s transitive relations" % (count,)


if __name__ == "__main__":
    main()
        
