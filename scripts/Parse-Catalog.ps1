param(
    [Parameter(Mandatory = $true)]
    [string]$CatalogPath,

    [string]$OutputPath = ".\jogos-catalogo.csv"
)

$resolvedCatalog = (Resolve-Path -LiteralPath $CatalogPath).Path
$catalog = Get-Content -LiteralPath $resolvedCatalog -Raw -Encoding UTF8 | ConvertFrom-Json

if ($catalog -is [System.Array]) {
    $drawers = $catalog
} elseif ($null -ne $catalog.drawers) {
    $drawers = @($catalog.drawers)
} elseif ($null -ne $catalog.items) {
    $drawers = @($catalog.items)
} else {
    $drawers = @($catalog)
}

$rows = foreach ($drawer in $drawers) {
    $drawerName = if ($drawer.DisplayName) { $drawer.DisplayName } elseif ($drawer.displayName) { $drawer.displayName } elseif ($drawer.Name) { $drawer.Name } else { $drawer.name }
    $files = if ($null -ne $drawer.Files) { @($drawer.Files) } elseif ($null -ne $drawer.files) { @($drawer.files) } else { @($drawer) }

    foreach ($game in $files) {
        [pscustomobject]@{
            Drawer         = $drawerName
            Id             = if ($null -ne $game.Id) { $game.Id } else { $game.id }
            Name           = if ($game.Name) { $game.Name } else { $game.name }
            DisplayName    = if ($game.DisplayName) { $game.DisplayName } else { $game.displayName }
            Url            = if ($game.Url) { $game.Url } else { $game.url }
            CoverImage     = if ($game.CoverImage) { $game.CoverImage } else { $game.coverImage }
            DefaultSubPath = if ($game.DefaultSubPath) { $game.DefaultSubPath } else { $game.defaultSubPath }
            SubDirectory   = if ($game.SubDirectory) { $game.SubDirectory } else { $game.subDirectory }
            Downloads      = $game.downloads
        }
    }
}

$rows | Export-Csv -LiteralPath $OutputPath -NoTypeInformation -Encoding UTF8
Write-Output ("Exportados {0} itens para {1}" -f @($rows).Count, (Resolve-Path -LiteralPath $OutputPath).Path)
