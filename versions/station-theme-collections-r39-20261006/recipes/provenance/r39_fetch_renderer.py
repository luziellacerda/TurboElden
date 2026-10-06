from pathlib import Path
import urllib.request,json,tarfile,io,hashlib
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');T=W/'temp/lottie-render';T.mkdir(exist_ok=True)
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read()
meta=json.loads(get('https://registry.npmjs.org/lottie-web/latest'));package=get(meta['dist']['tarball']);tar=tarfile.open(fileobj=io.BytesIO(package),mode='r:gz')
assert hashlib.sha1(package).hexdigest()==meta['dist']['shasum']
for src,dst in [('package/build/player/lottie.min.js','lottie.min.js'),('package/LICENSE.md','lottie-web-LICENSE.md')]:
 (T/dst).write_bytes(tar.extractfile(src).read())
(W/'assets/dark-mode-button-LICENSE.html').write_bytes(get('https://lottiefiles.com/page/license'))
(W/'assets/dark-mode-button-NOTICE.txt').write_text('Dark Mode Button — Mohammad\nhttps://lottiefiles.com/pt/free-animation/dark-mode-button-nrQ5WkuReW\nLottie Simple License: https://lottiefiles.com/page/license\nOriginal animation and native sampled presentation. Rendered with lottie-web '+meta['version']+' (MIT) at build time.\n','utf8')
(W/'evidence/lottie-renderer.json').write_text(json.dumps({'version':meta['version'],'tarball':meta['dist']['tarball'],'sha1':meta['dist']['shasum'],'runtimeInAPK':False},indent=2),'utf8')
print('Build-time Lottie renderer',meta['version'])
