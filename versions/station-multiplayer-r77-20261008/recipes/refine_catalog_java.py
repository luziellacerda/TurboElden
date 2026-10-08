"""Overlay only signed content binding and the display-only catalogue evidence publication."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT.parent/'station-current-r55-20261006/client/src/java/org/emulationstation/frontend/station'
DEST=ROOT/'java/client/src/java/org/emulationstation/frontend/station'
PIN={'StationCatalog.java':'1a5f2eb81e48857d8ff8e4c3e67a6eede8358bf494c4351770205613fd56b572','StationFrontend.java':'f9219d5ef4158cae16ce6d046e441b2b08e396826dc709a6adfd7ffa0d5d3af9'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)
def main():
    output={}
    for name,pin in PIN.items():
        source=BASE/name;assert sha(source)==pin,name
        s=source.read_text('utf8')
        if name=='StationCatalog.java':
            s=replace(s,'public final String description, developer, publisher, genre, players, releaseDate;','public final String description, developer, publisher, genre, players, releaseDate;\n        public final String contentSha256;')
            s=replace(s,'genre=metadataText(row,"genre",80);players=metadataText(row,"players",40);releaseDate=metadataText(row,"releaseDate",40);','genre=metadataText(row,"genre",80);players=metadataText(row,"players",40);releaseDate=metadataText(row,"releaseDate",40);\n            Object digest=row.opt("contentSha256");contentSha256=digest instanceof String&&StationCatalogPlayerEvidence.digest((String)digest)?(String)digest:"";')
            s=replace(s,'row.put("coverId", item.coverId);','row.put("coverId", item.coverId);\n                if(!item.contentSha256.isEmpty())row.put("contentSha256",item.contentSha256);')
        else:
            s=replace(s,'  images.replaceCatalog(()->publishCatalog(rows.toArray(new byte[0][]),utf8(library.displayName)));','  StationCatalogPlayerEvidenceLoader.publish(app.context,library.catalog);\n  images.replaceCatalog(()->publishCatalog(rows.toArray(new byte[0][]),utf8(library.displayName)));')
        dest=DEST/name
        if dest.exists():assert dest.read_text('utf8')==s,'Do not overwrite a different overlay: '+name
        else:dest.write_text(s,'utf8')
        output[name]={'baseSHA256':pin,'sha256':sha(dest)}
    (ROOT/'catalog/java-binding.json').write_text(json.dumps(output,indent=2)+'\n','utf8')
    print(json.dumps(output,indent=2))
if __name__=='__main__':main()
