#!/usr/bin/python

# python match-ids.py IDMap_dump-AA152-28-1-2019\ at\ 17.38.21.625.txt 1710-dumps /Applications/MultiMC.app/Contents/MacOS/instances/1.5.2AA\ \(Migrated\)1/minecraft/config/ /Applications/MultiMC.app/Contents/MacOS/instances/1.7.10s/minecraft/config

import sys
import os
import re

VANILLA_BLOCK_END = 158 # 1.5.2 dropper
VANILLA_ITEM_END = 408 # 1.5.2

global id2info

"""Read 1.7.10 circa NEI dumps, directory of .csv files"""
def readNEIDumpDir(dir):
    global id2info
    def readCSV(fn, name2id, id2info, skip_id_le):
        f = file(fn, "rt")
        for line in f.readlines():
            if line.startswith("Name,ID,"): continue
            name, id, has_itemblock, mod, cls = line.strip().split(",")
            id = int(id)

            if id <= skip_id_le:
                # skip vanilla IDs since they don't change
                continue

            if name2id.has_key(name) and id != name2id[name]:
                print "Duplicate name %s assigned to both id %s and %s" % (name, name2id[name], id)
                raise SystemExit
            name2id[name] = id

            if id2info.has_key(id) and name != id2info[id][0]:
                print "Duplicate id %s assigned to both %s and %s" % (id, id2info[id], (name, mod, cls))
                raise SystemExit
            if mod == "null": mod = ""
            id2info[id] = (name, mod, cls)

        return name2id, id2info

    name2id = {}
    id2info = {}

    readCSV(os.path.join(dir, "block.csv"), name2id, id2info, VANILLA_BLOCK_END)
    readCSV(os.path.join(dir, "item.csv"), name2id, id2info, VANILLA_ITEM_END) 

    #import pprint
    #pprint.pprint(id2info)
    #raise SystemExit
    return name2id

"""Load an NEI ID map dump into a dictionary of unlocalized name -> numeric ID"""
def readNEIDump(fn):
    if os.path.isdir(fn): return readNEIDumpDir(fn)

    m = {}
    # based on ModAnalyzer
    for line in file(fn).readlines():
        line = line.replace("\n", "")

        if line.startswith("Block. Name: ") or line.startswith("Item. Name: "):
            kind, info = line.split(": ", 1)
            unlocalizedName, id = info.split(". ID: ")
            id = int(id)

            if line.startswith("Block. Name: ") and id <= VANILLA_BLOCK_END: continue
            if line.startswith("Item. Name: ") and id <= VANILLA_ITEM_END: continue

            while m.has_key(unlocalizedName):
                unlocalizedName += "_" # overloaded name

            m[unlocalizedName] = int(id)

    return m

replacePrefixes = {
    "tile.bop.": "BiomesOPlenty:", "item.bop.": "BiomesOPlenty:",
    "tile.extrabiomes.": "ExtrabiomesXL:",
    "tile.immibis/redlogic:": "RedLogic:redlogic.",
    "item.AppEng.": "appliedenergistics2:item.", "tile.AppEng.": "appliedenergistics2:tile.",
    "tile.railcraft.": "Railcraft:", "item.railcraft.": "Railcraft:",
    "tile.myst.": "Mystcraft:",
    "tile.immibis.microblock.": "ImmibisMicroblocks:",
    "tile.tconstruct.": "TConstruct:", "item.tconstruct.": "TConstruct:",
    "tile.thermalexpansion.": "ThermalExpansion:",
    "tile.powerconverters.": "PowerConverters3:",
    "tile.openblocks.": "OpenBlocks:",
    "tile.mfr.": "MineFactoryReloaded:", "item.mfr.": "MineFactoryReloaded:",
    "item.spear.": "weaponmod:spear.", "item.halberd.": "weaponmod:halberd.", "item.battleaxe.": "weaponmod:battleaxe.",
    "item.knife.": "weaponmod:knife.", "item.flail.": "weaponmod:flail.", "item.boomerang.": "weaponmod:boomerang.",
    "item.musketbayonet.": "weaponmod:musketbayonet.", "item.katana.": "weaponmod:katana.",
    "item.Atum:": "atum:item.", "tile.Atum:": "atum:tile.",
    "tile.Biblio": "BiblioCraft:Biblio",
    "tile.MoC": "MoCreatures:MoC",
}

def ucfirst(s):
    return s[0].upper() + s[1:]

def lcfirst(s):
    return s[0].lower() + s[1:]

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

        newName = oldName.replace("item.", "").replace("item.", "")
        if after.has_key(newName):
            newID = after[newName]
            mapping[oldID] = (newID, oldName, newName, "replace")
            del after[newName]
            continue

        for k, v in replacePrefixes.items():
            if oldName.startswith(k):
                newName = v + oldName[len(k):]
                break
        n = newName.split(":")
        if len(n) > 1: m = n[1].split(".")
        if newName.startswith("Mystcraft:"): newName = n[0] + ":" + "Block" + ucfirst(n[1])
        if newName.startswith("TConstruct:"): newName = n[0] + ":" + lcfirst(n[1])
        if newName.startswith("atum:"): newName = n[0] + ":" + m[0] + "." + lcfirst(m[1])

        if after.has_key(newName):
            newID = after[newName]
            mapping[oldID] = (newID, oldName, newName, "namespace")
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
        

        mapping[oldID] = (None, oldName, newName, "no match")

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

    for k in sorted(mapping.keys()):
        v = mapping[k]
        if v[0] is not None:
            print "%s -> %s # %s " % (k, v[0], v[1:])
        else:
            print "# %s -> %s" % (k, v)
 

if __name__ == "__main__":
    main()
