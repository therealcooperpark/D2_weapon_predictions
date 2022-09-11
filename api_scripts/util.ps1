$ammoType = @{
    'key1' = 'primary';
    'key2' = 'special';
    'key3' = 'heavy';
}

$elementClass = @{
    'key1' = 'kinetic';
    'key2' = 'arc';
    'key3' = 'solar';
    'key4' = 'void';
    'key6' = 'stasis';
}

$hiddenStats = @(
    1345609583, # aim_assistance
    1931675084, # inventory_size
    3555269338, # zoom
    2715839340  # recoil_direction
)

function Get-WeaponType {
    param( [string[]]$TraitIds )

    $weaponType = 'trace_rifle'
    if ($TraitIds -notcontains 'weapon_type.trace_rifle') {
        $weaponType = $TraitIds | Where-Object { $_ -match 'weapon_type\.' } | Select-Object -First 1
        $weaponType = $weaponType.replace('weapon_type.', '')
    }

    $weaponType
}
function Get-AmmoType {
    param( [int64]$Key )
    $ammoType['key' + $Key]
}

function Get-ElementClass {
    param( [int64]$Key )
    $elementClass['key' + $Key]
}

function Get-Stats {
    param( $WeaponStats, $StatsData, [int64[]]$VisibleStatHashes )

    $currentStats = @{}

    foreach ($statHash in ($VisibleStatHashes + $hiddenStats)) {
        $value = $WeaponStats.$statHash.value
        if ($null -ne $value) {
            $currentStats[$StatsData.$statHash] = $value
        }
    }

    $currentStats
}

function Get-Frame {
    param( $SocketsData, $Entries )

    # 3956125808 is usually the frame perk
    $framePerk = $Entries | Where-Object { $_.socketTypeHash -eq 3956125808 }
    $SocketsData.($framePerk.singleInitialItemHash) | Select-Object name, description, icon
}

function Get-Perks {
    param( $SocketsData, $PlugsetsData, $Entries )

    $perks = @()
    $cleanedEntries = $Entries | Where-Object { $_.socketTypeHash -ne 3956125808 -and $_.singleInitialItemHash -ne 0 }

    foreach ($entry in $cleanedEntries) {
        if ($null -ne $entry.randomizedPlugSetHash) {
            foreach ($hash in $entry.randomizedPlugSetHash) {
                $currentPerks = $PlugsetsData.$hash | Foreach-Object { $SocketsData.($_) } | Where-Object { $_ -ne $null }
                $perks += @(, $currentPerks)
            }
        } else {
            $currentPerk = $SocketsData.($entry.singleInitialItemHash)
            if ($currentPerk) {
                $perks += @(, @($currentPerk))
            }
        }
    }

    $perks
}
