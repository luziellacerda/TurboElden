from pathlib import Path
import subprocess,csv,io,json,collections,hashlib
W=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005')
repo=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
commit='100e4bbd92aa4c85cda10a633e6463fbb24ae8ab'
path='docs/station-android/biblioteca-neogeocd-20261005/catalogo-completo.tsv'
raw=subprocess.check_output(['git','-c','safe.directory='+repo.as_posix(),'-C',str(repo),'show',commit+':'+path])
rows=list(csv.DictReader(io.StringIO(raw.decode('utf8')),delimiter='\t'))
counts=collections.Counter('/'.join(json.loads(x['folderPath'])) for x in rows if x['platform']=='neogeo' and x['catalogVisible']=='yes')
record={'source':'server-published-catalog-tsv','platform':'neogeo','commit':commit,'path':path,
        'sourceSHA256':hashlib.sha256(raw).hexdigest(),'serverDeclaredCatalogRevision':14,
        'url':'https://github.com/luziellacerda/Servidor-pix/blob/'+commit+'/'+path,
        'folders':[{'folderPath':p,'count':n} for p,n in sorted(counts.items())],
        'visibleItems':sum(counts.values()),'deviceObserved':False}
(W/'evidence/catalog-folders.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
print(json.dumps(record))
