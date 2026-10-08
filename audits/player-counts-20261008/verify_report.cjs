// Exercise report filters/pagination using a tiny DOM; not a visual browser test.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const page=fs.readFileSync(__dirname+'/jogadores.html','utf8');
const data=page.match(/<script type="application\/json" id="data">([\s\S]*?)<\/script>/)[1];
const js=page.match(/<\/script><script>([\s\S]*?)<\/script>/)[1];
class Element{constructor(){this.children=[];this.value='';this.checked=false;this.dataset={};this.textContent='';this.listeners={};}append(...v){this.children.push(...v)}replaceChildren(...v){this.children=v}setAttribute(k,v){this[k]=v}addEventListener(k,v){this.listeners[k]=v}}
const els={};const get=id=>els[id]??(els[id]=new Element());get('data').textContent=data;
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>get('groups').children},Option:function(t,v){const e=new Element();e.textContent=t;e.value=v;return e;}});
vm.runInContext(js,context);let checks=0;function check(c){checks++;assert(c)}
check(get('rows').children.length===75);check(get('counter').textContent.startsWith('3.479'));
for(const b of get('groups').children){b.onclick();check(b['aria-pressed']==='true');check(get('rows').children.length<=75)}
get('reset').onclick();get('q').value='Super Bomberman 3';get('q').listeners.input();check(get('rows').children.length===1);check(get('rows').children[0].children[1].children[0].textContent===5);
get('reset').onclick();get('four').checked=true;get('four').listeners.change();check(get('rows').children.some(tr=>tr.children[0].children[0].textContent==='Super Bomberman 3'));
get('reset').onclick();get('quality').value='any-conflict';get('quality').listeners.change();check(get('counter').textContent.startsWith('141'));
get('reset').onclick();get('next').onclick();check(get('page').textContent.startsWith('Página 2'));get('prev').onclick();check(get('page').textContent.startsWith('Página 1'));
get('compat').checked=true;get('compat').listeners.change();check(get('counter').textContent.startsWith('3.734'));
get('q').value='no-such-game-000';get('q').listeners.input();check(get('rows').children.length===0&&get('prev').disabled&&get('next').disabled);
fs.writeFileSync(__dirname+'/report-verification.json',JSON.stringify({checks,passed:checks,scope:'DOM simulation; filters, search, empty state, pagination; not a visual browser test'},null,2)+'\n');console.log(JSON.stringify({checks,passed:checks}));
