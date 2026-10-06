const fs=require('fs');const path=require('path');
const {chromium}=require('C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root='E:/ESTUDO APK/work/station-theme-collections-r39-20261006';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',args:['--disable-background-networking']});
 try{
 const page=await browser.newPage({viewport:{width:160,height:160},deviceScaleFactor:1});
 await page.route('http://**/*',r=>r.abort());await page.route('https://**/*',r=>r.abort());
 await page.setContent('<html><style>html,body{margin:0;background:transparent}#lottie{width:160px;height:160px}</style><div id="lottie"></div></html>');
 await page.addScriptTag({path:path.join(root,'temp/lottie-render/lottie.min.js')});
 const data=JSON.parse(fs.readFileSync(path.join(root,'assets/online-robot.json'),'utf8'));
 await page.evaluate(data=>new Promise(resolve=>{window.anim=lottie.loadAnimation({container:document.getElementById('lottie'),renderer:'svg',loop:false,autoplay:false,animationData:data});anim.addEventListener('DOMLoaded',resolve);}),data);
 const output=path.join(root,'temp/lottie-render/online-robot-frames');fs.mkdirSync(output,{recursive:true});
 for(let f=0;f<242;f++){
  await page.evaluate(frame=>anim.goToAndStop(frame,true),f);
  await page.locator('#lottie').screenshot({path:path.join(output,`${f}.png`),omitBackground:true});
 }
 console.log('Rendered original online robot frames 0–241 at source 60 fps; local SVG, no network/autoplay.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
