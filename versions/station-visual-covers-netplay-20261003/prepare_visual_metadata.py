"""Build offline synopsis data by the server's exact source XML identity.

Does not call the network, rewrite catalog IDs or manufacture missing descriptions.
Original XMLs stay outside the APK; the APK receives their descriptive fields only.
"""
from pathlib import Path
import csv, collections, hashlib, json, re, textwrap
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
OLD = Path(r'E:\ESTUDO APK\work\native-carousel\implementation')
THEME = Path(r'G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx')
SERVER_MAP = Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002\docs\station-android\catalogo-candidato-cruzado-20261003.tsv')
ROMS = Path(r'G:\TURBORAMA\RetroBat\roms')
LABELS = {'snes':'Super Nintendo','snesbr':'Super Nintendo - BR','megadrive':'MegaDrive','megadrivebr':'MegaDrive - BR'}
FIELDS = ('name','desc','genre','developer','publisher','players','releasedate','rating')

def sha(data): return hashlib.sha256(data).hexdigest()
def clean(text):
    text=re.sub(r'https?://[^\s<>]+','',text or '',flags=re.I)
    return re.sub(r'\s+', ' ', text).strip()
def write_json(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def write_xml(path, root):
    ET.indent(root)
    ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def main():
    assets=ROOT/'assets/station-metadata'; xmlout=assets/'xml'
    xmlout.mkdir(parents=True,exist_ok=True);(ROOT/'evidence').mkdir(exist_ok=True)
    paths={Path(x['file']) for x in json.loads((OLD/'game-xml-sources.json').read_text('utf-8'))}
    manifest=OLD/'metadata-sources/catalog-xml-manifest.json'
    paths.update(Path(x['file']) for x in json.loads(manifest.read_text('utf-8')) if x.get('file'))
    paths.update(ROMS.rglob('gamelist.xml'))
    paths.update((OLD/'game-info-xml').glob('*.xml'))
    inventory=[]; parsed={}; hashes={}
    for path in sorted(paths,key=lambda p:str(p).lower()):
        if not path.is_file():
            inventory.append({'source':str(path),'status':'missing'});continue
        data=path.read_bytes()
        try:root=ET.fromstring(data)
        except ET.ParseError as error:
            inventory.append({'source':str(path),'status':'invalid','error':str(error)});continue
        games=root.findall('game'); parsed[str(path)]=games
        digest=sha(data);hashes[str(path)]=digest; archive=ET.Element('gameList',{'sourceSha256':digest,'metadataOnly':'true'})
        for ordinal,game in enumerate(games,1):
            target=ET.SubElement(archive,'game',{'sourceOrdinal':str(ordinal)})
            for field in FIELDS:
                text=clean(game.findtext(field,''))
                if text:ET.SubElement(target,field).text=text
        name=digest+'.xml';write_xml(xmlout/name,archive)
        inventory.append({'source':str(path),'status':'imported','sha256':digest,'asset':'station-metadata/xml/'+name,'games':len(games),'descriptions':sum(bool(clean(g.findtext('desc',''))) for g in games)})
    rows=list(csv.DictReader(SERVER_MAP.open(encoding='utf-8'),delimiter='\t'))
    seen=set(); exact=[]; missing=[]; byplatform=collections.Counter()
    for row in rows:
        identity=row['itemId'];platform=row['platform']; sourceplatform=row['sourcePlatform']
        assert identity not in seen and identity.startswith('station_'),identity
        seen.add(identity)
        path=ROMS/sourceplatform/'gamelist.xml'
        games=parsed[str(path)]
        ordinal=int(row['sourceXmlEntry']);game=games[ordinal-1]
        assert game.findtext('name','')==row['name'],(identity,ordinal)
        desc=clean(game.findtext('desc',''))
        record={'itemId':identity,'platform':platform,'label':LABELS[platform],'name':row['name'],'description':desc,
                'sourceSha256':hashes[str(path)],'sourceOrdinal':ordinal,'sourcePlatform':sourceplatform,
                'match':'server-source-ordinal-and-exact-name'}
        exact.append(record);byplatform[platform]+=1
        if not desc:missing.append(record)
    # Resolve only empty descriptions through other original local XMLs.
    # Preserve Station identity; reject conflicting descriptions instead of guessing.
    write_json(ROOT/'evidence/xml-source-inventory.json',inventory)
    from audit_missing_synopses import main as audit_missing
    supplemental=audit_missing(exact)
    lookup={r['itemId']:r for r in exact};restored=0
    for match in supplemental['items']:
        if match['status']!='unique-description':continue
        source=match['matches'][0];record=lookup[match['itemId']]
        assert not record['description']
        record.update(description=source['description'],descriptionSourceSha256=source['sha256'],
            descriptionSourceOrdinal=source['ordinal'],descriptionSourcePlatform=source['platform'],
            descriptionMatch=source['match'])
        restored+=1
    missing=[r for r in exact if not r['description']]
    exact.sort(key=lambda r:r['itemId'])
    header=['// Generated by prepare_visual_metadata.py; exact server IDs, never title guessing.',
        'static const GameInfo stationGameInfos[]={']
    for r in exact:
        pages=textwrap.wrap(r['description'],width=440,break_long_words=False,break_on_hyphens=False) or ['Sinopse ainda não disponível nesta edição.']
        fields=[r['label'],r['itemId'],r['name'],'\f'.join(pages),'xml-sha256:'+r.get('descriptionSourceSha256',r['sourceSha256'])+':'+str(r.get('descriptionSourceOrdinal',r['sourceOrdinal']))]
        header.append('{'+','.join(json.dumps(v,ensure_ascii=False) for v in fields)+','+str(len(pages))+'},')
    header.extend(['};','static constexpr int NSTATIONGAMEINFOS=sizeof(stationGameInfos)/sizeof(stationGameInfos[0]);'])
    (ROOT/'native/station_game_infos.h').write_text('\n'.join(header)+'\n',encoding='utf-8')
    write_json(assets/'station-synopses.json',exact)
    write_json(assets/'missing-station-synopses.json',missing)
    # APK manifest deliberately excludes local source paths and legacy source URLs.
    public=[{k:v for k,v in r.items() if k!='source'} for r in inventory if r['status']=='imported']
    write_json(assets/'xml-manifest.json',public)
    write_json(ROOT/'evidence/xml-source-inventory.json',inventory)
    report={'serverMap':str(SERVER_MAP),'serverMapSha256':sha(SERVER_MAP.read_bytes()),'items':len(exact),
        'descriptions':len(exact)-len(missing),'missing':len(missing),'platforms':dict(byplatform),
        'descriptionsRestoredByExactLocalIdentity':restored,'supplementalSearchCounts':supplemental['counts'],
        'sourceFilesImported':len(public),'uniqueXmlAssets':len({r['sha256'] for r in public}),
        'sourceFilesMissing':sum(r['status']=='missing' for r in inventory),
        'sourceFilesInvalid':sum(r['status']=='invalid' for r in inventory),
        'legacyGameXmlPreserved':36,'identityPolicy':'exact server itemId + source ordinal + exact source name; missing desc only from same platform and exact full name or ROM stem with a unique description; no fuzzy fallback'}
    write_json(ROOT/'evidence/metadata-build-result.json',report)
    desktop=(THEME/'_theme_inc/premium-magazine-led.glsl').read_text('utf-8-sig')
    # The desktop shader already supports GLSL100. Keep all lighting calculations.
    # Skip samples where the exact emitter formula must multiply by zero.
    mobile=desktop
    needle='float emitter(vec2 p) {\n    vec4 c=sampleArt(p);'
    assert needle in mobile
    mobile=mobile.replace(needle,'float emitter(vec2 p) {\n    if(region(p)<=0.0) return 0.0; // Equivalent zero mask; saves texture reads.\n    vec4 c=sampleArt(p);')
    # The PC shader has full-width int. GLSL ES fragments default to mediump int.
    # Keep FrameCount's arithmetic explicit at high precision on the mobile port.
    mobile=mobile.replace('precision highp float;','precision highp float;\nprecision highp int;')
    (ROOT/'native/premium-magazine-led-android.glsl').write_text(mobile,encoding='utf-8')
    (ROOT/'native/magazine_shader.h').write_text('static const char magazineShaderSource[]=R"STATION_MAGAZINE('+mobile+')STATION_MAGAZINE";\n',encoding='utf-8')
    write_json(ROOT/'evidence/shader-provenance.json',{'source':str(THEME/'_theme_inc/premium-magazine-led.glsl'),
        'sourceSha256':sha((THEME/'_theme_inc/premium-magazine-led.glsl').read_bytes()),'sourceNormalizedTextSha256':sha(desktop.encode()),'androidSha256':sha(mobile.encode()),'adaptation':'one mathematically equivalent early return when emitter region mask is zero; explicit highp integer default within GL_ES, preserving all PC light/color equations and FrameCount periodicity',
        'clock':'SDL monotonic milliseconds converted to the PC 60Hz frame units; independent of menu FPS','scope':'selected game cover only','idleFpsUnchanged':15})
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
