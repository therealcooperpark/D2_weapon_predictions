#! /usr/bin/env python3

import json
import os
import requests


# Create data folder
#os.mkdir('source/')
#os.chdir('source/')

baseurl = 'https://www.bungie.net'

# Download the manifest
response = requests.get(f'{baseurl}/Platform/Destiny2/Manifest/')
manifest = response.json()['Response']


# Write out manifest version
with open('version.txt', 'w') as version_file:
    version_file.write(manifest['version'])

# Collect Sunset Powercap file
pwr_url = manifest['jsonWorldComponentContentPaths']['en']['DestinyPowerCapDefinition']
pwr_header = {'Accept-Encoding' : 'gzip'}
pwr_response = requests.get(f'{baseurl}{pwr_url}', headers=pwr_header)
pwrcapData = pwr_response.json()

sunset_gear = {}
for key, val in pwrcapData.items():
    if val['powerCap'] < 900000:
        sunset_gear[val['hash']] = val['powerCap']

with open('sunset.json', 'w') as sunset_file:
    json.dump(sunset_gear, sunset_file, indent=4)

# Write out Stats file
stat_url = manifest['jsonWorldComponentContentPaths']['en']['DestinyStatDefinition']
stat_header = {'Accept-Encoding' : 'gzip'}
stat_response = requests.get(f'{baseurl}{stat_url}', headers=stat_header)
statData = stat_response.json()

remappedStats = {}
for key, val in statData.items():
    name = val['displayProperties']['name'].lower().replace(' ', '_')
    if name != '':
        remappedStats[name] = val['hash']
        remappedStats[val['hash']] = name

with open('stats.json', 'w') as stat_file:
    json.dump(remappedStats, stat_file, indent=4)

# Write out Stat Groups file
group_url = manifest['jsonWorldComponentContentPaths']['en']['DestinyStatGroupDefinition']
group_header = {'Accept-Encoding' : 'gzip'}
group_response = requests.get(f'{baseurl}{group_url}', headers=group_header)
groupData = group_response.json()

remappedGroup = {}
for key, val in groupData.items():
    remappedGroup[val['hash']] = []
    for statHash in val['scaledStats']:
        remappedGroup[val['hash']].append(statHash['statHash'])

with open('statgroups.json', 'w') as group_file:
    json.dump(remappedGroup, group_file, indent=4)

# Write out Weapons file
weapon_url = manifest['jsonWorldComponentContentPaths']['en']['DestinyInventoryItemDefinition']
weapon_header = {'Accept-Encoding' : 'gzip'}
weapon_response = requests.get(f'{baseurl}{weapon_url}', headers=weapon_header)
weaponData = weapon_response.json()

remappedWeapons = {}
for key, val in weaponData.items():
    if 'itemCategoryHashes' in val.keys():
        if 1 in val['itemCategoryHashes'] and 3109687656 not in val['itemCategoryHashes']:
            remappedWeapons[key] = val

with open('weapons.json', 'w') as weapon_file:
    json.dump(remappedWeapons, weapon_file, indent=4)
