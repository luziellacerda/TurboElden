"""Read exact existing server commit; emit reviewable patch and isolated local index test. No deploy."""
from pathlib import Path
import difflib, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parent
CLONE=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
BUILD=Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\build\server-capacity-40000')
COMMIT='fa7a10cccd93a8d97de16e28fbc81b8da4c6fa61'
SOURCE='src/TurboRamaSuiteOnlineServer/StationLibrary.cs'
base=subprocess.check_output(['git','-c','safe.directory='+str(CLONE),'-C',str(CLONE),'show',COMMIT+':'+SOURCE]).decode('utf-8')
changed=base.replace('public const int MaximumItems = 4096;', '''// Private entries include hidden compatibility IDs; public catalog is limited separately.
    public const int MaximumItems = 65_536;
    public const int MaximumCatalogItems = 40_000;
    public const long MaximumIndexBytes = 128L * 1024 * 1024;''')
changed=changed.replace('        var json = File.ReadAllText(path);','''        if (new FileInfo(path).Length > MaximumIndexBytes)
            throw new InvalidOperationException("Station library index is too large.");
        var json = File.ReadAllText(path);''')
changed=changed.replace('        foreach (var row in itemsElement.EnumerateArray())','        var visibleCount = 0;\n        foreach (var row in itemsElement.EnumerateArray())')
changed=changed.replace('            StationArtifactDescriptor? artifact = null;','''            if (catalogVisible && ++visibleCount > MaximumCatalogItems)
                throw new InvalidOperationException("Station public catalog exceeds supported item count.");
            StationArtifactDescriptor? artifact = null;''')
assert changed!=base and 'MaximumCatalogItems = 40_000' in changed and '++visibleCount' in changed
patch=''.join(difflib.unified_diff(base.splitlines(True),changed.splitlines(True),fromfile='a/'+SOURCE,tofile='b/'+SOURCE))
(ROOT/'servidor-capacidade-40000.patch').write_text(patch,encoding='utf-8',newline='\n')
(ROOT/'server-patch-manifest.json').write_text(json.dumps({'baseCommit':COMMIT,'file':SOURCE,'baseSha256':hashlib.sha256(base.encode()).hexdigest(),'candidateSha256':hashlib.sha256(changed.encode()).hexdigest(),'productionApplied':False,'publicMaximum':40000,'privateMaximumIncludingCompatibility':65536,'indexBytesMaximum':134217728},indent=2)+'\n',encoding='utf-8')
BUILD.mkdir(parents=True,exist_ok=True)
(BUILD/'StationLibrary.cs').write_text(changed,encoding='utf-8')
(BUILD/'Capacity.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net9.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>',encoding='utf-8')
(BUILD/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>',encoding='utf-8')
(BUILD/'ProtocolAdapter.cs').write_text('''// Exact IsSafeLibraryId implementation from StationProtocol at the base commit.
// Only adapter needed by this isolated StationLibrary compile; not a substitute for API tests.
namespace TurboRamaSuiteOnlineServer;
public static class StationProtocol {
 public static bool IsSafeLibraryId(string value) =>
 value.Length is >= 8 and <= 64 &&
 value.All(c => char.IsAsciiLetterOrDigit(c) || c is '-' or '_') &&
 !value.Contains("..", StringComparison.Ordinal);
}
''',encoding='utf-8')
(BUILD/'Program.cs').write_text((ROOT/'ServerCapacityTest.cs').read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps({'patch':str(ROOT/'servidor-capacidade-40000.patch'),'testProject':str(BUILD/'Capacity.csproj'),'productionApplied':False}))
