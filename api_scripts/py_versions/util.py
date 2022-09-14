#! /usr/bin/env python3

def get_weapontype(traitIds):
    weapontype = 'trace_rifle'
    if 'weapon_type.trace_rifle' not in traitIds:
        for trait in traitIds:
            if 'weapon_type.' in trait:
                weapontype = trait.replace('weapon_type.', '')
                break
    return weapontype

def get_ammotype(key):
    return ammotype['key'+key]

def get_elementclass(key):
    return elementClass['key'+key]

def get_stats(weaponStats, statsData, visibleStatHashes):
    currentStats = {}
    for statHash in visibleStatHashes + hiddenStats:
        value = weaponStats[statHash]['value']
        if value:
            currentStats[statsData[statHash]] = value
    return currentStats

def get_frame(socketsData, entries):
    # 3956125808 is usually the frame perk
    frameperks = []
    for entry in entries:
        if entry['socketTypeHash'] == 3956125808:
            frameperks.append(entry)
    frame = socketsData[frameperks[0]['singleInitialItemHash']]
    return [frame.name, frame.description, frame.icon] 

def get_perks(socketsData, plugsetsData, entries):
    perks = []
    cleanedEntries = [entry for entry in entries if entry['socketTypeHash'] != 3956125808 and entry['singleInitialItemHash'] != 0]

    for entry in cleanedEntries:
        if entry['randomizedPlugSetHash']:
            for hashid in entry['randomizedPlugSetHash']:
                currentPerks = plugsetsData['hash']


ammotype = {'key1' : 'primary',
            'key2' : 'special',
            'key3' : 'heavy'}

elementClass = {'key1' : 'kinetic',
                'key2' : 'arc',
                'key3' : 'solar',
                'key4' : 'void',
                'key6' : 'stasis'}

hiddenStats = [
                1345609583, # aim_assistance
                1931675084, # inventory_size
                3555269338, # zoom
                2715839340  # recoil_direction
              ]

