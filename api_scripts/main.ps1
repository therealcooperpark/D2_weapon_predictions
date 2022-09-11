. ".\util.ps1"

Write-Output 'Loading weapons JSON file...'
$weapons = Get-Content 'source/weapons.json' | ConvertFrom-Json

# ========================================
Write-Output 'Loading other JSON files...'
$sunsetPowercapData = Get-Content './source/sunset.json' | ConvertFrom-Json
$statsData = Get-Content './source/stats.json' | ConvertFrom-Json
$statGroupsData = Get-Content './source/statgroups.json' | ConvertFrom-Json
$socketsData = Get-Content './source/sockets.json' | ConvertFrom-Json
$plugsetsData = Get-Content './source/plugsets.json' | ConvertFrom-Json

# ========================================
Write-Output 'Mapping into objects...'
$remappedWeapons = $weapons | ForEach-Object {
    [ordered]@{
        id            = $_.hash;
        name          = $_.displayProperties.name;
        icon          = $_.displayProperties.icon;
        watermark     = $_.quality.displayVersionWatermarkIcons[0];
        screenshot    = $_.screenshot;
        flavor_text   = $_.flavorText;
        weapon_tier   = $_.inventory.tierTypeName.ToLower();
        ammo_type     = Get-AmmoType -Key $_.equippingBlock.ammoType;
        element_class = Get-ElementClass -Key $_.damageTypes[0];
        weapon_type   = Get-WeaponType -TraitIds $_.traitIds;
        powercap      = $sunsetPowercapData.($_.quality.versions[0].powerCapHash);
        stats         = Get-Stats -WeaponStats $_.stats.stats -StatsData $statsData -VisibleStatHashes $statGroupsData.($_.stats.statGroupHash);
        frame         = Get-Frame -SocketsData $socketsData -Entries $_.sockets.socketEntries;
        perks         = Get-Perks -SocketsData $socketsData -PlugsetsData $plugsetsData -Entries $_.sockets.socketEntries;
    }
}

Write-Output "Remapped $(($remappedWeapons | Measure-Object).Count) weapons!"

# ========================================
Write-Output 'Writing into major JSON files...'
New-Item -ItemType Directory -Force -Path '../data/weapons/id'
New-Item -ItemType Directory -Force -Path '../data/weapons/name'
Copy-Item 'source/version.txt' '../data/'

$remappedWeapons | ConvertTo-Json -Compress -Depth 100 | Out-File '../data/weapons/all.json'
$remappedWeapons | Foreach-Object {
    [ordered]@{
        id        = $_.id;
        name      = $_.name;
        icon      = $_.icon;
        watermark = $_.watermark;
    }
} | ConvertTo-Json -Compress -Depth 100 | Out-File '../data/weapons/all_lite.json'

# ========================================
Write-Output 'Writing into ID-based JSON files...'
foreach ($weapon in $remappedWeapons) {
    $weapon | ConvertTo-Json -Compress -Depth 100 | Out-File "../data/weapons/id/$($weapon.id).json"
}

# ========================================
Write-Output 'Writing into name-based JSON files...'
$uniqueWeaponNames = $remappedWeapons.name | Sort-Object | Get-Unique
foreach ($weaponName in $uniqueWeaponNames) {
    # https://stackoverflow.com/a/49941546
    $slugName = $weaponName.ToLower().Normalize([Text.NormalizationForm]::FormD)
    $slugName = $slugName -replace '\p{M}', '' -replace '[^A-Za-z0-9]', ''

    $matchedWeapons = $remappedWeapons | Where-Object { $_.name -eq $weaponName }

    if (($matchedWeapons | Measure-Object).Count -ne 1) {
        $matchedWeapons = ($matchedWeapons | Sort-Object id -Descending)[0]
    }

    $matchedWeapons | ConvertTo-Json -Compress -Depth 100 | Out-File "../data/weapons/name/${slugName}.json"
}

# ========================================
Write-Output 'Done!'
