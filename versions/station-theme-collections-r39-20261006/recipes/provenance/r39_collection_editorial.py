from pathlib import Path
import csv,json,collections,hashlib
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native'
source=Path(r'work\TurboElden-git\versions\station-final-details-r37-20261005\data\synopses-catalog-14.tsv')
texts={
'BOMBER MAN':'''Uma arena cheia de passagens, obstáculos e explosões transforma cada movimento em uma pequena decisão. A coleção Super Bomberman reúne desafios em que abrir caminho não basta: é preciso calcular o tempo da bomba, observar as rotas livres e evitar ficar preso na própria estratégia. O desenho claro dos labirintos ajuda a acompanhar a ação, mesmo quando o espaço fica mais apertado.

Os jogos desta seleção convidam a aprender pela tentativa e pela leitura do cenário. Uma abertura pode criar uma fuga ou deixar o personagem exposto; um item muda o alcance das explosões e exige atenção renovada. Entre fases e arenas, a graça está em perceber como regras simples produzem situações diferentes. Consulte a ficha de cada título para conhecer a edição e a quantidade de jogadores antes de começar.''',
'DONKEY KONG':'''Selvas, minas, trilhos e passagens escondidas dão ritmo à coleção Donkey Kong Country. A seleção reúne as três aventuras de Super Nintendo presentes nesta pasta, com protagonistas, cenários e desafios que mudam ao longo da série. Saltar com precisão, observar os movimentos dos inimigos e explorar além do caminho mais evidente faz parte da descoberta.

A apresentação dos personagens e a música ajudam cada ambiente a ganhar personalidade. Há trechos que pedem velocidade e outros em que vale diminuir o passo para procurar segredos. Em vez de repetir sempre o mesmo percurso, os jogos alternam situações e convidam a aprender novas maneiras de atravessar as fases. É uma coleção para revisitar lembranças, descobrir detalhes esquecidos e acompanhar como a série desenvolve suas ideias de uma aventura para a seguinte.''',
'FINAL FIGHT':'''Ruas tomadas por adversários, combates próximos e avanços de tela em tela definem a seleção Final Fight. Os três títulos reunidos nesta pasta colocam o jogador diante de grupos que tentam cercar o personagem, fazendo da posição no cenário uma parte importante da luta. Escolher quando avançar, recuar ou interromper um ataque ajuda a controlar o ritmo da partida.

Cada jogo apresenta sua combinação de lutadores, golpes e ambientes. O prazer da descoberta está tanto em aprender os comandos quanto em reconhecer os tipos de inimigo e evitar ficar sem espaço. A coleção permite acompanhar diferentes interpretações da briga de rua no Super Nintendo. As opções de personagens e de participantes variam entre as edições: a ficha do jogo escolhido traz as informações para preparar a sessão.''',
'MEGA MAN':'''A coleção Mega Man aproxima duas maneiras de explorar o universo do herói: as fases de ação e plataforma de Mega Man 7 e da série X, e a proposta esportiva de Mega Man Soccer. O conjunto evidencia como personagens e ideias podem ganhar outros ritmos, mantendo uma identidade visual fácil de reconhecer.

Nas aventuras de ação, observar o cenário, ajustar os saltos e aprender o comportamento dos chefes faz parte da progressão. Cada encontro convida a testar uma abordagem e a usar melhor os recursos disponíveis. Já a presença de Soccer oferece uma mudança de perspectiva dentro da mesma seleção. Abra as fichas para comparar cada título, conhecer seus objetivos e escolher entre uma jornada de precisão nas fases ou uma experiência de futebol com os personagens da série.''',
'SUPER MARIO':'''O universo de Mario aparece nesta coleção em mais de um formato. Ao lado das aventuras de plataforma, o catálogo desta pasta inclui corridas, RPG e experiências educativas. Essa variedade permite escolher uma sessão de reflexos e exploração, uma disputa nas pistas ou uma proposta com outro ritmo, sem tratar todos os jogos como se fossem a mesma aventura.

Personagens conhecidos, cores expressivas e cenários cheios de detalhes conectam experiências bastante diferentes. Nas plataformas, a curiosidade leva a novos caminhos; nos outros estilos, os objetivos e comandos seguem as regras de cada título. Percorra as capas e leia as sinopses para descobrir o que distingue cada edição. A coleção funciona como uma porta de entrada para diferentes lados do universo de Mario no Super Nintendo, dos jogos familiares às propostas menos lembradas.''',
'TOP GEAR':'''Top Gear, Top Gear 2 e Top Gear 3000 formam uma seleção dedicada à velocidade. A pista ocupa o centro da atenção: curvas, adversários e mudanças no traçado pedem respostas rápidas e uma leitura constante do que está adiante. O desafio vai além de manter a aceleração; encontrar o momento de ultrapassar e conservar uma boa trajetória pode mudar o resultado.

A coleção permite comparar a apresentação, o ritmo e as propostas de cada jogo. Música, paisagens e sensação de movimento fazem parte da personalidade das corridas, enquanto a prática ajuda a reconhecer trechos e melhorar a pilotagem. Escolha uma edição pela sua ficha e descubra as pistas, os modos e as regras que ela oferece. É um convite para retornar a uma corrida conhecida ou aprender um percurso novo, buscando uma chegada melhor a cada tentativa.''',
'ART OF FIGTHERS':'''A seleção Art of Fighting coloca em destaque confrontos de luta em que distância, defesa e tempo de resposta precisam trabalhar juntos. Os títulos presentes nesta pasta permitem conhecer diferentes momentos da série, observando a apresentação dos personagens e o modo como cada combate ganha intensidade.

Aprender um lutador envolve mais do que decorar uma sequência: reconhecer o alcance dos golpes e os intervalos entre ataques ajuda a decidir quando pressionar ou esperar. A coleção oferece um ponto de partida para comparar essas escolhas nas edições disponíveis. Leia a ficha de cada jogo para identificar a versão selecionada e preparar os comandos. A satisfação vem de perceber a evolução entre uma tentativa e outra, transformando movimentos antes difíceis em decisões conscientes durante a luta.''',
'METAL SLUG':'''Ação lateral, veículos e cenários cheios de acontecimentos dão identidade à coleção Metal Slug. As edições reunidas nesta pasta alternam deslocamento, saltos e disparos, com atenção constante ao que chega de diferentes lados da tela. As animações e os detalhes dos ambientes ajudam a contar pequenas histórias mesmo no meio do combate.

O ritmo muda entre avançar rapidamente e encontrar uma posição segura para enfrentar o próximo obstáculo. Aprender os padrões dos inimigos e aproveitar os recursos de cada trecho torna as novas tentativas mais consistentes. A lista contém edições e variantes identificadas pelos próprios nomes do catálogo; confira a ficha antes de escolher. Assim é possível revisitar uma missão familiar ou conhecer outra versão sem perder a referência do título que está sendo aberto.''',
'SAMURAI SHODOWN':'''A coleção Samurai Shodown reúne duelos em que o espaço entre os combatentes merece atenção. O alcance das armas, o momento da aproximação e a escolha de quando atacar dão às lutas um ritmo próprio. Observar a postura do adversário pode ser tão importante quanto executar um comando com rapidez.

As edições disponíveis permitem acompanhar mudanças de personagens, apresentação e regras ao longo da série. Cada confronto convida a controlar a impaciência, estudar as aberturas e compreender o risco de um golpe mal calculado. As paisagens e a caracterização dos lutadores reforçam a atmosfera dos combates. Explore a ficha de cada jogo, escolha sua edição e descubra quais movimentos combinam com sua maneira de jogar, aperfeiçoando a leitura da luta a cada nova rodada.''',
'THE KING OF FIGTHERS':'''Esta pasta reúne jogos e variantes organizados no catálogo em torno de The King of Fighters, além de títulos relacionados presentes na seleção. Os nomes das edições ajudam a distinguir temporadas, versões e outros confrontos. A variedade de personagens e estilos faz de cada escolha uma oportunidade para experimentar um ritmo diferente de luta.

Aprender a alternar defesa e pressão, reconhecer o alcance dos ataques e aproveitar uma abertura são habilidades que atravessam esses jogos. As regras de equipe e os recursos disponíveis dependem da edição escolhida; a coleção não impõe um único formato a todos os títulos. Percorra as capas e consulte as fichas para encontrar a versão desejada. Depois, explore os personagens com calma e descubra combinações de movimentos que tornem suas decisões mais seguras durante a partida.''',
'FATAL FURY':'''Os confrontos de Fatal Fury ganham espaço nesta coleção com edições que apresentam diferentes momentos da série. Cada jogo traz sua leitura dos lutadores, das arenas e do ritmo do combate. O primeiro contato pode começar por um personagem conhecido, mas reconhecer os movimentos do oponente logo se torna parte essencial da disputa.

Posicionamento, defesa e oportunidade precisam funcionar juntos. Aproximar-se sem cuidado pode abrir espaço para um contra-ataque; esperar o instante certo permite aproveitar melhor os golpes. A seleção convida a comparar as regras e a apresentação de cada edição disponível, sem misturar suas particularidades. Leia a sinopse do título escolhido, conheça seus participantes e volte à arena para transformar observação e prática em uma forma própria de jogar.''',
'HACKS':'''Esta seleção reúne os arquivos que o catálogo organizou na pasta HACKS. Os nomes incluem variantes, identificações de conjuntos e um protótipo, ao lado de outros títulos publicados nesta categoria. A organização da pasta não significa que todos tenham a mesma alteração: cada entrada deve ser reconhecida pelo nome e pela edição informados na sua ficha.

Explorar a coleção é uma oportunidade para observar diferenças de apresentação, conteúdo e comportamento entre versões, quando elas existirem. Antes de começar, confira qual arquivo está selecionado e leia a sinopse correspondente. As regras, personagens e opções pertencem a cada jogo, e não ao nome geral da pasta. Essa atenção ajuda a reencontrar uma edição já conhecida ou experimentar outra mantendo uma referência clara do que está sendo jogado.''',
}
br='''Esta coleção reúne as edições que o catálogo organiza na categoria PT-BR. A seleção permite encontrar essas versões em um só lugar e comparar jogos de estilos diferentes, das aventuras de plataforma às lutas, corridas e jornadas de RPG. O idioma e a abrangência da adaptação devem ser observados em cada edição, sem presumir que todos os textos ou recursos foram alterados da mesma maneira.

Ler diálogos, objetivos e pistas com mais familiaridade pode mudar o ritmo de uma aventura e aproximar o jogador de detalhes antes deixados de lado. Ao percorrer a lista, confira o nome completo e a sinopse de cada título para reconhecer a versão que deseja abrir. A organização por coleção facilita voltar aos favoritos e descobrir outros jogos da mesma categoria, mantendo a identidade de cada edição publicada.'''
groups=collections.defaultdict(list)
for r in csv.DictReader(source.open(encoding='utf-8-sig',newline=''),delimiter='\t'):
 parts=json.loads(r['folderPath'])
 for i in range(1,len(parts)+1):groups[(r['platform'],'/'.join(parts[:i]))].append(r)
platforms={'snes':'Super Nintendo','snesbr':'Super Nintendo - BR','megadrivebr':'MegaDrive - BR','neogeo':'Neo Geo'}
entries=[]
for (platform,path),rs in sorted(groups.items()):
 matches=[text for key,text in texts.items() if key in path]
 if 'PT-BR' in path:matches=[br.replace('Esta coleção', 'A seleção de '+('Super Nintendo' if platform=='snesbr' else 'Mega Drive')+' em PT-BR',1)]
 assert len(matches)==1,(platform,path)
 entries.append(dict(platform=platforms[platform],serverPlatform=platform,path=path,text=matches[0],countSnapshot=len(rs),examples=[r['name'] for r in rs[:3]]))
q=lambda s:json.dumps(s,ensure_ascii=False)
(N/'collection_editorial.h').write_text('#pragma once\n// Original editorial grounded in catalog revision 14. Counts/examples are resolved live.\nstruct CollectionEditorial {const char*platform;const char*path;const char*text;};\nstatic const CollectionEditorial collectionEditorials[]={\n'+''.join('{'+','.join(q(e[k]) for k in ('platform','path','text'))+'},\n' for e in entries)+'};\n','utf8')
(W/'data/collection-editorial.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),'utf8')
(W/'data/collection-editorial-provenance.json').write_text(json.dumps({'source':str(source.resolve()),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'catalogRevision':14,'collections':len(entries),'method':'Original Portuguese collection editorial using exact folder membership and descriptions of its published games. No invented items, counts, ratings or online support. Dynamic fallback for future folders.'},indent=2),'utf8')
p=N/'system_infos.h';p.write_text('#pragma once\n'+p.read_text('utf8'),'utf8')
p=N/'collection_presentation.h';s=p.read_text('utf8');s=s[:s.index('static void collectionSynopsis(')]
s+='''#include "collection_editorial.h"
#include "system_infos.h"
static bool collectionKeyEqual(const char*a,const char*b){
 while(*a&&*b){char x=*a++,y=*b++;if(x>='A'&&x<='Z')x+=32;if(y>='A'&&y<='Z')y+=32;if(x!=y)return false;}
 while(*a==' ')a++;while(*b==' ')b++;return !*a&&!*b;
}
static const char*collectionEditorial(const char*platform,const char*path){
 for(const auto&e:collectionEditorials)if(collectionKeyEqual(platform,e.platform)&&collectionKeyEqual(path,e.path))return e.text;
 return nullptr;
}
static void collectionSynopsis(char*output,unsigned long size,const char*name,const char*platform,unsigned long count,int kind,const char*const*examples,unsigned exampleCount,const char*path=nullptr){
 CollectionText text(output,size);const char*editorial=kind==2?nullptr:collectionEditorial(platform,path?path:name);
 if(kind==2){
  text.append("Toda a biblioteca de ");text.append(platform);text.append(" em uma única seleção: ");text.number(count);text.append(count==1?" jogo disponível.":" jogos disponíveis.");
  text.append(" Aqui estão os títulos publicados na raiz e nas coleções da plataforma, reunidos para facilitar a descoberta e o retorno aos seus favoritos.\\n\\n");
  bool found=false;for(const auto&info:systemInfos)if(collectionKeyEqual(platform,info.key)){text.append(info.description);found=true;break;}
  if(!found)text.append("Explore as capas e as fichas para conhecer a proposta de cada jogo. Personagens, objetivos e estilos variam de um título para outro, permitindo escolher a próxima experiência pelo que desperta sua curiosidade.");
 }else{
  text.append(name);text.append(" — ");text.number(count);text.append(count==1?" jogo de ":" jogos de ");text.append(platform);text.append(".\\n\\n");
  if(editorial)text.append(editorial);
  else{
   text.append("Esta seleção reúne os títulos organizados em ");text.append(name);text.append(". Percorrer suas capas é uma maneira de reconhecer jogos familiares e encontrar outras propostas dentro da mesma coleção. Cada ficha apresenta a experiência e a edição daquele título, preservando as diferenças entre os jogos.\\n\\n");
   text.append(kind==1?"A lista apresenta os jogos diretamente nesta pasta. ":"A lista reúne esta seleção e suas subcoleções, quando houver. ");
   text.append("Vale comparar as sinopses, observar os objetivos e escolher o próximo jogo pelo tipo de desafio que procura. A seleção acompanha os títulos publicados no catálogo: novos itens aparecem na mesma organização, sem perder o nome da coleção.");
  }
 }
 if(exampleCount&&examples){text.append("\\n\\nNesta seleção: ");for(unsigned i=0;i<exampleCount;i++){if(i)text.append("; ");text.append(examples[i]);}text.append(".");}
 text.append("\\n\\nAbra a lista para pesquisar nesta seleção, consultar os detalhes, baixar um título ou continuar um jogo já instalado.");
}
'''
p.write_text(s,'utf8')
p=N/'native_folders.h';s=p.read_text('utf8');old='meta.kind,examples,count);';assert old in s;p.write_text(s.replace(old,'meta.kind,examples,count,path);'),'utf8')
p=N/'native_info.h';s=p.read_text('utf8');assert 'folderText[2048]' in s;p.write_text(s.replace('folderText[2048]','folderText[6144]'),'utf8')
print('Collection editorial:',len(entries),'exact paths; dynamic counts and future-folder fallback')
