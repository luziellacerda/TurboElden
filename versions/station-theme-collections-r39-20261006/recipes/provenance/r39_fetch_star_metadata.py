from pathlib import Path
import urllib.request,zipfile,io,re,json,hashlib
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006')
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://lottiefiles.com/'}),timeout=50).read()
u='https://lottiefiles.com/pt/free-animation/stars-G6SjCsY2cp';page=get(u).decode('utf8');(W/'evidence/lottie-star-page.html').write_text(page,'utf8')
urls=sorted(set(re.findall(r'https://assets-v2\.lottiefiles\.com/a/[^"\\\s<>]+\.lottie',page)));assert len(urls)==1,urls
raw=get(urls[0]);(W/'assets/stars.lottie').write_bytes(raw);z=zipfile.ZipFile(io.BytesIO(raw));name=next(n for n in z.namelist() if n.startswith('animations/') and n.endswith('.json'));j=json.loads(z.read(name));(W/'assets/stars.json').write_bytes(z.read(name))
print('Star',urls[0],{k:j.get(k) for k in ['fr','ip','op','w','h','nm']},'layers',[(l.get('nm'),l.get('ty')) for l in j['layers']],flush=True)
title=re.search(r'<meta property="og:title" content="([^"]+)"',page);print('credit',title.group(1) if title else '')
(W/'evidence/lottie-star-source.json').write_text(json.dumps({'page':u,'asset':urls[0],'credit':title.group(1) if title else '', 'sha256':hashlib.sha256(z.read(name)).hexdigest()},indent=2),'utf8')
target=Path(r'G:\BAKUP SISTEMA APP 03-10-2026\metadata-publica-20261006');target.mkdir(exist_ok=True)
u='https://gamesdb.launchbox-app.com/Metadata.zip';r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'TurboStationsMetadataPreparation/1.0'}),timeout=60)
print('Public metadata download bytes',r.headers.get('Content-Length'),flush=True)
out=target/'Metadata.zip';assert not out.exists();total=0;nextmark=100*1024*1024
with out.open('wb') as f:
 while b:=r.read(1024*1024):
  f.write(b);total+=len(b)
  if total>=nextmark:print('Downloaded MB',round(total/1024/1024),flush=True);nextmark+=100*1024*1024
with zipfile.ZipFile(out) as z:print('Metadata archive',[(i.filename,i.file_size) for i in z.infolist()],flush=True)
(target/'source.json').write_text(json.dumps({'url':u,'bytes':total,'sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},indent=2),'utf8')
