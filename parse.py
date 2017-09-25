import json
from collections import OrderedDict

class UnitBonus:
    Hp = 0
    Mp = 0
    Atk = 0
    Def = 0
    Mag = 0
    Spr = 0

class KillerBonus:
    Phys = 0
    Mag = 0
    
itemTypeString = {
    1: 'dagger',
    2: 'sword',
    3: 'greatSword',
    4: 'katana',
    5: 'staff',
    6: 'rod',
    7: 'bow',
    8: 'axe',
    9: 'hammer',
    10: 'spear',
    11: 'harp',
    12: 'whip',
    13: 'throwing',
    14: 'gun',
    15: 'mace',
    16: 'fist',
    30: 'lightShield',
    31: 'heavyShield',
    40: 'hat',
    41: 'helm',
    50: 'clothes',
    51: 'lightArmor',
    52: 'heavyArmor',
    53: 'robe',
    60: 'accessory',
    }

elementString = {
    1: 'fire',
    2: 'ice',
    3: 'lightning',
    4: 'water',
    5: 'wind',
    6: 'earth',
    7: 'light',
    8: 'dark',
    }

killerString = {
    1: 'beast',
    2: 'bird',
    3: 'aquatic',
    4: 'demon',
    5: 'human',
    6: 'machine',
    7: 'dragon',
    8: 'spirit',
    9: 'bug',
    10: 'stone',
    11: 'plant',
    12: 'undead',
    }


with open('units.json') as unitsFile:
    unitsData = json.load(unitsFile)

with open('skills.json') as skillsFile:            
    skillsData = json.load(skillsFile)

with open('enhancements.json') as enhanceFile:            
    enhanceData = json.load(enhanceFile)

def parseData():
    jsonOutput = OrderedDict()

    for unitId in unitsData:
        unit = unitsData[unitId]
        if 'skills' in unit:            
            unitJson = OrderedDict()
            unitName = unit['name'].encode('utf-8')
            unitOutput = OrderedDict()                    
            unitOutput['max_rarity'] = unit['rarity_max']
            unitOutput['stats'] = getStats(unit)
            unitOutput['sex'] = unit['sex']
            unitOutput['equip'] = getEquips(unit['equip'])
            unitOutput['skills'] = getPassives(unitId, unit['skills'])
            jsonOutput[unitName] = unitOutput
                    
    try:
        with open('output.json', 'w') as outFile:
           json.dump(jsonOutput, outFile, indent=2, ensure_ascii=False)
    except UnicodeError:
        print 'error'


def getEquips(equips):
    equipString = []
    for id in equips:
        if id is not 60:
            equipName = itemTypeString[id]
            equipString.append(equipName)

    return equipString


def getStats(unit):
    unitRarityData = unit['entries']
    unitIDs = []
    for key in unitRarityData:
        unitIDs.append(key)

    unitIDs.sort()
    maxUnitData = unitRarityData[unitIDs[-1]]
    
    unitStats = OrderedDict()
    unitStatsData = maxUnitData['stats']
    maxStats = OrderedDict()
    maxStats['hp'] = unitStatsData['HP'][1]
    maxStats['mp'] = unitStatsData['MP'][1]
    maxStats['atk'] = unitStatsData['ATK'][1]
    maxStats['def'] = unitStatsData['DEF'][1]
    maxStats['mag'] = unitStatsData['MAG'][1]
    maxStats['spr'] = unitStatsData['SPR'][1]

    maxPots = OrderedDict()
    maxPots['hp'] = unitStatsData['HP'][2]
    maxPots['mp'] = unitStatsData['MP'][2]
    maxPots['atk'] = unitStatsData['ATK'][2]
    maxPots['def'] = unitStatsData['DEF'][2]
    maxPots['mag'] = unitStatsData['MAG'][2]
    maxPots['spr'] = unitStatsData['SPR'][2]

    unitStats['maxStats'] = maxStats
    unitStats['pots'] = maxPots

    return unitStats    

def getPassives(unitId, skills):
    unitBonus = UnitBonus()
    typesString = []
    masteries = []
    killerDict = {}
    enhanceDict = {}

    if unitId in enhanceData:
        for enhancementId in enhanceData[unitId]:
            oldId = enhanceData[unitId][enhancementId]['skill_id_old']
            newId = enhanceData[unitId][enhancementId]['skill_id_new']
            enhanceDict[oldId] = newId
        pass

    for item in skills:
        skillIdNum = item['id']
        while skillIdNum in enhanceDict:
            skillIdNum = enhanceDict[skillIdNum]

        skillId = str(skillIdNum)
        skillData = skillsData[skillId]
        for effect in skillData['effects_raw']:
            if (effect[1] == 3 and effect[2] == 1) and (effect[0] == 0 or effect[0] == 1):                
                effectData = effect[3]            
                unitBonus.Hp += effectData[4]
                unitBonus.Mp += effectData[5]
                unitBonus.Atk += effectData[0]
                unitBonus.Def += effectData[1]
                unitBonus.Mag += effectData[2]
                unitBonus.Spr += effectData[3]

            #dw 
            if (effect[1] == 3 and effect[2] == 14) and (effect[0] == 0 or effect[0] == 1):                
                DWTypes = effect[3]
                for dwType in DWTypes:
                    if dwType not in itemTypeString:
                        typesString.append('all')
                    else:
                        typesString.append(itemTypeString[dwType])

            #killers
            if ((effect[1] == 3 and effect[2] == 11) and (effect[0] == 0 or effect[0] == 1) or
                (effect[0] == 1 and effect[1] == 1 and effect[2] == 11)):
                killerEffect = effect[3]
                #remove this if block when implementing magic damage killer
                if not killerEffect[1]:
                    continue
                killerType = killerEffect[0]
                if killerType in killerDict:
                    killerData = killerDict[killerType]
                else:
                    killerData = KillerBonus()

                killerData.Phys += killerEffect[1]
                #killerData.Mag += killerEffect[2]
                #maybe have dict with 'name', 'phys', 'magic' as keys instead of 'name' and 'percent'
                killerDict[killerType] = killerData

            #masteries
            if (effect[1] == 3 and effect[2] == 6) and (effect[0] == 0 or effect[0] == 1):
                masteryEffect = effect[3]
                masteryType = masteryEffect[0]                
                if not masteryType:
                    continue

                masteryBonus = OrderedDict()

                if (len(masteryEffect) > 5):
                    if masteryEffect[5]:
                        masteryBonus['hp%'] = masteryEffect[5]
                    if masteryEffect[6]:
                        masteryBonus['mp%'] = masteryEffect[6]
                if masteryEffect[1]:
                    masteryBonus['atk%'] = masteryEffect[1]
                if masteryEffect[2]:
                    masteryBonus['def%'] = masteryEffect[2]
                if masteryEffect[3]:
                    masteryBonus['mag%'] = masteryEffect[3]
                if masteryEffect[4]:
                    masteryBonus['spr%'] = masteryEffect[4]
                masteryBonus['equipedConditions'] = []
                masteryBonus['equipedConditions'].append(itemTypeString[masteryType])

                masteries.append(masteryBonus)

            #unarmed
            if (effect[0] == 1 and effect[1] == 3 and effect[2] == 19):
                unarmedMasteryEffect = effect[3]
                unarmedBonus = OrderedDict()
                if unarmedMasteryEffect[0]:
                    unarmedBonus['atk%'] = unarmedMasteryEffect[0]
                #all of the following is assummed. only atk is known.
                if len(unarmedMasteryEffect) > 1:
                    if unarmedMasteryEffect[1]:
                        unarmedBonus['def%'] = unarmedMasteryEffect[1]
                    if unarmedMasteryEffect[2]:
                        unarmedBonus['mag%'] = unarmedMasteryEffect[2]
                    if unarmedMasteryEffect[3]:
                        unarmedBonus['spr%'] = unarmedMasteryEffect[3]

                unarmedBonus['equipedConditions'] = ['unarmed']
                masteries.append(unarmedBonus)
                
            #element based masteries
            if effect[0] == 1 and effect[1] == 3 and effect[2] == 10004:
                elementBonus = OrderedDict()
                elementEffect = effect[3]
                elementType = elementEffect[0]
                if elementEffect[1]:
                    elementBonus['hp%'] = elementEffect[1]
                if elementEffect[2]:
                    elementBonus['mp%'] = elementEffect[2]
                if elementEffect[3]:
                    elementBonus['atk%'] = elementEffect[3]
                if elementEffect[4]:
                    elementBonus['mag%'] = elementEffect[4]
                if elementEffect[5]:
                    elementBonus['def%'] = elementEffect[5]
                if elementEffect[6]:
                    elementBonus['spr%'] = elementEffect[6]
                elementBonus['equipedConditions'] = elementString[elementType]
                masteries.append(elementBonus)

            
    passiveStat = OrderedDict()
    if unitBonus.Hp:
        passiveStat['hp%'] = unitBonus.Hp
    if unitBonus.Mp:
        passiveStat['mp%'] = unitBonus.Mp
    if unitBonus.Atk:
        passiveStat['atk%'] = unitBonus.Atk
    if unitBonus.Def:
        passiveStat['def%'] = unitBonus.Def
    if unitBonus.Mag:
        passiveStat['mag%'] = unitBonus.Mag
    if unitBonus.Spr:
        passiveStat['spr%'] = unitBonus.Spr
    if typesString:
        if len(typesString) == 1:
            passiveStat['dualWield'] = typesString[0]
        else:
            passiveStat['dualWield'] = typesString
    if killerDict:
        killers = []
        for key in killerDict:
            killerName = killerString[key]
            killerPhys = killerDict[key].Phys
            killerObj = OrderedDict()
            killerObj['name'] = killerName
            killerObj['percent'] = killerPhys
            killers.append(killerObj)
        passiveStat['killers'] = killers

    returnSkills = []
    if passiveStat:
        returnSkills.append(passiveStat)
    if masteries:
        returnSkills.extend(masteries)
    return returnSkills


if __name__ == '__main__':
    parseData()
