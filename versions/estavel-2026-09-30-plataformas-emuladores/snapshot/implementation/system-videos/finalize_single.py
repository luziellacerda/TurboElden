from pathlib import Path
import json
P=Path(__file__).resolve().parent.parent;R=P/'system-videos'
b=json.loads((R/'build-result.json').read_text(encoding='utf-8'));i=json.loads((R/'installed.json').read_text(encoding='utf-8'))
assert b['installed'] and b['sha256']==i['sha256'] and b['apk'].endswith('TurboramaStation-videos-720-unico.apk')
status=f'''# Estado atual — vídeo único 720p, velocidade normal, cores do usuário

Instalação confirmada em {i['time']}; Success e hash do APK no aparelho conferido.
APK: {b['apk']}
SHA256: {b['sha256']}

Somente um vídeo 720p por célula. Loop nativo do Android, velocidade 1.0, pitch 1.0. Arquivos convertidos a 60fps preservando a duração e velocidade originais; quadros repetidos quando a fonte tem taxa inferior. Não afirmar 60fps sustentados nem movimento novo.

O atlas, a versão leve, a camada duplicada e a implementação manual de EOF/timestamps foram retirados do APK. MediaPlayer prepara de forma assíncrona e controla a repetição do mesmo arquivo. Apenas clipes visíveis ficam ativos; liberados ao sair, entrar nos jogos ou abrir modal. Diagnóstico anterior mostrou duas reproduções ativas; não reintroduzir essa arquitetura rejeitada.

Usar EXCLUSIVAMENTE os vídeos de G:\\TURBORAMA\\RetroBat\\emulationstation\\.emulationstation\\themes\\TURBORAMAx\\_theme_inc\\images\\caratulas. Foram encontrados 27 vídeos aplicáveis / 32 chaves, 29 das 36 plataformas ativas. Ausentes: Atari7800, Game Gear, Game Boy Color, Jaguar, PC Engine, PC Engine CD e SuperGrafx; sufami também está sem arquivo no mapa ampliado, mas não na lista ativa de 36. Não há fotos animadas ou vídeos de outra pasta no APK. A resposta "SIM" do usuário não forneceu os arquivos faltantes; isso permanece pendente. Manter os sistemas no catálogo, sem inventar vídeos.

LED conforme ordem explícita: PSP azul; Switch azul/vermelho; Wii branco; Atari marrom; Atomiswave verde; CPS1 verde; CPS2 amarelo/azul; CPS3 azul; Dreamcast laranja; GBA roxo; MAME/Arcade azul; Master System vermelho; Nintendo64 amarelo; NDS branco. Outros mantêm cores do tema. Fonte da regra: laser-user-overrides.json. Duas cores são aplicadas no contorno esquerdo/direito, sem trocar o vídeo.

Motores/DEX originais/login/ícone idênticos à base estável congelada. Jogos, saves, configurações e nave preservados. Sem novo teste visual, de loop ou benchmark no aparelho após esta correção; compilar/instalar não prova esses resultados.

Fontes: E:\\ESTUDO APK\\work\\native-carousel\\implementation.
Preparar vídeos: system-videos/prepare_720.py (restringe à pasta indicada).
Gerar cores: prepare_laser.py (aplica overrides do usuário).
Compilar: build_native.py; empacotar: system-videos/build_videos.py.
Instalar: system-videos/install_videos.py, recusa emulação ativa.
Detalhes: system-videos/CORRECAO-VIDEO-UNICO.md e CORES-SOLICITADAS.md.
Registros: system-videos/build-result.json e installed.json.

Git estável intocado: TurboElden, commit 95d244bcea95647236bea335c41b46afe15674bf, tag estavel-2026-09-29-camera-traseira; motor 1.0.8/6727ab7. APK de retorno privado em E:\\ESTUDO APK\\estaveis\\2026-09-29-camera-traseira. Esta correção não foi publicada ou promovida a estável. Revisão duplicada rejeitada preservada em system-videos/revisions/720-dual-rejected.

O backup criptografado anterior ainda é pré-vídeos; seu gerador foi atualizado com novos fontes/paleta, mas não foi executado novamente.
'''
for name in ['ESTADO-EM-ANDAMENTO.md','PLANO-ATUAL.md','README.md']:
 p=R/name;s=p.read_text(encoding='utf-8') if p.exists() else '';p.write_text(status+('\n## Histórico substituído\n\n'+s if name=='README.md' else ''),encoding='utf-8')
p=P/'stable-design/active-profile.json';v=json.loads(p.read_text(encoding='utf-8'));v.update(installed_apk=b['apk'],installed_apk_sha256=b['sha256'],build=str(R/'build-result.json'),installation_record=str(R/'installed.json'),installation_pending=False,active_visual_update='Only one 720p video per card, native 1x looping; no atlas; exact owner LED palette; strict source directory',requested_video_quality=b['requested_video_quality'],missing_platform_videos=b['missing_videos'],current_revision_promoted_to_stable=False);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in [P/'AGENTS.md',P.parent/'HANDOFF-IMPLEMENTACAO-CARROSSEL-NATIVO.md']:
 s=p.read_text(encoding='utf-8');p.write_text(status+'\n## Histórico anterior\n\n'+s,encoding='utf-8')
p=P/'brand-login/README.md';s=p.read_text(encoding='utf-8');p.write_text('# Saída atual\n\nTurboramaStation-videos-720-unico.apk. Ver ../system-videos/README.md; estados abaixo são históricos.\n\n'+s,encoding='utf-8')
for name in ['videos-unsigned.apk','videos-aligned.apk']:
 f=R/name;assert f.resolve().parent==R.resolve()
 if f.exists():f.unlink()
print('Installed single-video revision recorded; requested palette saved; missing files explicitly documented.')
