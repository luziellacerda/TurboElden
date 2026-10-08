"""Cross every revision-19 catalog row, retaining uncertainty and exact item identity.

No app assets, APK, production catalog or admission profiles are changed.
Source-backed descriptions never authorize online seats.
"""
from pathlib import Path, PurePosixPath
import collections,hashlib,html,json,re

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-player-audit-20261008')
CAT=REPO/'docs/server/recovery-r79-20261008/CATALOGO-REV19.json'
META=REPO/'versions/station-multiplayer-r77-20261008/catalog/catalog-game-metadata.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def maximum(value):
    # A trailing plus is a lower bound, not an exact maximum.
    if not isinstance(value,str):return None
    m=re.fullmatch(r'([1-9][0-9]?)(?:-([1-9][0-9]?))?',value.strip())
    if not m:return None
    lo=int(m[1]);hi=int(m[2] or m[1]);return hi if lo<=hi<=16 else None
def group(value):return str(value) if value in (1,2,3,4) else '5+' if value and value>4 else 'pendente'
def main():
    catalog=read(CAT);old=read(META);fb=read(WORK/'fbneo-players.json');review=read(HERE/'manual-review.json')
    prior={r['itemId']:r for r in old['records']};manual={r['itemId']:r for r in review['records']}
    driver=collections.defaultdict(list)
    for r in fb['records']:driver[r['driver']].append(r)
    rows=[];used_sources={};used_drivers=[];used_dat={}
    for item in catalog['items']:
        ident=item['itemId'];artifact=item['artifact'];visible=item.get('catalogVisible',True)
        raw=item.get('metadata',{}).get('players','');catmax=maximum(raw)
        evidence=[];manualrow=None
        historical=prior.get(ident)
        if historical and historical['artifactSha256']==artifact['sha256'] and historical['platform']==item['platform']:
            p=historical['fields']['playersMaximumDescriptive']
            if isinstance(p['value'],int) and 1<=p['value']<=16 and historical['editionMatch']=='exact-edition-and-size-candidate':
                refs=[]
                for ref in p['sourceRefs']:
                    source=old['sources'][ref['sourceId']];used_dat[ref['sourceId']]=source
                    refs.append({'label':'Libretro DAT · linha '+str(ref['line']),'url':source['url'],'sourceSHA256':source['sha256'],'line':ref['line']})
                evidence.append({'kind':'libretro-dat','maximum':p['value'],'binding':'mesmo itemId/plataforma/SHA do artefato; edição e tamanho exatos na pesquisa DAT; conteúdo não lido','sources':refs})
        if item['platform'] in ('neogeo','fbneo','cps1','cps2','cps3'):
            short=PurePosixPath(artifact.get('launchPath','').replace('\\','/')).stem
            candidates=driver.get(short,[]);counts={r['players'] for r in candidates}
            if len(counts)==1:
                refs=[]
                for d in candidates:
                    source=fb['sources'][d['source']];used_sources[d['source']]=source;used_drivers.append(d)
                    refs.append({'label':'FinalBurn Neo · '+d['driver'],'url':source['url']+'#L'+str(d['line']),'sourceSHA256':source['sha256'],'line':d['line']})
                evidence.append({'kind':'fbneo-driver','maximum':next(iter(counts)),'binding':'nome exato do driver no arquivo ZIP; conjunto de ROMs e DIP/mode não verificados','sources':refs})
        m=manual.get(ident)
        if m and m['artifactSHA256']==artifact['sha256'] and m['platform']==item['platform']:
            manualrow=m
            evidence.append({'kind':'original-manual-or-publisher','maximum':m['maximum'],'binding':m['binding'],'sources':[review['sources'][s] for s in m['sourceIds']]})
        values={e['maximum'] for e in evidence};cross_values=set(values)
        if catmax:cross_values.add(catmax)
        conflict=len(cross_values)>1
        if manualrow:
            best=manualrow['maximum'];status='manual';basis='Manual/editora: capacidade do jogo original';mode=manualrow['modeSummary']
        elif conflict:
            best=None;status='divergente';basis='Fontes discordam; máximo não escolhido automaticamente';mode='Simultâneo/alternado a conferir'
        elif evidence and catmax:
            best=catmax;status='concordante';basis='Catálogo e base técnica concordam no máximo';mode='Simultâneo/alternado a conferir'
        elif evidence:
            best=next(iter(values));status='fonte-tecnica';basis='Máximo da base técnica; catálogo sem número exato';mode='Simultâneo/alternado a conferir'
        elif catmax:
            best=catmax;status='catalogo';basis='Somente declarado no catálogo; falta cruzamento independente';mode='Simultâneo/alternado a conferir'
        else:
            best=None;status='sem-dado';basis='Sem máximo exato confirmado nas fontes cruzadas';mode='A conferir'
        rows.append({'itemId':ident,'name':item['name'],'platform':item['platform'],'visible':visible,'folderPath':item.get('folderPath',[]),'itemRevision':item['revision'],
            'artifactSHA256':artifact['sha256'],'launchPath':artifact.get('launchPath',''),'catalogPlayers':raw,'catalogMaximum':catmax,
            'externalMaxima':sorted(values),'maximumForList':best,'group':group(best),'status':status,'basis':basis,'modeSummary':mode,
            'manualModes':manualrow.get('modes',[]) if manualrow else [],'conflict':conflict,'evidence':evidence,
            'onlineAdmission':'not-evaluated-by-this-audit; requires current signed exact profile; no seats granted'})
    rows.sort(key=lambda r:(r['platform'],r['name'].casefold(),r['itemId']))
    visible=[r for r in rows if r['visible']]
    counts=collections.Counter(r['status'] for r in visible);groups=collections.Counter(r['group'] for r in visible)
    summary={'catalogRevision':catalog['revision'],'catalogExportUTC':catalog['indexExportUtc'],'rows':len(rows),'visibleRows':len(visible),'compatibilityRows':len(rows)-len(visible),
      'groupsByMaximum':dict(groups),'statusCounts':dict(counts),'platforms':dict(collections.Counter(r['platform'] for r in visible)),
      'crossedWithExternalSource':sum(bool(r['evidence']) for r in visible),'conflictingVisibleRows':sum(r['conflict'] for r in visible),
      'allRowsAccountedFor':len(rows)==catalog['itemCount'] and len({r['itemId'] for r in rows})==len(rows),'allModesVerified':False,'onlineSeatsAuthorized':0,
      'inputs':{'catalog':sha(CAT),'historicalDatResearch':sha(META),'fbneoExtract':sha(WORK/'fbneo-players.json'),'manualReview':sha(HERE/'manual-review.json')},
      'limits':['Export integral revisão19, não nova consulta autenticada ao telefone/servidor.','Um máximo 4 não prova que o modo aceita exatamente 3, nem que é simultâneo.','Concordância de bancos não substitui manual ou prova de edição/modo.','Contagem original pode superar o limite de quatro do app.','Traduções/hacks não herdam homologação online do jogo original.']}
    dump(HERE/'catalogo-cruzado.json',{'schemaVersion':1,'summary':summary,'records':rows})
    dump(HERE/'resumo.json',summary)
    dump(HERE/'fontes-cruzadas.json',{'libretro':{'commit':old['sourceCommit'],'sources':used_dat,'metadataLicense':old['metadataLicense']},
         'fbneo':{'commit':fb['commit'],'sources':used_sources,'matchedDrivers':list({r['driver']+r['source']:r for r in used_drivers}.values())},'manuals':review['sources']})
    dump(HERE/'divergencias.json',{'records':[r for r in rows if r['visible'] and r['conflict']]})
    lines=['JOGADORES POR JOGO — CATÁLOGO REVISÃO 19','Máximo descritivo; as condições por modo ficam ao lado. Não é lista de salas liberadas.',
           'Legenda: manual = capacidade original documentada; concordante = catálogo/base técnica; fonte-tecnica = base técnica; catalogo = falta fonte independente.',
           'Não converter máximos em vagas simultâneas automaticamente.','']
    for g in ['1','2','3','4','5+','pendente']:
        entries=[r for r in visible if r['group']==g];lines+=['=== '+g.upper()+' — '+str(len(entries))+' registros ===']
        for r in entries:lines.append(f"{r['platform']} | {r['name']} | máximo {r['maximumForList'] or '?'} | {r['status']} | {r['modeSummary']} | {r['itemId']}")
        lines.append('')
    (HERE/'lista-jogadores.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')
    template=(HERE/'report-template.html').read_text(encoding='utf8')
    payload=json.dumps({'summary':summary,'records':rows},ensure_ascii=False).replace('<','\\u003c').replace('&','\\u0026')
    (HERE/'jogadores.html').write_text(template.replace('__AUDIT_DATA__',payload),encoding='utf8')
    assert summary['allRowsAccountedFor'] and len(visible)==catalog['visibleCount']
    assert all(r['maximumForList'] is None for r in rows if r['status']=='divergente')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
