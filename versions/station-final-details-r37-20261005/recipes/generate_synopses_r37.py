"""Build R37 offline synopses for the exact 2,212-item Station revision 14.

No network calls, authentication data, title guessing or server modifications.
The catalog input is a public, pinned Git TSV; full published descriptions stay
byte-for-byte equal except the one explicitly reviewed title-only value.
"""
from pathlib import Path
import argparse, collections, csv, hashlib, io, json, posixpath, re, subprocess
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
SERVER_COMMIT='100e4bbd92aa4c85cda10a633e6463fbb24ae8ab'
SERVER_PATH='docs/station-android/biblioteca-neogeocd-20261005/catalogo-completo.tsv'
CATALOG_SHA='3dae0cfa3877fba31b9a347b58795fe0df95333aea628b9ea8be597b7ccfed6e'
NEOGEO_SHA='555672bfb311bcef62a5f5409e81a199b37e32eb082f2b04c5a1619bbcbe5463'
SNES_SOURCE_SHA='733b6ef4c642d171ca71edf23f6426bb4e2720899888740c6660aa826a90e3cc'
LABELS={'snes':'Super Nintendo','snesbr':'Super Nintendo - BR','megadrive':'MegaDrive','megadrivebr':'MegaDrive - BR','n64':'Nintendo 64','neogeo':'Neo Geo','neogeocd':'Neo Geo CD'}
EXPECTED={'snes':644,'snesbr':191,'megadrive':887,'megadrivebr':94,'n64':157,'neogeo':189,'neogeocd':50}
OVERRIDES={'ab9773189dbfc1571ca0d56adb13ff32':'Old Towers'}
BOOTLEGS={'station_759d5d8bed21547d5e3fe8c303bdadf7','station_ed2bf0bfae84e0d02a0eefbb8c0991fe','station_fd15a6f06bf33793b0d652a0bed98dbe'}
def sha(data): return hashlib.sha256(data).hexdigest()
def require(condition,message):
    if not condition: raise ValueError(message)
def checked(path,expected):
    raw=Path(path).read_bytes();require(sha(raw)==expected,'Pinned source hash mismatch: '+str(path));return raw
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def parse_catalog(raw):
    require(sha(raw)==CATALOG_SHA,'Pinned catalog changed')
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')),delimiter='\t'))
    require(len(rows)==2212,'Unexpected catalog size')
    require(len({r['itemId'] for r in rows})==len(rows),'Duplicate catalog ID')
    require(dict(collections.Counter(r['platform'] for r in rows))==EXPECTED,'Unexpected platforms/counts')
    require(all(r['catalogVisible']=='yes' for r in rows),'Hidden items in input')
    return rows
def stable_id(platform,path):
    path=path.replace('\\','/')
    require(path and not path.startswith('/') and ':' not in path,'Invalid relative path')
    normalized=posixpath.normpath(path)
    require(normalized!='..' and not normalized.startswith('../'),'Escaping relative path')
    return 'station_'+sha((platform+':'+normalized).encode('utf8'))[:32]
def xml_games(raw):
    require(b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper(),'XML entities are unsupported')
    return ET.fromstring(raw).findall('game')
def make_records(rows,neo_raw,snes_raw,editorials):
    require(sha(neo_raw)==NEOGEO_SHA,'Neo Geo source changed')
    require(sha(snes_raw)==SNES_SOURCE_SHA,'SNES source changed')
    neo={}
    for ordinal,g in enumerate(xml_games(neo_raw),1):
        identity=stable_id('neogeo',g.findtext('path',''))
        require(identity not in neo,'Duplicate Neo Geo path identity')
        neo[identity]=(ordinal,g)
    snes=xml_games(snes_raw)
    edits={e['itemId']:e for e in editorials}
    require(len(edits)==len(editorials)==17,'Expected 17 curated titles')
    records=[];consumed=set();recovered=0;preserved=0
    for r in rows:
        identity=r['itemId'];original=r['description'];description=original
        record={'itemId':identity,'platform':r['platform'],'label':LABELS[r['platform']],'name':r['name'],
                'catalogRevision':14,'catalogItemRevision':int(r['itemRevision']),
                'serverDescription':original,'serverDescriptionSha256':sha(original.encode('utf8'))}
        if identity in edits:
            e=edits[identity]
            require(e['platform']==r['platform'] and e['name']==r['name'],'Curated identity mismatch '+identity)
            if original.strip():require(OVERRIDES.get(identity)==original==e.get('replaceServerDescriptionExact'),'Unexpected overwrite')
            else: require('replaceServerDescriptionExact' not in e,'Invalid empty-description override')
            require(e['language']=='pt-BR' and e['method']=='original-editorial-summary' and bool(e['sources']),'Incomplete provenance')
            for source in e['sources']:
                if source['kind']=='local-xml':
                    require(source['sourceSha256']==SNES_SOURCE_SHA,'Unexpected XML authority')
                    g=snes[source['sourceOrdinal']-1]
                    # Preserve region identity via the exact catalog ROM basename.
                    original_stem=Path(g.findtext('path','').replace('\\','/')).stem
                    artifact_stem=Path(r['artifactFileName']).stem
                    require(original_stem==artifact_stem and r['platform']=='snes','SNES editorial source mismatch')
                    require(g.findtext('desc','').strip(),'Empty editorial XML source')
                elif source['kind']=='web':require(source['url'].startswith('https://') and source['accessed']=='2026-10-05','Invalid web provenance')
                else:raise ValueError('Unknown editorial provenance')
            description=e['description'];record['provenance']={k:v for k,v in e.items() if k not in ('itemId','platform','name','description')}
            record['sourceKind']='editorial';consumed.add(identity)
        elif not original.strip():
            require(r['platform']=='neogeo' and identity in neo,'Unresolved description '+identity)
            ordinal,g=neo[identity];description=g.findtext('desc','')
            require(bool(description.strip()),'Empty exact XML synopsis')
            record['sourceKind']='exact-xml';record['provenance']={'sourceSha256':NEOGEO_SHA,'sourceOrdinal':ordinal,'sourcePlatform':'neogeo','sourceRelativePath':g.findtext('path',''),'sourceName':g.findtext('name',''),'sourceDescription':description,'identity':'station_ + sha256(platform + colon + normalized relative POSIX path)[:32]'}
            if identity in BOOTLEGS:
                require('bootleg' in r['name'].lower(),'Unverified variant')
                description='Esta entrada é uma variante não oficial (bootleg). A sinopse a seguir apresenta o jogo base; as alterações específicas desta variante não foram documentadas.\n\n'+description
                record['provenance']['variantDisclosure']='Published catalog identifies bootleg; no patch-specific behavior claimed.'
            recovered+=1
        else:
            preserved+=1;record['sourceKind']='server-catalog';record['provenance']={'commit':SERVER_COMMIT,'path':SERVER_PATH,'catalogSha256':CATALOG_SHA,'field':'description','preservedVerbatim':True}
        require(len(description.strip())>=30,'Description is empty/title-only: '+identity)
        require(not re.search(r'sinopse ainda|sinopse n.o dispon.vel|sinopse ainda n.o localizada|no description available',description,re.I),'Placeholder '+identity)
        require('\ufffd' not in description and all(ord(c)>=32 or c in '\n\r\t' for c in description),'Invalid description characters '+identity)
        record['description']=description;record['descriptionSha256']=sha(description.encode('utf8'));records.append(record)
    require(consumed==set(edits),'Unused editorial items')
    require(recovered==27 and preserved==2168,'Unexpected source counts')
    return sorted(records,key=lambda x:x['itemId'])
def header(records):
    lines=['#pragma once','// Generated by generate_synopses_r37.py; exact Station revision 14 IDs and labels.',
           '// 2168 server descriptions preserved, 27 exact XML recoveries, 17 original editorial summaries.',
           '// Keep full descriptions: the native synopsis viewport provides scrolling.','static const GameInfo stationGameInfos[]={']
    for r in records:
        p=r['provenance'];kind=r['sourceKind']
        source=('xml-sha256:'+p['sourceSha256']+':'+str(p['sourceOrdinal'])) if kind=='exact-xml' else ('editorial:pt-BR:20261005:'+r['descriptionSha256']) if kind=='editorial' else 'station-catalog:14:'+SERVER_COMMIT
        fields=[r['label'],r['itemId'],r['name'],r['description'],source]
        lines.append('{'+','.join(json.dumps(s,ensure_ascii=False).replace('?',r'\?') for s in fields)+',1},')
    lines.extend(['};','static constexpr int NSTATIONGAMEINFOS=sizeof(stationGameInfos)/sizeof(stationGameInfos[0]);',
     '// Only replace the exact verified title-only server value. New server prose always wins.',
     'static bool stationSynopsisNeedsOverride(const char*id,const char*serverDescription){',
     ' return id&&serverDescription&&strcmp(id,"ab9773189dbfc1571ca0d56adb13ff32")==0&&strcmp(serverDescription,"Old Towers")==0;',
     '}'])
    return '\n'.join(lines)+'\n'
def main():
    p=argparse.ArgumentParser();p.add_argument('--server-repo',type=Path,default=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002'))
    p.add_argument('--catalog',type=Path,default=ROOT/'data/synopses-catalog-14.tsv');p.add_argument('--neo-xml',type=Path,default=Path(r'G:\TURBORAMA\RetroBat\roms\neogeo\gamelist.xml'))
    p.add_argument('--snes-xml',type=Path,default=Path(r'E:\ESTUDO APK\work\native-carousel\implementation\metadata-sources\catalog-xml\34-snes.xml'))
    p.add_argument('--editorial',type=Path,default=ROOT/'data/synopses-editorial.json');a=p.parse_args()
    if a.catalog.exists():raw=checked(a.catalog,CATALOG_SHA)
    else:
        raw=subprocess.check_output(['git','-c','safe.directory='+a.server_repo.as_posix(),'-C',str(a.server_repo),'show',SERVER_COMMIT+':'+SERVER_PATH])
        require(sha(raw)==CATALOG_SHA,'Git input changed');a.catalog.parent.mkdir(parents=True,exist_ok=True);a.catalog.write_bytes(raw)
    edits=json.loads(a.editorial.read_text('utf8'));rows=parse_catalog(raw)
    records=make_records(rows,checked(a.neo_xml,NEOGEO_SHA),checked(a.snes_xml,SNES_SOURCE_SHA),edits)
    dump(ROOT/'data/synopses-complete.json',records)
    output=ROOT/'native/station_game_infos.h';output.parent.mkdir(parents=True,exist_ok=True);output.write_text(header(records),encoding='utf8')
    report={'scope':'Frozen public catalog revision 14, not a live HTTP read; no new IDs outside these 2212 implied.',
      'serverCommit':SERVER_COMMIT,'catalogPath':SERVER_PATH,'catalogSha256':CATALOG_SHA,'catalogRevision':14,'items':len(records),
      'platforms':EXPECTED,'sourceCounts':dict(collections.Counter(r['sourceKind'] for r in records)),
      'originalServerNonempty':2169,'originalServerEmpty':43,'serverDescriptionsPreservedVerbatim':2168,'titleOnlyValuesEnriched':1,
      'missing':0,'placeholders':0,'duplicates':0,'neoXmlSha256':NEOGEO_SHA,'snesXmlSha256':SNES_SOURCE_SHA,
      'editorialSha256':sha(a.editorial.read_bytes()),'outputHeaderSha256':sha(output.read_bytes()),'completeDataSha256':sha((ROOT/'data/synopses-complete.json').read_bytes()),
      'overrideHookRequired':'Call stationSynopsisNeedsOverride(id,serverDescription) in native_info before choosing server text; only Old Towers title-only is overridden.',
      'limitations':['The 2168 preserved server descriptions have not been individually fact-checked or translated.','New future IDs need server descriptions or a regenerated offline index.','Named variants are described without inventing patch-specific behavior; ROM binaries not inspected.','No APK, installation, server, network or netplay changes performed by this generator.']}
    dump(ROOT/'evidence/synopses-build.json',report);print(json.dumps(report,ensure_ascii=True))
if __name__=='__main__':main()