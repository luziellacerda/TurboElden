# Saída atual

Montagem completa entrega TurboramaStation-playlist-retro.apk. Ver ../retro-playlist/ENTREGA.md. Referências anteriores são históricas.

# Saída atual

Montagem completa entrega TurboramaStation-led-intenso.apk. Ver ../led-brightness/ENTREGA.md. Referências anteriores são históricas.

# Saída atual

Montagem completa entrega TurboramaStation-videos-retorno-pronto.apk. Ver ../video-ready-cache/ENTREGA.md. Referências anteriores são históricas.

# Saída atual

Montagem completa entrega TurboramaStation-led-premium-diagonal.apk. Ver ../premium-led/ENTREGA.md. Referências anteriores abaixo são históricas.

# Saída atual

Montagem completa entrega TurboramaStation-nave-video-cache.apk. Ver ../flight-cinematic/ENTREGA.md. Referências anteriores abaixo são históricas.

# Saída atual

TurboramaStation-videos-720-unico.apk. Ver ../system-videos/README.md; estados abaixo são históricos.

# Saída atual

A montagem completa entrega TurboramaStation-videos-720p60.apk. Ver ../system-videos/QUALIDADE-720P60.md e registros; referências anteriores abaixo são históricas.

# Saída atual de montagem

A montagem completa `package_apk.py --full` entrega **TurboramaStation-videos-todas-celulas.apk**. O arquivo design-base-videos.apk é intermediário. O ponto estável congelado permanece na pasta E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira. Consulte ../system-videos/README.md e ../stable-design/active-profile.json.

## Histórico anterior

# Entrega atual com movimento da nave

A compilação completa agora termina em TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk. Ícone v2 e código do login aprovado preservados; detalhes e status em ../flight-rear-view/README.md e ../stable-design/active-profile.json.

# Turborama — ícone e tela de login

## Revisão atual: ícone v2 (29/09/2026 14:59)

O mantenedor aprovou a tela de login e rejeitou o primeiro ícone. Agora foi instalado **TurboramaStation-ESTAVEL-6727ab7-icone-v2.apk**, SHA256 **9fa98f2ad3f0747b7872291d959442bb1bc93f6199661acb5ef1a576e26ef21d**. Success e hash no aparelho conferidos.

Novo emblema: T simples, verde sobre preto e pequeno detalhe vermelho. Arte gerada pela ferramenta image_gen integrada: **assets/turborama-icon-v2.png**, prompt exato em **PROMPT-ICONE-V2.txt**. A cópia ativa usada pela compilação é assets/turborama-icon-master.png. O ícone com asas rejeitado fica em assets/turborama-icon-v1-rejeitado.png apenas como histórico.

Esta revisão altera somente os sete PNGs da marca/atalho. **Todos os DEX, bibliotecas nativas, Manifest e tabela de recursos são idênticos à versão com login aprovada pelo usuário.** O layout e as regras do login não foram editados. O emblema do login acompanha o novo ícone. Jogos, saves e preferências preservados. Não houve teste visual pelo agente no aparelho.

Reprodução exata desta revisão: **build_icon_only.py** sobre o APK identidade.apk/e40f7c71 preservado. A montagem completa **build_brand_login.py** e o empacotador principal entregam a edição indicada no início deste documento com a arte ativa. O tamanho da imagem adaptativa respeita a zona circular segura, enquanto os ícones antigos usam mais área. Evidências atuais em build-result.json e installed.json; evidências da primeira edição em revisions/v1/.

## Histórico da primeira edição de login (layout aprovado; ícone substituído)

Instalado em 29/09/2026 14:48 com Success; hash no aparelho idêntico ao build-result.json. Nenhuma limpeza de dados ou alteração de configurações. O celular estava bloqueado, portanto não houve conferência visual no aparelho. Nenhum teste de desempenho realizado nesta edição.

## Pedido e visual

Pedido do mantenedor de 29/09/2026: criar novo ícone nas cores Turborama e modificar o design do login.

- Marca: emblema T metálico com asas, verde luminoso, fundo preto e pequeno detalhe vermelho.
- Login Android nativo: cabeçalho Turborama, emblema, apresentação à esquerda e painel de senha à direita em telas largas; organização vertical em janelas estreitas.
- Painel com bordas finas, campo de senha identificado, botão verde “ENTRAR” e mensagem de erro acessível.
- Fundo estático com luz verde suave e linhas discretas. Não há animação, timer ou motor 3D nesta Activity.
- Teclado, Enter e foco direcional mantidos; dimensões em dp/sp e rolagem quando necessária.

## Base e escopo

Base: `../TurboramaStation-ESTAVEL-6727ab7-design.apk`, SHA256 `545e9b71e24da653f59ca67e2dd5f716a26fec3a64f5eb39860c87f14303f4e6`.
Ela deriva da versão 1.0.8 do commit `6727ab7`, cuja base original foi recuperada byte a byte.

Nova saída: `../TurboramaStation-ESTAVEL-6727ab7-identidade.apk`.
Hash da montagem inicial: `e40f7c715da6ffa606b71a9aa122b9a9e06ccfe68f2c24fee854d4c0935f1e1c`.

Somente sete entradas existentes foram alteradas: classes8.dex e os seis PNGs do ícone. Um PNG de marca foi adicionado em assets/turborama-brand/. Manifest, tabela de recursos, todos os outros DEX e todas as bibliotecas nativas permanecem iguais à base com design. Recursos visuais do carrossel e nave também permanecem iguais.

No classes8.dex, somente LoginActivity e suas classes internas de apresentação são substituídas. Todas as outras classes smali, inclusive AuthSession, LocalPassword, catálogo e integração do motor, são preservadas literalmente. Os métodos ensureAuthorized, submit, openFrontend, onNewIntent e onBackPressed são transplantados literalmente do login estável. FLAG_SECURE, autenticação, restrições de senha e ausência de salvamento/autofill da senha mantidos. Nenhuma senha, endpoint ou regra de acesso nova.

O redesenho não muda configurações, motor, shaders, downloads, jogos nem saves.

## Arquivos e reprodução

- `java/org/emulationstation/frontend/auth/LoginActivity.java`: fonte visual editável.
- `assets/turborama-icon-master.png`: arte original gerada pela ferramenta de imagens integrada; prompt em PROMPT.txt.
- `assets/launcher/`: imagens dimensionadas mecanicamente para as densidades Android. Emblema adaptativo dentro da área segura 66/108.
- `build_brand_login.py`: compila apenas o login, preserva os métodos críticos, substitui imagens existentes e assina com a mesma identidade. Requer APK base local, SDK/JDK/apktool já presentes e Pillow.
- `build-result.json`: hashes e limites exatos da alteração.
- `install_brand.py`: atualização com -r, sem desinstalar ou limpar dados; recusa se houver EmulationActivity na pilha.
- `installed.json`: evidência de instalação, se realizada. Não confundir compilação com conferência visual.

Executar `C:\Python314\python.exe build_brand_login.py` nesta pasta reconstrói sobre a base com design guardada. O empacotador principal `../package_apk.py --full` agora chama esta etapa ao final; entregar o APK terminado em **camera-traseira.apk**, conforme o estado atual no início deste documento. O intermediário design.apk permanece como base.

APK e login contêm materiais privados preexistentes: não publicar APK, credenciais ou código de autenticação. A nova arte e esta implementação não alteram as licenças dos componentes de terceiros.
