#!/usr/bin/python

# python match-ids.py IDMap_dump-AA152-28-1-2019\ at\ 17.38.21.625.txt 1710-dumps /Applications/MultiMC.app/Contents/MacOS/instances/1.5.2AA\ \(Migrated\)1/minecraft/config/ /Applications/MultiMC.app/Contents/MacOS/instances/1.7.10s/minecraft/config

import sys
import os
import re
import types

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

# Try replacing the old name with these prefixes to obtain new name
replacePrefixes = {
    "tile.bop.": "BiomesOPlenty:", "item.bop.": "BiomesOPlenty:",
    "tile.extrabiomes.": "ExtrabiomesXL:",
    "tile.immibis/redlogic:": "RedLogic:redlogic.",
    "item.AppEng.": "appliedenergistics2:item.", "tile.AppEng.": "appliedenergistics2:tile.",
    "tile.railcraft.": "Railcraft:", "item.railcraft.": "Railcraft:",
    "tile.myst.": "Mystcraft:",
    "item.myst.": "Mystcraft:",
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
    "tile.for.": "Forestry:",
}

# Normally, the old:new is 1:1 mapping, but allow n:1 (multiple blocks mapping to same block) _to_ this
# if is included in this list, e.g., lossy conversion since cannot be reversed. Useful for removed mods.
overloaded_allow_multiple_substitutions = [
    "ForgottenNature:FNWStairs1",
    "ExtrabiomesXL:log1",
    "ExtrabiomesXL:leaves_1",
    "ExtrabiomesXL:leaves_2",
    "ExtrabiomesXL:saplings_1",
    "chisel:holystone",
    "BuildCraft|Energy:blockOil",
    "ExtrabiomesXL:log_elbow_baldcypress",
    "ExtrabiomesXL:cornerlog_rainboweucalyptus",
    "ExtrabiomesXL:woodslab",
    "ExtraUtilities:etherealglass",
    "ForgottenNature:falseBlock",
    "MineFactoryReloaded:stone",
    "Forestry:logs",
    "MineFactoryReloaded:stainedglass.pane",
    "thaumicenergistics:thaumicenergistics.block.infusion.provider",
    "Thaumcraft:blockCosmeticSolid",
    "ThaumicTinkerer:nitorGas",
    "cfm:couch",
    "ExtraUtilities:chandelier",
    "OpenBlocks:trophy",
    "cfm:freezer",
    "OpenBlocks:paintcan",
    "ExtrabiomesXL:terrain_blocks1",
    "ExtrabiomesXL:slabRedRock",
    "GalacticraftCore:tile.landingPad",
    "Railcraft:part.circuit",
    "UsefulFood:RawMarshmallow",
    "MoCreatures:furchest",
    "minecraft:leather",
    "atum:item.bow",
    "MoCreatures:katana",
    "ExtraTiC:shuriken",
]

# Normally vanilla content is completely ignored, but sometimes having these
# items available for substitutions is useful; if so add them here
force_available_substitutions = {
    "minecraft:air": 0,
    "minecraft:leather": 334,
    "minecraft:iron_horse_armor": 417,
}

# Manually assigned old name to new name replacements
manual = {
    "tile.IronChest": "IronChest:BlockIronChest",
    "tile.CompactSolar": "CompactSolars:CompactSolarBlock",

    "tile.bau5ProjectBench": "projectbench:pb_block",

    "AppEng.Items.*": "appliedenergistics2:item.ItemBasicStorageCell.64k",
    "AppEng.Items.*_": "appliedenergistics2:item.ItemMultiPart",
    "item.AppEng.Tools.QuartzCuttingKnife": "appliedenergistics2:item.ToolCertusQuartzCuttingKnife",

    "item.enderStaff": "xreliquary:ender_staff",
    "item.sacredEye": "xreliquary:salamander_eye",
    "item.artifact": "factorization:brokenArtifact",

    # Mo' Creatures
    "item.moc_egg": "MoCreatures:mocegg",
    "item.turtlemeat": "MoCreatures:turtleraw",
    "item.key": "MoCreatures:key",
    "item.furplate": "MoCreatures:furchest",
    "item.stingdirt": "MoCreatures:scorpstingdirt",
    "item.harness": "MoCreatures:elephantharness",
    "item.chestset": "MoCreatures:furchest",
    "item.swordsilver": "MoCreatures:silversword",
    "item.armormetal": "minecraft:iron_horse_armor",

    # ChessCraft
    "item.Piece Mover": "JABBA:mover",

    # Dartcraft substitutions
    "item.gemForce": "thebetweenlands:aquaMiddleGemOre",
    "item.ingotForce": "HardcoreEnderExpansion:endium_ingot",
    "item.forceShard": "Automagy:shardSliver",
    "item.forceRod": "ProjectE:item.pe_divining_rod_1",
    "item.forceStick": "thebetweenlands:crabstick",
    "item.forceAxe": "thebetweenlands:swiftPickaxe",
    "item.forceShears": "WitchingGadgets:item.WG_ThaumiumShears",
    "item.forceBucket": "thebetweenlands:weedwoodBucketStagnantWater",
    "item.forceWrench": "PneumaticCraft:pneumaticWrench",
    "item.forceMitts": "miscutils:TungstenCarbideMultipick",
    "item.lootBag": "Thaumcraft:ItemLootBag",
    "item.itemTear": "TwilightForest:item.fieryTears",
    "item.itemClaw": "xreliquary:infernal_claws",
    "item.tileBox": "IC2:itemToolbox",

    "item.railcraft.liquid.creosote.bottle": "Railcraft:fluid.creosote.bottle",
    "item.railcraft.part.gear": "Railcraft:part.circuit",
    "item.railcraft.cart.loco.steam": "Railcraft:cart.loco.steam.solid",
    
    "item.rawLambchop": "UsefulFood:RawMutton",
    "item.cookedLambchop": "UsefulFood:CookedMutton",

    "tile.fyriteOre": "netherrocks:fyrite_ore", "tile.fyriteBlock": "netherrocks:fyrite_block",
    "tile.malachiteOre": "netherrocks:malachite_ore", "tile.malachiteBlock": "netherrocks:malachite_block",
    "tile.ashstoneOre": "netherrocks:ashstone_ore", "tile.ashstoneBlock": "netherrocks:ashstone_block",
    "tile.illumeniteOre": "netherrocks:illumenite_ore", "tile.illumeniteBlock": "netherrocks:illumenite_block",
    "tile.dragonstoneOre": "netherrocks:dragonstone_ore", "tile.dragonstoneBlock": "netherrocks:dragonstone_block",
    "tile.argoniteOre": "netherrocks:argonite_ore", "tile.argoniteBlock": "netherrocks:argonite_block",
    "tile.netherFurnaceOn": "netherrocks:nether_furnace",
    "item.malachitePick": "netherrocks:malachite_pickaxe",
    "item.malachiteSword": "netherrocks:malachite_sword",
    "item.ashstonePick": "netherrocks:ashstone_pickaxe",
    "item.ashstoneAxe": "netherrocks:ashstone_axe",
    "item.dragonstonePick": "netherrocks:dragonstone_pickaxe",
    "item.dragonstoneAxe": "netherrocks:dragonstone_axe",
    "item.dragonstoneSword": "netherrocks:dragonstone_sword",
    "item.argonitePick": "netherrocks:argonite_pickaxe",
    "item.argoniteShovel": "netherrocks:argonite_shovel",
    "item.malachiteChest": "netherrocks:malachite_chestplate",
    "item.illumeniteBoots": "netherrocks:malachite_boots",
    "item.fyriteIngot": "netherrocks:fyrite_ingot",
    "item.malachiteIngot": "netherrocks:malachite_ingot",
    "item.ashstoneGem": "netherrocks:ashstone_gem",
    "item.illumeniteIngot": "netherrocks:illumenite_ingot",
    "item.dragonstoneGem": "netherrocks:dragonstone_gem",
    "item.argoniteIngot": "netherrocks:argonite_ingot",

    "tile.thermalexpansion.ore": "ThermalFoundation:Ore",
    "tile.thermalexpansion.engine": "ThermalExpansion:Device",
    "tile.thermalexpansion.energycell": "ThermalExpansion:Cell",
    "tile.thermalexpansion.conduit": "ThermalDynamics:ThermalDynamics_0",
    "tile.thermalexpansion.lamp": "ThermalExpansion:Light",

    "tile.liquid.redstone": "ThermalFoundation:FluidRedstone",
    "tile.liquid.glowstone": "ThermalFoundation:FluidGlowstone",
    "tile.liquid.ender": "ThermalFoundation:FluidEnder",

    "tile.thermalexpansion.storage": "ThermalExpansion:Strongbox",

    "tile.BlockLimbo": "dimdoors:Unraveled Fabric",
    "tile.blockDimWallPerm": "dimdoors:Fabric of RealityPerm",
    "tile.dimDoor": "dimdoors:Dimensional Door",
    "tile.dimHatch": "dimdoors:Transdimensional Trapdoor",
    "tile.blockDimWall": "dimdoors:Fabric of Reality",
    "tile.chaosDoor": "dimdoors:Unstable Door",
    "tile.dimDoorWarp": "dimdoors:Warp Door",

    # Modular Forcefields System
    "tile.MFFSControlSystem": "factorization:ArtifactForge",
    "tile.MFFSForceEnergyConverter": "GalaxySpace:convertersurface",
    "tile.MFFSMonazitOre": "ihl:oreDatolite",
    "tile.MFFSCapacitor": "OpenComputers:capacitor",
    "tile.MFFSSecurityStation": "PneumaticCraft:securityStation",
    "item.itemCardEmpty": "enhancedportals:location_card",
    "item.itemCardPowerLink": "enhancedportals:portal_module",

    "tile.easycraftingtable": "thebetweenlands:weedwoodCraftingTable",

    "tile.mod_SRM.SecretPlayerPlate": "ForgottenNature:falseBlock",
    "item.mod_SRM.SecretIronDoorItem": "ForgottenNature:falseBlock",
    "item.mod_SRM.CamoflaugePaste": "ForgottenNature:falseBlock",
    "tile.mod_SRM.GhostBlock": "ForgottenNature:falseBlock",
    "tile.mod_SRM.SecretButton": "ForgottenNature:falseBlock",
    "tile.mod_SRM.SecretIronDoorBlock": "ExtraUtilities:etherealglass",
    "tile.mod_SRM.SecretRedstone": "ForgottenNature:falseBlock",
    "tile.mod_SRM.SecretTrapDoor": "ExtraUtilities:etherealglass",
    "tile.mod_SRM.OneWayGlass": "ExtraUtilities:etherealglass",
    "tile.mod_SRM.TorchLever": "ForgottenNature:falseBlock",
    "item.mod_SRM.SecretWoodenDoorItem": "ExtraUtilities:etherealglass",

    "tile.PortalMod": "PortalGun:Portal_BlockPortal",

    "tile.cccomputer": "OpenComputers:case1", # ComputerCraft substitute with OpenComputers
    "tile.ccturtle": "OpenComputers:robot",

    "tile.myst.writing_desk": "Mystcraft:WritingDesk",
    "tile.myst.inkmixer": "Mystcraft:BlockInkMixer",
    "tile.myst.bookbinder": "Mystcraft:BlockBookBinder",
    "item.myst.agebook": "Mystcraft:agebook",
    "item.myst.linkbook": "Mystcraft:linkbook",
    "item.myst.page": "Mystcraft:page",
    "item.myst.vial": "Mystcraft:vial",

    "tile.enderIO:blockCustomFence": "thebetweenlands:weedwoodPlankFence",
    "item.enderIO:itemRedstoneConduit": "EnderIO:itemRedstoneConduit",

    "tile.oilMoving": "BuildCraft|Energy:blockOil",
    "tile.builderBlock": "BuildCraft|Builders:builderBlock",
    "tile.oilStill": "BuildCraft|Energy:blockOil",
    "tile.tankBlock": "BuildCraft|Factory:tankBlock",

    "item.woodenGearItem": "flansmod:woodenPropeller",
    "item.stoneGearItem": "TravellersGear:simpleGear",
    "item.ironGearItem": "miscutils:itemGearSelenium",
    "item.goldGearItem": "miscutils:itemGearZirconium",
    "item.diamondGearItem": "miscutils:itemGearRuthenium",
    "item.PipeItemsWood": "BuildCraft|Transport:item.buildcraftPipe.pipeitemswood",
    "item.PipeItemsCobblestone": "BuildCraft|Transport:item.buildcraftPipe.pipeitemscobblestone",
    "item.PipeItemsStone": "BuildCraft|Transport:item.buildcraftPipe.pipeitemsstone",
    "item.PipeItemsIron": "BuildCraft|Transport:item.buildcraftPipe.pipeitemsiron",
    "item.PipeItemsGold": "BuildCraft|Transport:item.buildcraftPipe.pipeitemsgold",
    "item.PipeItemsDiamond": "BuildCraft|Transport:item.buildcraftPipe.pipeitemsdiamond",
    "item.PipeItemsObsidian": "BuildCraft|Transport:item.buildcraftPipe.pipeitemsobsidian",
    "item.PipeLiquidsWood": "BuildCraft|Transport:item.buildcraftPipe.pipefluidswood",
    "item.PipeLiquidsCobblestone": "BuildCraft|Transport:item.buildcraftPipe.pipefluidscobblestone",
    "item.PipeLiquidsStone": "BuildCraft|Transport:item.buildcraftPipe.pipefluidsstone",
    "item.PipeLiquidsIron": "BuildCraft|Transport:item.buildcraftPipe.pipefluidsiron",
    "item.PipeLiquidsGold": "BuildCraft|Transport:item.buildcraftPipe.pipefluidsgold",
    "item.PipePowerWood": "BuildCraft|Transport:item.buildcraftPipe.pipepowerwood",
    "item.PipePowerStone": "BuildCraft|Transport:item.buildcraftPipe.pipepowerstone",
    "item.PipePowerGold": "BuildCraft|Transport:item.buildcraftPipe.pipepowergold",

    "tile.extrabiomes.cattail": "ExtrabiomesXL:plants4",
    "tile.extrabiomes.log": "ExtrabiomesXL:log1",
    "tile.extrabiomes.log_": "ExtrabiomesXL:log2",
    "tile.extrabiomes.woodslab": "ExtrabiomesXL:woodslab",
    "tile.extrabiomes.woodslab_": "ExtrabiomesXL:woodslab2",
    "tile.extrabiomes.woodslab__": "ExtrabiomesXL:woodslab",
    "tile.extrabiomes.woodslab___": "ExtrabiomesXL:woodslab",
    "tile.extrabiomes.leafpile": "ExtrabiomesXL:leaf_pile",
    "tile.extrabiomes.redrock": "ExtrabiomesXL:terrain_blocks1",
    "tile.extrabiomes.crackedsand": "ExtrabiomesXL:terrain_blocks2",
    "tile.extrabiomes.redrockslab": "ExtrabiomesXL:slabRedRock",
    "tile.extrabiomes.redrockslab_": "ExtrabiomesXL:slabRedRock",
    "tile.extrabiomes.flower": "ExtrabiomesXL:leaves_3",
    "tile.extrabiomes.tallgrass": "ExtrabiomesXL:leaves_2",
    "tile.extrabiomes.leaves": "ExtrabiomesXL:leaves_1",
    "tile.extrabiomes.leaves_": "ExtrabiomesXL:leaves_4",
    "tile.extrabiomes.leaves__": "ExtrabiomesXL:leaves_1",
    "tile.extrabiomes.leaves___": "ExtrabiomesXL:leaves_2",
    "tile.extrabiomes.log.quarter": "ExtrabiomesXL:cornerlog_baldcypress",
    "tile.extrabiomes.log.quarter_": "ExtrabiomesXL:cornerlog_rainboweucalyptus",
    "tile.extrabiomes.log.quarter__": "ExtrabiomesXL:cornerlog_oak",
    "tile.extrabiomes.log.quarter___": "ExtrabiomesXL:cornerlog_fir",
    "tile.extrabiomes.stairs.redcobble": "ExtrabiomesXL:terrain_blocks1",
    "tile.extrabiomes.stairs.redrockbrick": "ExtrabiomesXL:terrain_blocks1",
    "tile.extrabiomes.redrockslab": "ExtrabiomesXL:slabRedRock",
    "tile.extrabiomes.sapling": "ExtrabiomesXL:saplings_1",
    "tile.extrabiomes.sapling_": "ExtrabiomesXL:saplings_2",
    "tile.extrabiomes.baldcypressquarter": "ExtrabiomesXL:log_elbow_baldcypress",
    "tile.extrabiomes.cypresskneelog": "ExtrabiomesXL:log_elbow_baldcypress",
    "tile.extrabiomes.rainbowkneelog": "ExtrabiomesXL:log_elbow_rainbow_eucalyptus",
    "tile.extrabiomes.rainboweucalyptusquarter": "ExtrabiomesXL:cornerlog_rainboweucalyptus",
    "tile.extrabiomes.newlog": "ExtrabiomesXL:log1",
    "tile.extrabiomes.woodslab_": "ExtrabiomesXL:woodslab2",

    "tile.bop.holyStone": "chisel:holystone",
    "tile.bop.generic.holy_dirt": "GalaxySpace:barnardaCdirt",
    "tile.bop.generic.ash_stone": "BiomesOPlenty:ashStone",
    "tile.bop.generic.crag_rock": "BiomesOPlenty:cragRock",
    "tile.bop.generic.dried_dirt": "BiomesOPlenty:driedDirt",
    "tile.bop.generic.hard_dirt": "BiomesOPlenty:hardDirt",
    "tile.bop.generic.hard_ice": "BiomesOPlenty:hardIce",
    "tile.bop.generic.hard_sand": "BiomesOPlenty:hardSand",
    "tile.bop.holyGrass": "chisel:holystone",
    "tile.bop.redRocks": "BiomesOPlenty:rocks",
    "tile.bop.leavesFruit": "BiomesOPlenty:leaves3",
    "tile.bop.wood1": "BiomesOPlenty:logs1",
    "tile.bop.wood2": "BiomesOPlenty:logs2",
    "tile.bop.wood3": "BiomesOPlenty:logs3",
    "tile.bop.wood4": "BiomesOPlenty:logs4",
    #"tile.bop.redCobbleStairs": "ExtrabiomesXL:stairsRedCobble",
    #"tile.bop.redBricksStairs": "Red Brick Stairs ID",
    "tile.bop.leavesColorized": "BiomesOPlenty:leaves4",
    "tile.bop.puddle": "thebetweenlands:puddle",
    "tile.bop.glass": "ExtraUtilities:etherealglass",
    "tile.bop.altar": "Botania:altar",
    "tile.bop.springWater": "IC2:fluidDistilledWater",
    "tile.bop.liquidPoison": "ihl:fluidBlueVitriolDissolvedInWater",
    "tile.bop.amethystOre": "ihl:orePotassiumFeldspar",
    "tile.bop.cloud": "chisel:cloud",
    "tile.bop.generic.mud_brick": "thebetweenlands:mud",
    "tile.bop.promisedPortal": "thebetweenlands:portalBark",
    "tile.bop.generic.crystal": "GalaxySpace:enceladuscrystal",
   
    "tile.blockSurreal": "ihl:oreGypsum", # Legendary Beasts

    "tile.crudeOilMoving": "BuildCraft|Energy:blockOil",
    "tile.crudeOilStill": "BuildCraft|Energy:blockOil",

    "tile.netherores.ore.0": "ProjRed|Exploration:projectred.exploration.ore",
    "tile.netherores.ore.1": "miscutils:blockStoneoreFluorite",
    "tile.netherores.hellfish": "miscutils:blockHellFire",

    "tile.tconstruct.gravelore": "TConstruct:GravelOre",
    "tile.tconstruct.stoneore": "ihl:oreTrona",
    "tile.TConstruct.Soil": "TConstruct:CraftedSoil",
    "tile.tconstruct.metalblock": "TConstruct:MetalBlock",
    "tile.ToolStation": "TConstruct:ToolStationBlock",
    "tile.liquid.metalFlow": "TConstruct:fluid.molten.iron",
    "tile.liquid.metalStill": "TConstruct:fluid.molten.gold",
    "tile.Decoration.Brick": "TConstruct:MeatBlock",
    "tile.tconstruct.glasspanestained": "MineFactoryReloaded:stainedglass.pane",

    "tile.Redstone.Machine": "OpenBlocks:drawingtable", # Tinker's Construct drawbridge/igniter

    "tile.BiblioArmorStand": "BiblioCraft:Armor Stand",
    "tile.BiblioPress": "BiblioCraft:Printing Press",
    "tile.BiblioType": "BiblioCraft:Typesetting Machine",

    #"tile.for.slabs3": "Forestry:slabs",
    #"tile.for.planks2": "Forestry:planks",
    #tile.null. ID: 924
    "tile.leaves": "Forestry:leaves",
    "tile.for.log1": "Forestry:logs",
    "tile.for.log2": "Forestry:logsFireproof",
    "tile.for.log3": "Forestry:logs",
    "tile.for.log4": "Forestry:logs",
    "tile.for.planks": "Forestry:planks",
    "tile.for.slabs1": "Forestry:slabs",
    "tile.for.slabs2": "Forestry:slabsDouble",
    #"tile.stained": 
    "tile.ffarm": "Forestry:ffarm",
    "tile.apiaristMachine": "gendustry:IndustrialApiary",
    "item.hiveFrame__": "Forestry:frameProven",
   
    # Dartcraft substitutions
    "tile.hive_": "ihl:oreBischofite",
    "tile.powerOre": "ihl:oreMica",
    "tile.forceStairs": "ForgottenNature:FNWStairs1",
    "tile.forceLog": "ExtrabiomesXL:log1",
    "tile.forceLeaves": "ExtrabiomesXL:leaves_1",
    "tile.forceSapling": "ExtrabiomesXL:saplings_1",

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
    "tile.Half block_": "ForgottenNature:FNdHalfStone",
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
    "tile.immibis.microblock.container": "ImmibisMicroblocks:MicroblockContainer",

    "tile.BlockMetaID_Block": "gregtech:gt.blockcasings4", # loose match, different meta (Advanced Machine Block :0 -> ?, Fusion Coil :1 -> :7)
    "tile.GT_LightSource": "gregtech:gt.blockcasings5", # not really
    "tile.BlockMetaID_Machine": "gregtech:gt.blockmachines",
    "tile.BlockMetaID_Ore": "gregtech:gt.blockores",
    "tile.BlockMetaID_Block2": "gregtech:gt.blockmetal1", # different metals

    "tile.mfr.liquid.chocolatemilk.still": "MineFactoryReloaded:chocolatemilk.still",
    "tile.mfr.decorativestone": "MineFactoryReloaded:stone",
    "tile.mfr.decorativebrick": "MineFactoryReloaded:stone",
    "tile.mfr.liquid.essence.still": "MineFactoryReloaded:mobessence.still",

    # Jammy Furniture Mod -> Crayfish Furniture Mod
    "tile.bathBlock": "cfm:freezer",
    "tile.ceramicBlockOne": "cfm:fridge",
    "tile.ironBlockOne": "cfm:coffetablestone",
    "tile.ironBlocksTwo": "cfm:tablestone",
    "tile.lightsOff": "cfm:lampoff",
    "tile.lightsOn": "cfm:lampon",
    "tile.miscOne": "ihl:goldChimneyKnee",
    "tile.MobHeadsOne": "Botania:gaiaHeadBlock",
    "tile.MobHeadsTwo": "cfm:showerheadoff",
    "tile.MobHeadsThree": "HardcoreEnderExpansion:enderman_head_block",
    "tile.MobHeadsFour": "cfm:showerheadon",
    "tile.roofingBlocksOne": "erebus:siloRoof",
    "tile.sofaCenter": "cfm:couch",
    "tile.sofaCorner": "cfm:couch",
    "tile.sofaLeft": "cfm:couch",
    "tile.sofaRight": "cfm:couch",
    "tile.woodBlocks": "cfm:coffetablewood",
    "tile.woodBlocksThree": "cfm:tablewood",
    "tile.woodBlocksTwo": "cfm:chairwood",
    "item.itemLightBulb": "cfm:ceilinglighton",
    "item.mantlePieceUnf": "cfm:mailbox",
    "item.itemCeramicPanel": "cfm:printer",
    "item.itemBlindPart": "cfm:blindon",


    "tile.machineBlock": "BuildCraft|Builders:machineBlock",

    "tile.blockThermalMonitor": "IC2NuclearControl:blockNuclearControlMain",

    "tile.chargePad": "IC2:blockChargepad",

    "tile.glassBell": "ihl:glassBoxBlock", # EE3 substitution
    "tile.aludel": "ihl:electrolysisBath", # EE3 substitution

    "tile.cage": "thebetweenlands:geckoCage", # SoulShards substitution

    "tile.extrautils:chandelier_invis": "ExtraUtilities:chandelier",

    "tile.openblocks.trophy": "OpenBlocks:trophy",

    # Thaumcraft
    "tile.blockCrucible": "Thaumcraft:blockMetalDevice",
    "tile.blockInfusionWorkbench": "thaumicenergistics:thaumicenergistics.block.infusion.provider",
    "tile.blockWooden": "Thaumcraft:blockCosmeticSolid",
    "tile.blockNitor": "ThaumicTinkerer:nitorGas",

    # Camping Mod substitutions
    "tile.campfire": "erebus:fireBloom",
    "tile.tent": "cfm:freezer",
    "tile.ghostBlock": "ForgottenNature:falseBlock",
    "tile.radishCrop": "thebetweenlands:fungusCrop",

    "tile.markShip": "ArchimedesShips:marker",
    "tile.archiFloater": "ArchimedesShips:floater",
    "tile.archiBalloon": "ArchimedesShips:balloon",
    "tile.archiGauge": "ArchimedesShips:gauge",
    
    "tile.Atum:AtumCoal": "atum:tile.coalOre",
    "tile.Atum:AtumCobble": "atum:tile.cobble",
    "tile.Atum:AtumCrystalGlass": "atum:tile.crystalGlass",
    "tile.Atum:FlaxBlock": "atum:tile.flax",
    "tile.Atum:AtumIron": "atum:tile.ironOre",
    "tile.AtumPharaohChest": "atum:tile.pharaohChest",
    "tile.Atum:AtumBrickSmall": "atum:tile.smallBrick",
    "tile.Atum:SmallStoneStair": "atum:tile.smallStairs",
    "tile.Atum:AtumSand": "atum:tile.sand",
    "tile.Atum:AtumSlab": "atum:tile.slab",
    "tile.Atum:AtumStoneWall": "atum:tile.walls",

    "tile.decorationblock": "GalacticraftCore:tile.landingPad",
    "item.oxygenTankLightFull": "GalacticraftCore:item.oxygenTankLightFull",
    "item.oxygenTankHeavyFull": "GalacticraftCore:item.oxygenTankHeavyFull",
    "item.airVent": "GalacticraftCore:item.airVent",
    "item.oxygenConcentrator": "GalacticraftCore:item.oxygenConcentrator",
    "item.airFan": "GalacticraftCore:item.airFan",
    "item.parachute": "GalacticraftCore:item.parachute",
    "item.oilExtractor": "GalacticraftCore:item.oilExtractor",
    "item.oilCanisterPartial": "GalacticraftCore:item.oilCanisterPartial",
    "item.steel_pickaxe": "GalacticraftCore:item.steel_pickaxe",

    # UsefulFood
    "item.marshmallowFood": "UsefulFood:RawMarshmallow",

    # ExtraUtilities
    "item.extrautils:defoliageAxe": "ExtraUtilities:defoliageAxe",
    "item.extrautils:divisionSigil": "ExtraUtilities:divisionSigil",

    # RanCraft Penguins
    "item.PSLBLU": "minecraft:leather", # light blue penguin skin
    "item.PSBLK": "minecraft:leather",
    "item.PSBLU": "minecraft:leather",
    "item.PSKR": "minecraft:leather",
    "item.PSBR": "minecraft:leather",
    "item.PB": "atum:item.bow", # penguin bow
    "item.PKD": "MoCreatures:katana", # penguin katana
    "item.PS": "ExtraTiC:shuriken", # penguin shuriken

    # Balkon's WeaponMod
    "item.bullet": "weaponmod:bullet",
    "item.crossbow": "weaponmod:crossbow",
    "item.dart": "weaponmod:dart",
    "item.firerod": "weaponmod:firerod",
    "item.cannon": "weaponmod:cannon",
}

# Direct ID mappings where the name is inadequate so the numeric identifier has to be used,
# sometimes the name is useless like "tile.null", or ambiguous
# old id: (new name or id, better informative old name note)
direct = {
    501: ("OpenComputers:assembler", "BuildCraft assemblyTable.id"),

    645: ("AdvancedMachines:advancedmachines.block", "Immibis AdvancedMachines"),

    683: ("minecraft:air", "ModularForceFieldSystem MFFSFieldblock"),

    743: ("RedLogic:redlogic.wire", "redlogic.wire.id"),
    749: ("RedLogic:redlogic.gates", "redlogic.gates.id"),

    #1144: (, "Immibis peripherals.lan-wire.id"),
    #1145: (, "Immibis peripherals.block.id"),
    1146: ("InfiniTubes:infinitubes.machine", "Immibis infinitubes.machine.id"),
    1148: ("LiquidXP:liquidxp.machine", "Immibis liquidxp.machine.id"),
    
    1150: ("Tubestuff:machine", "Immibis tubestuff.id"),
    1151: ("Tubestuff:storage", "Immibis tubestuff.storage.id"),

    1555: ("ObsidiPlates:ObsidianPressurePlate", "ObsidiPlates obsidianPlate"),

    2510: ("appliedenergistics2:tile.BlockCableBus", "AppliedEnergistics appeng.blockMulti/ME Cable"),
    2511: ("appliedenergistics2:tile.BlockIOPort", "AppliedEnergistics appeng.blockMulti2/ME Precision Export Bus/~tile.BlockIOPort"),
    2512: ("appliedenergistics2:tile.OreQuartz", "AppliedEnergistics appeng.blockWorld"),
    2513: ("appliedenergistics2:tile.BlockSpatialIOPort", "AppliedEnergistics appeng.blockMulti3/ME Fuzzy Export Bus"),
    2514: ("appliedenergistics2:tile.BlockTinyTNT", "AppliedEnergistics appeng.TinyTNT/tile.BlockTinyTNT"),

    514: ("BuildCraft|Transport:pipeBlock", "BuildCraft pipe.id/BuildCraft|Transport:pipeBlock"),

    2375: ("UsefulFood:AppleCakeBlock", "UsefulFood:AppleCakeBlock"),
    2376: ("UsefulFood:CaramelCakeBlock", "UsefulFood:CaramelCakeBlock"),
    2377: ("UsefulFood:ChocolateCakeBlock", "UsefulFood:ChocolateCakeBlock"),
    2378: ("UsefulFood:MagicCakeBlock", "UsefulFood:MagicCakeBlock"),

    ## Forgotten Nature

    # ambiguous with vanilla
    2573: ("ForgottenNature:nGlass", "tile.glass"), 
    2606: ("ForgottenNature:nFence", "tile.fence"),

    # tile.null
    2608: ("ForgottenNature:oneWayCamo", "Forgotten Nature groundID/oneWayCamo?"),

    2609: ("ForgottenNature:FNLeaves1", "Forgotten Nature leafIDIndex+0/red maple"),
    2610: ("ForgottenNature:FNLeaves2", "Forgotten Nature leafIDIndex+1/sequoia"),
    2611: ("ForgottenNature:FNLeaves3", "Forgotten Nature leafIDIndex+2/swamp willow"),
    2612: ("ForgottenNature:FNLeaves4", "Forgotten Nature leafIDIndex+3/beech"),
    2613: ("ForgottenNature:FNLeaves5", "Forgotten Nature leafIDIndex+4/lemon"),
    2614: ("ForgottenNature:FNLeaves6", "Forgotten Nature leafIDIndex+5/huckleberry"),
    
    2615: ("ForgottenNature:crystalLeaves", "Forgotten Nature leafIDIndex+6/crystal"),
    2616: ("ForgottenNature:netherLeaves", "Forgotten Nature leafIDIndex+7/nether ash"),

    2620: ("ForgottenNature:FNLogs1", "Forgotten Nature logIDindex+0/cherry log"),
    2621: ("ForgottenNature:FNLogs2", "Forgotten Nature logIDindex+1/desert willow"),
    2622: ("ForgottenNature:FNLogs3", "Forgotten Nature logIDindex+2/bukkit log"),
    2623: ("ForgottenNature:FNLogs4", "Forgotten Nature logIDindex+3/cherry log*"),
    2624: ("ForgottenNature:netherFNLogs", "Forgotten Nature logIDindex+4/nether ash log*"),

    2630: ("ForgottenNature:FNPlanks1", "Forgotten Nature plankID/ForgottenNature:FNPlanks1/brown plank"),
    2631: ("ForgottenNature:FNPlanks2", "Forgotten Nature plankID2/ForgottenNature:FNPlanks2/herringbone"),

    2633: ("ForgottenNature:FNSapling1", "Forgotten Nature sapIDindex+0/desert ironwood sapling"),
    2634: ("ForgottenNature:FNSapling2", "Forgotten Nature sapIDindex+1/palm sapling"),
    2635: ("ForgottenNature:FNSapling3", "Forgotten Nature sapIDindex+2/huckleberry bushling"),

    2640: ("ForgottenNature:Crystal Torch", "Forgotten Nature torchID"),

    3660: ("atum:tile.portal", "Atum Portal Block"),

    3709: ("ExtrabiomesXL:fencegate_acacia", "Forestry ExtraTrees gate Fir Gate"),
    3710: ("malisisdoors:door_acacia", "Forestry ExtraTrees door Fir Door"),
    13256: ("Forestry:adventurerBag", "Forestry Adventurer's Backpack"),

    4091: ("MineFactoryReloaded:laserair", "MineFactoryReloaded ID.FakeLaser"),
    4093: ("flansmod:gunBox.american", "Flan's Mod Weapons Box"),
}

force_direct = {
    # Legacy substitutions
    # Missing blocks not in 1.5.2 but they were in 1.2.5 (or 1.5.1), and they
    # were leftover by 1.7.10, so would be empty if loaded. Fix it here.
    182: (1915, "1.2.5/RedPower2 tile.rpframe/GalacticraftCore:tile.airLockFrame"),
    208: (2510, "1.2.5/Railcraft tile.mill/ihl:wireMill"),
    213: (3289, "1.2.5/Plugins for Forestry tile.Thatch/thebetweenlands:thatch"),
    244: (3959, "1.2.5/BuildCraft tile.blockMiningTip/miscutils:blockMiningExplosives"),
    390: (140, "1.2.5/tile.plantpot/minecraft:flower_pot"),
    750: (2492, "1.2.5/RedPower2 appliance.id eloraam.base.BlockAppliance (alloy furnace, blulectric)/ihl:vacuumInductionMeltingFurnace"),
    751: (2773, "1.2.5/tile.freezer/cfm.freezer"),
    765: (2502, "1.2.5/RedPower2 eloraam.machine.BlockMachinePanel/ihl:gaedesMercuryRotaryPump"),
    930: (1271, "1.5.1/Forestry tile.firsapling/ExtrabiomesXL:saplings_1"),
    931: (2503, "1.5.1/Forestry tile.harvester/ihl:labElectrolyzer"),
    942: (2521, "1.5.1/Forestry tile.planter/ihl:leadOven,2521"),
    943: (2524, "1.5.1/Forestry forestry.cultivation.BlockSaplings/ihl:achesonFurnance"),
    1086: (3822, "1.5.1/SecretRoomsMod tile.Secret Wooden Door/ForgottenNature:falseBlock"),
    1401: (1290, "1.2.5/Kaevator SuperSlopes tile.BlockKaevWoodCorners/ExtrabiomesXL:woodslab"),
    1432: (1290, "1.2.5/Kaevator SuperSlopes tile.BlockKaevWoodIntCorners/ExtrabiomesXL:woodslab"),
    1433: (1290, "1.2.5/Kaevator SuperSlopes tile.BlockKaevCobblestoneIntCorners"),
    1437: (1290, "1.2.5/Kaevator SuperSlopes tile.BlockKaevStoneIntCorners"),
    1478: (1290, "1.2.5/Kaevator SuperSlopes tile.BlockKaevWhiteWoolSlopes"),
    2000: (3514, "1.2.5/1.5.1/RedPower2 Copper Ore/erebus:oreCopper"),

    # RedPower2 from 1.2.5, substitutions
    # TODO: add NBT tag for custom name, historical item?
    1256: (7765, "1.2.5/RedPower2 eloraam.core.ItemParts/ProjRed|Core:projectred.core.part"),
    1258: (3832, "1.2.5/RedPower2 eloraam.core.ItemParts__/framez:motorcore"),
    1262: (7767, "1.2.5/RedPower2 item.screwdriver/ProjRed|Core:projectred.core.screwdriver"),
    1263: (5905, "1.2.5/RedPower2 eloraam.core.ItemParts___/RedLogic:redlogic.chip"),
    1290: (507, "1.2.5/RedPower2 eloraam.world.ItemCustomSeeds/flax/atum:tile.flax"),
    1293: (2873, "1.2.5/RedPower2 item.paintcan.orange/OpenBlocks:paintcan"),
    1296: (2873, "1.2.5/RedPower2 item.paintcan.yellow/OpenBlocks:paintcan"),
    1297: (2873, "1.2.5/RedPower2 item.paintcan.lime/OpenBlocks:paintcan"),
    1299: (2873, "1.2.5/RedPower2 item.paintcan.gray/OpenBlocks:paintcan"),
    1323: (2873, "1.2.5/RedPower2 item.paintbrush.red/OpenBlocks:paintcan"),
    1325: (6327, "1.2.5/RedPower2 item.voltmeter/factorization:tool/charge_meter"),
    1326: (6653, "1.2.5/RedPower2 item.btbattery/ihl:item.battery"),
    1327: (7031, "1.2.5/RedPower2 item.sonicDriver/OpenBlocks:sonicglasses"),
    1329: (9218, "1.2.5/RedPower2 item.athame/ProjRed|Exploration:projectred.exploration.athame"),
    1331: (7766, "1.2.5/RedPower2 item.drawplateDiamond/ProjRed|Core:projectred.core.drawplate"),
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
            if newName not in overloaded_allow_multiple_substitutions:
                del after[newName]
            continue

        if direct.has_key(oldID):
            newNameNotes = direct[oldID][1]
            newIDorName = direct[oldID][0]
            if type(newIDorName) == types.IntType:
                newID = newIDorName
            else:
                newID = after[newIDorName]
                oldName += "/" + newNameNotes
                newNameNotes = newIDorName
                if newName not in overloaded_allow_multiple_substitutions:
                    del after[newIDorName]
            mapping[oldID] = (newID, oldName, newNameNotes, "direct")
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
        if newName.startswith("ThermalExpansion:"): newName = n[0] + ":" + ucfirst(n[1])

        if after.has_key(newName):
            newID = after[newName]
            mapping[oldID] = (newID, oldName, newName, "namespace")
            if newName not in overloaded_allow_multiple_substitutions:
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
                if unprefixed == other.lower() or "tile." + unprefixed == other.lower() or "item." + unprefixed == other.lower():
                    possible.append(k)
            if len(possible) > 1:
                pass
                #print "# Ambiguous match",oldName,possible
            elif len(possible) == 1:
                newName = possible[0]

                newID = after[newName]
                mapping[oldID] = (newID, oldName, newName, "anyspace")
                if newName not in overloaded_allow_multiple_substitutions:
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

    for k, v in force_available_substitutions.items():
        after[k] = v

    configsBefore = scanConfigs(sys.argv[3])
    configsAfter = scanConfigs(sys.argv[4])

    mapping = matchAll(before, after, configsBefore, configsAfter)

    for k, v in force_direct.items():
        mapping[k] = (v[0], "None", v[1], "forced")

    for k in sorted(mapping.keys()):
        v = mapping[k]
        if v[0] is not None:
            print "%s -> %s # %s " % (k, v[0], v[1:])
        else:
            print "# %s -> %s" % (k, v)
 

if __name__ == "__main__":
    main()
