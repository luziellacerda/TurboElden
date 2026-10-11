param(
    [Parameter(Mandatory = $true)][string]$Apk,
    [string]$Expected = 'b2725c79238a1da67ab1d485cb86dd7875b618ad5fb4b63a7f0acb829a02a9ee'
)

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $Apk))
try {
    $entriesByName = @{}
    $names = [System.Collections.Generic.List[string]]::new()
    foreach ($entry in $archive.Entries | Where-Object {
        $_.FullName.StartsWith('assets/resources/', [StringComparison]::Ordinal) -and
        -not $_.FullName.EndsWith('/', [StringComparison]::Ordinal)
    }) {
        $entriesByName.Add($entry.FullName, $entry)
        $names.Add($entry.FullName)
    }
    $nameArray = $names.ToArray()
    [Array]::Sort($nameArray, [StringComparer]::Ordinal)
    $lines = [System.Collections.Generic.List[string]]::new()
    [long]$bytes = 0
    foreach ($name in $nameArray) {
        $entry = $entriesByName[$name]
        $stream = $entry.Open()
        $hasher = [System.Security.Cryptography.SHA256]::Create()
        try {
            $digest = [Convert]::ToHexString($hasher.ComputeHash($stream)).ToLowerInvariant()
        } finally {
            $hasher.Dispose()
            $stream.Dispose()
        }
        $lines.Add(('{0}|{1}|{2}' -f $entry.FullName, $entry.Length, $digest))
        $bytes += $entry.Length
    }
    $manifestText = [Text.StringBuilder]::new()
    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($index -gt 0) { [void]$manifestText.Append([char]10) }
        [void]$manifestText.Append($lines[$index])
    }
    $payload = [Text.Encoding]::UTF8.GetBytes($manifestText.ToString())
    $manifestHasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        $actual = [Convert]::ToHexString($manifestHasher.ComputeHash($payload)).ToLowerInvariant()
    } finally {
        $manifestHasher.Dispose()
    }
    if ($nameArray.Count -ne 199) { throw "Expected 199 resources, found $($nameArray.Count)" }
    if ($bytes -ne 81660567) { throw "Expected 81660567 bytes, found $bytes" }
    if ($actual -ne $Expected) { throw "Expected $Expected, found $actual" }
    [pscustomobject]@{ Files = $nameArray.Count; Bytes = $bytes; SHA256 = $actual }
} finally {
    $archive.Dispose()
}
