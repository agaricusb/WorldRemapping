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
    "tile.mfr.liquid.": "MineFactoryReloaded:",
    "tile.mfr.": "MineFactoryReloaded:", "item.mfr.": "MineFactoryReloaded:",
    "item.spear.": "weaponmod:spear.", "item.halberd.": "weaponmod:halberd.", "item.battleaxe.": "weaponmod:battleaxe.",
    "item.knife.": "weaponmod:knife.", "item.flail.": "weaponmod:flail.", "item.boomerang.": "weaponmod:boomerang.",
    "item.musketbayonet.": "weaponmod:musketbayonet.", "item.katana.": "weaponmod:katana.",
    "item.Atum:": "atum:item.", "tile.Atum:": "atum:tile.",
    "tile.Biblio": "BiblioCraft:Biblio",
    "tile.MoC": "MoCreatures:MoC",
    "tile.enderIO:": "EnderIO:",
    "tile.SC2": "StevesCarts:",
    "tile.TF": "TwilightForest:tile.TF", "item.TF": "TwilightForest:item.TF",
    "tile.extrautils:": "ExtraUtilities:",
    "item.Aquaculture": "Aquaculture:item.",
}

manual = {
    "tile.fyriteOre": "netherrocks:fyrite_ore", "tile.fyriteBlock": "netherrocks:fyrite_block",
    "tile.malachiteOre": "netherrocks:malachite_ore", "tile.malachiteBlock": "netherrocks:malachite_block",
    "tile.ashstoneOre": "netherrocks:ashstone_ore", "tile.ashstoneBlock": "netherrocks:ashstone_block",
    "tile.illumeniteOre": "netherrocks:illumenite_ore", "tile.illumeniteBlock": "netherrocks:illumenite_block",
    "tile.dragonstoneOre": "netherrocks:dragonstone_ore", "tile.dragonstoneBlock": "netherrocks:dragonstone_block",
    "tile.argoniteOre": "netherrocks:argonite_ore", "tile.argoniteBlock": "netherrocks:argonite_block",
    "tile.netherFurnaceOn": "netherrocks:nether_furnace",

    "tile.thermalexpansion.ore": "ThermalFoundation:Ore",

    "tile.extrabiomes.leaves": "ExtrabiomesXL:leaves_1",
    "tile.extrabiomes.leaves_": "ExtrabiomesXL:leaves_4",

    # Forgotten Nature
    "tile.newCrops1": "ForgottenNature:newCrops1",
    "tile.newCrops2": "ForgottenNature:newCrops2",
    "tile.newCrops3": "ForgottenNature:newCrops3",
    "tile.newCrops4": "ForgottenNature:newCrops4",
    "tile.newCrops5": "ForgottenNature:newCrops5",

    "tile.Crystal Mushroom Block": "ForgottenNature:cMushroomBlock",
    "tile.Crystal Mushroom": "ForgottenNature:cMushroom",

    "tile.Flowers": "ForgottenNature:newflowers",

    "tile.Half Plank": "ForgottenNature:halfPlank",
    "tile.Half Plank_": "ForgottenNature:halfPlank2",
    "tile.Half block": "ForgottenNature:FNHalfStone",
    "tile.flowerPot1": "ForgottenNature:flowerPot",
    #"tile.flowerPot2": "ForgottenNature:flowerPot",
    #"tile.flowerPot3": "ForgottenNature:flowerPot",
    #"tile.flowerPot4": "ForgottenNature:flowerPot",


    "tile.stairsWood0": "ForgottenNature:FNWStairs1",
    "tile.stairsWood1": "ForgottenNature:FNWStairs2",
    "tile.stairsWood2": "ForgottenNature:FNWStairs3",
    "tile.stairsWood3": "ForgottenNature:FNWStairs4",
    "tile.stairsWood4": "ForgottenNature:FNWStairs5",
    "tile.stairsWood5": "ForgottenNature:FNWStairs6",
    "tile.stairsWood6": "ForgottenNature:FNWStairs7",
    "tile.stairsWood7": "ForgottenNature:FNWStairs8",
    #"tile.stairsWood8": "ForgottenNature:FNWStairs9", # 9 is missing
    "tile.stairsWood9": "ForgottenNature:FNWStairs10",
    "tile.stairsWood10": "ForgottenNature:FNWStairs11",
    "tile.stairsWood11": "ForgottenNature:FNWStairs12",
    "tile.stairsWood12": "ForgottenNature:FNWStairs13",
    "tile.stairsWood13": "ForgottenNature:FNWStairs14",
    "tile.stairsWood14": "ForgottenNature:FNWStairs15",

    "tile.stairsStone1": "ForgottenNature:FNSStairs1",
    "tile.stairsStone2": "ForgottenNature:FNSStairs2",
    "tile.stairsStone3": "ForgottenNature:FNSStairs3",
    "tile.stairsStone4": "ForgottenNature:FNSStairs4",

    "tile.Stone2": "ForgottenNature:FNStone",

    "tile.crystalBlock": "ForgottenNature:crystalBlock",
    "tile.crystalStone": "ForgottenNature:crystalStone",
    "tile.crystalWood": "ForgottenNature:crystalWood",

    "tile.fruit": "ForgottenNature:FNFruit",

    "tile.Rope": "ForgottenNature:rope",
    
    "tile.immibis/infinitubes:cable": "InfiniTubes:infinitubes.infinitube",
    "tile.immibis/chunkloader:chunkloader": "DimensionalAnchors:chunkloader",

    "tile.BlockMetaID_Block": "gregtech:gt.blockcasings4", # loose match, different meta (Advanced Machine Block :0 -> ?, Fusion Coil :1 -> :7)
    "tile.GT_LightSource": "gregtech:gt.blockcasings5", # not really
    "tile.BlockMetaID_Machine": "gregtech:gt.blockmachines",
    "tile.BlockMetaID_Ore": "gregtech:gt.blockores",
    "tile.BlockMetaID_Block2": "gregtech:gt.blockmetal1", # different metals

    "tile.mfr.liquid.chocolatemilk.still": "MineFactoryReloaded:chocolatemilk.still",
    "tile.mfr.decorativestone": "MineFactoryReloaded:stone",
}

direct = {
    #1144: (, "Immibis peripherals.lan-wire.id"),
    #1145: (, "Immibis peripherals.block.id"),
    1146: (2705, "Immibis infinitubes.machine.id/InfiniTubes:infinitubes.machine"),
    1148: (2708, "Immibis liquidxp.machine.id/LiquidXP:liquidxp.machine"),
    
    1150: (3697, "Immibis tubestuff.id/Tubestuff:machine"),
    1151: (3698, "Immibis tubestuff.storage.id/Tubestuff:storage"),

    ## Forgotten Nature

    # ambiguous with vanilla
    2573: (3821, "ForgottenNature:nGlass/tile.glass"), 
    2606: (3792, "ForgottenNature:nFence/tile.fence"),

    # tile.null
    2608: (3823, "Forgotten Nature groundID/oneWayCamo?"),

    2609: (3772, "Forgotten Nature leafIDIndex+0/red maple"),
    2610: (3773, "Forgotten Nature leafIDIndex+1/sequoia"),
    2611: (3774, "Forgotten Nature leafIDIndex+2/swamp willow"),
    2612: (3775, "Forgotten Nature leafIDIndex+3/beech"),
    2613: (3776, "Forgotten Nature leafIDIndex+4/lemon"),
    2614: (3777, "Forgotten Nature leafIDIndex+5/huckleberry"),
    
    2615: (3792, "Forgotten Nature leafIDIndex+6/crystal"),
    2616: (3779, "Forgotten Nature leafIDIndex+7/nether ash"),

    2620: (3778, "Forgotten Nature logIDindex+0/cherry log"),
    2621: (3779, "Forgotten Nature logIDindex+1/desert willow"),
    2622: (3780, "Forgotten Nature logIDindex+2/bukkit log"),
    2623: (3781, "Forgotten Nature logIDindex+3/cherry log*"),
    2624: (3782, "Forgotten Nature logIDindex+4/nether ash log*"),

    2630: (3786, "Forgotten Nature plankID/ForgottenNature:FNPlanks1"),
    2631: (3787, "Forgotten Nature plankID2/ForgottenNature:FNPlanks2"),

    2633: (3783, "Forgotten Nature sapIDindex+0/desert ironwood sapling"),
    2634: (3784, "Forgotten Nature sapIDindex+1/palm sapling"),
    2635: (3785, "Forgotten Nature sapIDindex+2/huckleberry bushling"),

    2640: (3762, "Forgotten Nature torchID/ForgottenNature:Crystal Torch"),
}

def ucfirst(s):
    return s[0].upper() + s[1:]

def lcfirst(s):
    return s[0].lower() + s[1:]

def to_snakecase(s):
    return re.sub("([A-Z])", lambda x: "_" + x.group(1).lower(), "fooBar")

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

        if manual.has_key(oldName):
            newName = manual[oldName]
            newID = after[newName]
            mapping[oldID] = (newID, oldName, newName, "manual")
            del after[newName]
            continue

        if direct.has_key(oldID):
            newName = direct[oldID][1]
            newID = direct[oldID][0]
            mapping[oldID] = (newID, oldName, newName, "direct")
            #del after[newName]
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


        if (oldName.startswith("item") and oldName[4].isupper()) or (oldName.startswith("block") and oldName[5].isupper()) or oldName.startswith("reactor"):
            if after.has_key("IC2:" + oldName):
                newName = "IC2:" + oldName
                newID = after[newName]
                mapping[oldID] = (newID, oldName, newName, "unprefix")
                del after[newName]
                continue



        if oldName.startswith("item.") or oldName.startswith("tile."):
            unprefixed = ".".join(oldName.split(".")[1:]).lower()
            possible = []
            for k in after.keys():
                other = k.split(":")[1]
                if unprefixed == other.lower():
                    possible.append(k)
            if len(possible) > 1:
                pass
                #print "# Ambiguous match",oldName,possible
            elif len(possible) == 1:
                newName = possible[0]

                newID = after[newName]
                mapping[oldID] = (newID, oldName, newName, "anyspace")
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
