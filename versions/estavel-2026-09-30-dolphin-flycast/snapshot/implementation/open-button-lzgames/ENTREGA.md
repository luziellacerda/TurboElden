# Atualização do botão ABRIR — referência LZ Games

APK compilado e assinado, ainda NÃO instalado. Aparelho não apareceu na consulta USB desta entrega.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-abrir-lzgames.apk
SHA256: d9518d5c6359e27ce8c31c287c78de3700d56d85efc801da37660f9575198f10
Fontes/montagem: E:\ESTUDO APK\work\native-carousel\implementation\open-button-lzgames; native_skin.h. Gradiente e cores do botão Entrar de https://app.lzgames.com.br/login adaptados ao controle nativo, halo verde forte e transição de foco 200ms. Ação e toque preservados. Sem WebView ou novas texturas.
Montagem incremental: build_native.py e open-button-lzgames/build.py. Base é retorno-logado.apk; apenas libturbo_carousel.so mudou. Todos os DEX, autenticação persistente, motores e mídias byte a byte preservados. Não remontar sobre base antiga sem a correção de sessão.
Sem teste visual/benchmark nesta entrega. Não promover como estável automaticamente; tag estavel-2026-09-29-playlist-retro preservada. Perfil installed_apk ainda aponta para a versão efetivamente instalada.
Pedido pendente: analisar Turborama Switch, Git e arquivos locais para integrar site de vendas e senha individual; usuário priorizou este botão e forneceu o site app.lzgames.com.br/login.

## Histórico anterior

