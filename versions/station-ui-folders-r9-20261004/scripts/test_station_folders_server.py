from pathlib import Path
import subprocess,json
R=Path(r'E:\ESTUDO APK\work\station-netplay-20261004');W=R/'folders/server-tests';W.mkdir(parents=True,exist_ok=True)
(W/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>','utf8')
project=R/'server/upstream/src/TurboRamaSuiteOnlineServer/TurboRamaSuiteOnlineServer.csproj'
(W/'FolderTests.csproj').write_text(f'''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup><ItemGroup><ProjectReference Include="{project}" /></ItemGroup></Project>''','utf8')
(W/'Program.cs').write_text(r'''using System.Text.Json.Nodes;
using TurboRamaSuiteOnlineServer;
var work=Path.Combine(AppContext.BaseDirectory,"fixtures-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(work);var count=0;
void Check(bool ok){count++;if(!ok)throw new Exception("Check "+count);}
JsonObject Row()=>new(){["itemId"]="station_fixture001",["coverId"]="cover_fixture001",["name"]="Jogo fixture",["platform"]="snes",["revision"]=1,["filePath"]=Path.Combine(work,"game.rom"),["coverPath"]=Path.Combine(work,"cover.png")};
StationLibrary Load(JsonObject row){var path=Path.Combine(work,Guid.NewGuid().ToString("N")+".json");File.WriteAllText(path,new JsonObject{["revision"]=2,["items"]=new JsonArray(row)}.ToJsonString());return StationLibrary.TryLoad(path)!;}
void Reject(JsonNode? path){var row=Row();row["folderPath"]=path;try{Load(row);throw new Exception("Invalid folder accepted");}catch(InvalidOperationException){count++;}}
var flat=Load(Row());Check(flat.Catalog[0].FolderPath.Count==0);
var row=Row();row["folderPath"]=new JsonArray("Selecionados","Traduções");var item=Load(row).Catalog[0];Check(item.FolderPath.SequenceEqual(new[]{"Selecionados","Traduções"}));Check(item.ItemId==flat.Catalog[0].ItemId);Check(item.CoverId==flat.Catalog[0].CoverId);Check(item.Revision==1);
foreach(var bad in new[]{""," ",".","..","a/b","a\\b","bad\nname",new string('x',81)})Reject(new JsonArray(bad));
Reject(null);Reject(JsonValue.Create("RPG"));Reject(new JsonArray(1));Reject(new JsonArray((JsonNode?)null));
Reject(new JsonArray("1","2","3","4","5","6","7","8","9"));
row=Row();row["folderPath"]=new JsonArray("日本語 🎮");Check(Load(row).Catalog[0].FolderPath[0]=="日本語 🎮");
row=Row();row["folderPath"]=new JsonArray();Check(Load(row).Catalog[0].FolderPath.Count==0);
Console.WriteLine($"PASS {count} server folder checks; default, nested, Unicode, invalid input, preserved IDs/covers/revision");
''','utf8')
for args,name in [(['dotnet','restore',W/'FolderTests.csproj','--configfile',W/'NuGet.Config','--nologo'],'restore'),(['dotnet','run','--project',W/'FolderTests.csproj','--no-restore'],'test')]:
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(W/(name+'.log')).write_text(p.stdout+p.stderr,'utf8');assert p.returncode==0,p.stdout+p.stderr
 print(p.stdout,flush=True)
