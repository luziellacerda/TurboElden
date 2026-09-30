from pathlib import Path
import hashlib,json,os,subprocess,zipfile
P=Path(r'E:\ESTUDO APK\work\native-carousel\implementation');R=P/'open-button-lzgames'
BASE=P/'TurboramaStation-retorno-logado.apk';OUT=P/'TurboramaStation-abrir-lzgames.apk'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(BASE.read_bytes())=='6edd9f735236598fa1eb1f556c611a7ad56a2ee7d08f14bd1f0004c5b753e204'
JAVA=Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
BT=Path(r'E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15')
(R/'tmp').mkdir(exist_ok=True);os.environ['TMP']=os.environ['TEMP']=str(R/'tmp')
module='lib/arm64-v8a/libturbo_carousel.so';lib=(P/'libturbo_carousel.so').read_bytes()
unsigned=R/'button-unsigned.apk';aligned=R/'button-aligned.apk'
def run(*args):subprocess.run(list(map(str,args)),check=True)
with zipfile.ZipFile(BASE) as z,zipfile.ZipFile(unsigned,'w',allowZip64=True) as out:
    for info in z.infolist():
        if info.filename.startswith('META-INF/'):continue
        out.writestr(info,lib if info.filename==module else z.read(info.filename))
run(BT/'zipalign.exe','-f','-P','16','4',unsigned,aligned)
unsigned.unlink()
run(JAVA,'-jar',BT/'lib/apksigner.jar','sign','--alignment-preserved','true','--ks',r'C:\Users\Admin\.android\debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',OUT,aligned)
run(JAVA,'-jar',BT/'lib/apksigner.jar','verify',OUT)
with zipfile.ZipFile(BASE) as a,zipfile.ZipFile(OUT) as b:
    names={n for n in a.namelist() if not n.startswith('META-INF/')}
    assert names=={n for n in b.namelist() if not n.startswith('META-INF/')}
    changed=sorted(n for n in names if sha(a.read(n))!=sha(b.read(n)))
    assert changed==[module],changed
aligned.unlink()
report=dict(apk=str(OUT),sha256=sha(OUT.read_bytes()),bytes=OUT.stat().st_size,
    base=str(BASE),base_sha256=sha(BASE.read_bytes()),changed=changed,
    reference='https://app.lzgames.com.br/login',reference_component='/assets/Login-ab66cf00.js; Entrar submit button',
    native_module_sha256=sha(lib),session_dex_identical=True,all_other_dex_identical=True,
    emulator_engines_identical=True,media_identical=True,installed=False,visual_check_performed=False,
    promoted_to_stable=False)
(R/'build-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
profile_path=P/'stable-design/active-profile.json';profile=json.loads(profile_path.read_text(encoding='utf-8'))
profile.update(latest_built_apk=str(OUT),latest_built_apk_sha256=report['sha256'],installation_pending=True,
    current_revision_promoted_to_stable=False,source_visual_update='Native ABRIR adapted from LZ Games login code: emerald/lime gradient, strong green glow, 200ms focus transition')
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note=f'''# Atualização do botão ABRIR — referência LZ Games

APK compilado e assinado, ainda NÃO instalado. Aparelho não apareceu na consulta USB desta entrega.
APK: {OUT}
SHA256: {report['sha256']}
Fontes/montagem: {R}; native_skin.h. Gradiente e cores do botão Entrar de https://app.lzgames.com.br/login adaptados ao controle nativo, halo verde forte e transição de foco 200ms. Ação e toque preservados. Sem WebView ou novas texturas.
Montagem incremental: build_native.py e open-button-lzgames/build.py. Base é retorno-logado.apk; apenas libturbo_carousel.so mudou. Todos os DEX, autenticação persistente, motores e mídias byte a byte preservados. Não remontar sobre base antiga sem a correção de sessão.
Sem teste visual/benchmark nesta entrega. Não promover como estável automaticamente; tag estavel-2026-09-29-playlist-retro preservada. Perfil installed_apk ainda aponta para a versão efetivamente instalada.
Pedido pendente: analisar Turborama Switch, Git e arquivos locais para integrar site de vendas e senha individual; usuário priorizou este botão e forneceu o site app.lzgames.com.br/login.

## Histórico anterior

'''
for path in [P/'AGENTS.md',P.parent/'HANDOFF-IMPLEMENTACAO-CARROSSEL-NATIVO.md']:
    path.write_text(note+path.read_text(encoding='utf-8'),encoding='utf-8')
(R/'ENTREGA.md').write_text(note,encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
