using System.Text.Json;
using System.Security.Cryptography;
using TurboRamaSuiteOnlineServer;

// Only isolated index/parser tests. No production database, license, ROM or route.
var root=Path.GetFullPath(args[0]);Directory.CreateDirectory(root);
var artifact=Path.Combine(root,"fixture.bin");File.WriteAllBytes(artifact,new byte[]{1,2,3,4});
var cover=Path.Combine(root,"fixture.png");File.WriteAllBytes(cover,new byte[]{137,80,78,71,13,10,26,10});
var digest=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(artifact))).ToLowerInvariant();
int checks=0;
void Check(bool value,string message){checks++;if(!value)throw new Exception(message);}
string Index(int visible,int hidden,bool descriptors){
 var path=Path.Combine(root,$"index-{visible}-{hidden}-{descriptors}.json");
 using var stream=File.Create(path);using var json=new Utf8JsonWriter(stream);
 json.WriteStartObject();json.WriteNumber("revision",4);json.WriteStartArray("items");
 for(int i=0;i<visible+hidden;i++){
  json.WriteStartObject();json.WriteString("itemId",$"capacity_{100000+i}");json.WriteString("name","Fixture");
  json.WriteString("platform",i%2==0?"snes":"megadrive");json.WriteNumber("revision",4);
  json.WriteString("coverId","fixture_cover");json.WriteString("filePath",artifact);json.WriteString("coverPath",cover);
  json.WriteBoolean("catalogVisible",i<visible);
  if(descriptors){json.WriteStartObject("artifact");json.WriteString("fileName","fixture.bin");json.WriteNumber("sizeBytes",4);
   json.WriteString("sha256",digest);json.WriteString("format","raw");json.WriteString("launchPath","fixture.bin");
   json.WriteNumber("expandedSizeBytes",4);json.WriteNumber("fileCount",1);json.WriteEndObject();}
  json.WriteEndObject();
 }
 json.WriteEndArray();json.WriteEndObject();return path;
}
void Reject(Action action){try{action();throw new Exception("Expected index rejection");}catch(InvalidOperationException){checks++;}}
var start=System.Diagnostics.Stopwatch.StartNew();
var current=StationLibrary.TryLoad(Index(40000,255,true))!;
Check(current.ItemCount==40000,"Public count");Check(current.CompatibilityItemCount==255,"Hidden IDs preserved");
Check(current.ContainsItem("capacity_140254"),"Last hidden ID retained");
Check(current.TryResolve("capacity_139999",out var path,out var entry)&&path==artifact,"Last public file resolvable");
Check(current.Catalog.All(x=>x.Revision==4),"Item revisions retained");
var parseMs=start.ElapsedMilliseconds;
Reject(()=>StationLibrary.TryLoad(Index(40001,0,false)));
Check(StationLibrary.TryLoad(Index(40000,25536,false))!.CompatibilityItemCount==25536,"Private boundary 65536 accepted");
Reject(()=>StationLibrary.TryLoad(Index(40000,25537,false)));
var tooLarge=Path.Combine(root,"oversize-index.json");using(var stream=File.Create(tooLarge))stream.SetLength(StationLibrary.MaximumIndexBytes+1);
Reject(()=>StationLibrary.TryLoad(tooLarge));File.Delete(tooLarge);
Console.WriteLine(JsonSerializer.Serialize(new{checks,publicItems=40000,hiddenItems=255,descriptorHashesChecked=40255,parseMillis=parseMs,synthetic=true,fullApiTest=false,productionApplied=false}));
