from pathlib import Path
import urllib.request,zipfile,io,re,json,hashlib,shutil
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006')
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://lottiefiles.com/'}),timeout=50).read()
u='https://lottiefiles.com/free-animation/robot-playing-computer-LljdYvKKM4';page=get(u).decode('utf8');(W/'evidence/lottie-online-robot-page.html').write_text(page,'utf8')
urls=sorted(set(re.findall(r'https://assets-v2\.lottiefiles\.com/a/[^"\\\s<>]+\.lottie',page)));assert len(urls)==1,urls
raw=get(urls[0]);(W/'assets/online-robot.lottie').write_bytes(raw);z=zipfile.ZipFile(io.BytesIO(raw));name=next(n for n in z.namelist() if n.startswith('animations/') and n.endswith('.json'));j=json.loads(z.read(name));(W/'assets/online-robot.json').write_bytes(z.read(name))
title=re.search(r'<meta property="og:title" content="([^"]+)"',page);credit=title.group(1) if title else ''
record={'page':u,'asset':urls[0],'credit':credit,'sha256':hashlib.sha256(z.read(name)).hexdigest(),'source':{k:j.get(k) for k in ['fr','ip','op','w','h','nm']}}
(W/'evidence/lottie-online-robot-source.json').write_text(json.dumps(record,indent=2),'utf8');print(json.dumps(record,ensure_ascii=True,indent=2));print('layers',len(j['layers']));print('assets',len(j.get('assets',[])))
shutil.copy2(W/'assets/dark-mode-button-LICENSE.html',W/'assets/online-robot-LICENSE.html')
(W/'assets/online-robot-NOTICE.txt').write_text(credit+'\n'+u+'\nLottie Simple License: https://lottiefiles.com/page/license\nRendered from the original JSON with lottie-web 5.13.0 (MIT). No remote content in the Android button.\n','utf8')
