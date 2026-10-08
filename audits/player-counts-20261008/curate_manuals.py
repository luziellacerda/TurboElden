"""Human-reviewed original manuals/publisher facts, explicitly not online approvals."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
catalog=json.loads((REPO/'docs/server/recovery-r79-20261008/CATALOGO-REV19.json').read_text(encoding='utf8'))
items={x['itemId']:x for x in catalog['items']}
sources={
 'sb2':{'label':'Hudson · manual Super Bomberman 2 (USA), Playing a Battle Game, pp. 8–9','url':'https://www.videogamemanual.com/snes/Super%20Bomberman%202%20(USA).pdf','kind':'original-publisher-manual-third-party-archive'},
 'sb3':{'label':'Hudson · manual Super Bomberman 3 (Europe), pp. 5, 8–9','url':'https://www.retrogames.cz/manualy/SNES/Super_Bomberman_3_-_SNES_-_Manual.pdf','kind':'original-publisher-manual-third-party-archive'},
 'hero':{'label':'Nintendo · Bomberman Hero, campo Players: 1','url':'https://www.nintendo.com/en-gb/Games/Nintendo-64/Bomberman-Hero-276445.html','kind':'official-publisher-product-page'},
 'dc':{'label':'Sega · manual Bomberman Online, pp. 4, 14–16','url':'https://www.digitpress.com/library/manuals/dreamcast/bomberman_online.pdf','kind':'original-publisher-manual-third-party-archive'},
 'mana':{'label':'Nintendo · manual Secret of Mana, seção 12, PDF p. 15','url':'https://www.nintendo.com/es-es/games/oms/snes-classic/manuals/secret-of-mana/manual.pdf','kind':'official-publisher-hosted-manual'},
 'vikings':{'label':'Interplay · manual The Lost Vikings (Genesis), seção Two or Three Player Game, p. 16','url':'https://manualzz.com/doc/22466256/sega-genesis--the-lost-vikings-video-game-instruction-manual','kind':'original-publisher-manual-transcription-third-party-archive'},
 'mega':{'label':'Sega · manual Mega Bomberman (EU), seleção de modo, pp. 18–19','url':'https://www.scribd.com/document/695933057/Mega-Bomberman-MD-EU-cart-Manual','kind':'original-publisher-manual-transcription-third-party-archive'},
 'battletoads':{'label':'Tradewest · manual Battletoads in Battlemaniacs, Controlling the Action, p. 6','url':'https://www.retrogames.cz/manualy/SNES/Battletoads_in_Battlemaniacs_-_SNES_-_Manual.pdf','kind':'original-publisher-manual-third-party-archive'}
}
rows=[]
def mode(name,style,counts,condition=''):
 return {'name':name,'style':style,'humanCountsDocumentedForOriginal':counts,'condition':condition}
def add(ident,expected_name,source,maximum,summary,modes,variant='Edição declarada pelo catálogo; conteúdo do aparelho e funcionamento online não verificados.'):
 item=items[ident];assert item['name']==expected_name
 rows.append({'itemId':ident,'name':expected_name,'platform':item['platform'],'artifactSHA256':item['artifact']['sha256'],'itemRevision':item['revision'],
  'maximum':maximum,'maximumScope':'original-game-local-play','modeSummary':summary,'modes':modes,'sourceIds':[source],
  'binding':variant,'onlineApproved':False,'deviceGameplayVerified':False})
add('station_df50d575815ab105084a79d68e0c8fb3','Super Bomberman 2','sb2',4,'Campanha: 1. Batalha: até 4 simultâneos; Multitap para 3–4.',[mode('Normal Game','single-player',[1]),mode('Battle / Single Match','simultaneous',[1,2,3,4],'Slots MAN/COM/OFF; Multitap para 3–4 humanos.')])
add('station_46fe7356ab5cc63a1438f720b9c7ce2d','Super Bomberman 3','sb3',5,'Campanha: 1–2. Batalha: até 5 simultâneos; Multitap acima de 2. Quatro é subconjunto, não máximo original.',[mode('Normal Game','simultaneous',[1,2]),mode('Battle / Single Match','simultaneous',[1,2,3,4,5],'Multitap acima de 2; selecionar slots humanos no jogo.')])
add('station_3f28d41c9e666e0080106eda728e89da','Bomberman Hero','hero',1,'Individual: 1 jogador.',[mode('Adventure','single-player',[1])])
add('station_3f0267d082d3d99218768e6f4088960b','Bomberman Online','dc',4,'Campanha: 1. Batalha local: até 4. O antigo modo de rede é separado.',[mode('Normal Game','single-player',[1]),mode('Battle Game local','simultaneous',[1,2,3,4],'Um controle por humano; não é comprovação do antigo serviço de rede nem do netplay do app.')])
add('cbd83be3e89456758ad7c165907abd12','The Lost Vikings','vikings',3,'Mega Drive: até 3 cooperativos; Sega Team Player para o terceiro. Não transferir a regra para SNES.',[mode('Cooperativo','simultaneous',[1,2,3],'3 exige Sega Team Player; configurar OPTIONS / PLAYER.')])
add('9e5a873d6b384b8277568b297d3b8030','Mega Bomberman','mega',4,'Campanha: 1. Batalha: até 4; adaptador/controles precisam ser configurados.',[mode('Normal Game','single-player',[1]),mode('Battle Game / Normal','simultaneous',[1,2,3,4])], 'Manual europeu descreve o original Mega Drive; catálogo declara edição USA. Divergências regionais e conteúdo exato ainda não qualificados.')
add('station_7da80d23885a72cc56464834711b85a5','Secret of Mana','mana',3,'Original SNES: até 3 cooperativos, após entrada dos aliados. Variante PT-BR não homologada.',[mode('Aventura cooperativa','simultaneous',[1,2,3],'Jogadores adicionais dependem dos aliados já disponíveis e Multitap.')], 'Referência do original SNES; variante snesbr/header/tradução do catálogo não verificada por gameplay.')
for ident,name in [('826da6daebe9edbebffb3721f83abf12','Battletoads in Battlemaniacs (USA)'),('station_f1d9d06767f9a63592011424048bd181','Battletoads in Battlemaniacs')]:
 add(ident,name,'battletoads',2,'Original SNES: 1 ou 2; modo A/B muda o dano entre parceiros. Tradução não homologada.',[mode('Individual','single-player',[1]),mode('2 Players A/B','simultaneous',[2],'A/B altera fogo amigo, não adiciona terceiro jogador.')], 'Referência do original; o artefato é tradução/header ou diverge da região do título. Não é qualificação de bytes.')
add('station_80b7594ba22922d87fb43d720ba8be5a','Super Bomberman 2 (PT-BR)','sb2',4,'Original: campanha 1; batalha até 4. Tradução PT-BR não homologada.',[mode('Normal Game','single-player',[1]),mode('Battle / Single Match','simultaneous',[1,2,3,4],'Original usa Multitap para 3–4; tradução ainda requer conferência.')], 'Referência do original USA; tradução PT-BR do catálogo não testada. Não é evidência de conteúdo exato.')
(HERE/'manual-review.json').write_text(json.dumps({'schemaVersion':1,'reviewDate':'2026-10-08','sources':sources,'records':rows,'scope':'original-game-descriptive-facts; never online authorization'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
