# ESTÁVEL — TurboramaStation, câmera traseira

**Ponto estável solicitado pelo mantenedor em 29/09/2026.** A referência é o APK instalado com câmera atrás da nave e deslocamentos laterais. As nuvens dão a sensação de avanço. Alterações posteriores, inclusive vídeos nas células, devem partir de outra revisão e não mudar esta tag.

- Repositório: **luziellacerda/TurboElden**.
- Ramo estável: **estavel**.
- Tag fixa: **estavel-2026-09-29-camera-traseira**.
- Snapshot: [versions/estavel-2026-09-29-camera-traseira](versions/estavel-2026-09-29-camera-traseira/).
- Base dos motores: **1.0.8**, commit histórico **6727ab725f1c4ac9afdd0382cc7d4ae5d3ff8eb3**.
- APK exato: **TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk**.
- SHA256 do APK: **54681d24d4ae912c0d081b276064264f95ad5e1d41e4e2851d2daa87169c4257**.
- Tamanho: **562427492 bytes**.

O commit histórico 6727ab7 identifica a base do motor; a tag acima identifica a base com o design atual. Não são o mesmo ponto. Não escolher outro APK apenas porque contém “estavel” no nome.

## Pastas exatas neste computador

| Uso | Caminho absoluto |
|---|---|
| **Fontes ativos e compilação** | `E:\ESTUDO APK\work\native-carousel\implementation` |
| **APK estável de retorno (cópia separada)** | `E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira\TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk` |
| APK instalado, saída da compilação original | `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk` |
| Identidade da versão ativa | `E:\ESTUDO APK\work\native-carousel\implementation\stable-design\active-profile.json` |
| Evidências desta entrega | `E:\ESTUDO APK\work\native-carousel\implementation\flight-rear-view` |
| Handoff local completo | `E:\ESTUDO APK\work\native-carousel\HANDOFF-IMPLEMENTACAO-CARROSSEL-NATIVO.md` |
| Modelo, shaders e materiais 3D | `E:\ESTUDO APK\work\native-carousel\implementation\space3d` |
| Login aprovado e ícone T v2 | `E:\ESTUDO APK\work\native-carousel\implementation\brand-login` |
| Informações dos sistemas incorporadas | `E:\ESTUDO APK\work\native-carousel\implementation\theme-infos` |
| Sinopses dos jogos incorporadas | `E:\ESTUDO APK\work\native-carousel\implementation\game-info-xml` |
| Capas incorporadas ao nativo | `E:\ESTUDO APK\work\native-carousel\implementation\systems.h` |
| Base privada original | `E:\ESTUDO APK\work\native-carousel\implementation\stable-reference-audit\original-1.0.8-alignment-preserved.apk` |
| Ferramentas Android locais | `E:\ESTUDO APK\TurboRetroEmu-build` |
| Temporários principais | `E:\ESTUDO APK\work\native-carousel\implementation\tmp` |
| Checkout Git usado na publicação | `C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\TurboElden-git` |
| Cópia protegida anterior à publicação | `E:\ESTUDO APK\backups-seguros\TurboramaStation-fontes-20260929-153925.7z` |
| Tema de referência e artes originais | `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx` |
| XMLs originais de informação | `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx2\_theme_inc\infos` |
| Vídeos pedidos depois deste ponto estável | `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas` |

## Pastas dentro do Git

| Pasta/arquivo | Conteúdo |
|---|---|
| `versions/estavel-2026-09-29-camera-traseira/snapshot/implementation/` | Fontes e recursos congelados desta entrega |
| `.../snapshot/implementation/space3d/` | Shaders, materiais, modelo e fontes/licenças do F-16 |
| `.../snapshot/implementation/brand-login/` | Código visual do login e arte do ícone |
| `.../snapshot/implementation/theme-infos/` e `game-info-xml/` | Metadados incorporados ao APK |
| `.../snapshot/implementation/flight-rear-view/` | Script de montagem incremental e recibos da entrega |
| `.../MANIFESTO-ESTAVEL.json` | Caminhos, tamanhos e SHA256 de todos os 575 arquivos preservados |
| `.../restaurar_fontes.py` | Restauração em pasta nova, incluindo os cabeçalhos comprimidos |
| `.../RESTAURACAO.md` | Passos para identificar o APK correto, recuperar fontes e compilar |

## O que este ponto preserva

Carrossel nativo de plataformas, capas de sistemas arredondadas e de jogos retas, informações e sinopses, menus Turborama, login aprovado, ícone T v2 e F-16 com câmera traseira. Todos os motores da referência histórica 1.0.8 permanecem iguais; não incorpora os experimentos de motor, limite de FPS ou carregamento de shaders.

A versão foi instalada em 29/09/2026 15:38 por atualização, com Success e SHA256 conferido. A designação de estável foi solicitada pelo usuário. Não houve nova medição de FPS, teste universal de aparelhos nem inspeção visual desta animação pelo agente.

## Publicação e limites de recuperação

Este Git preserva fontes e recursos da integração visual. Os cabeçalhos grandes `systems.h` e `space3d_assets.h` estão em `.gz`, com o conteúdo original recuperável por hash; não são substitutos vazios. As licenças e os fontes correspondentes do modelo foram preservados.

**APKs, chaves, firmware, ROMs, BIOS, saves, credenciais, chave de assinatura e dados brutos do aparelho ficam somente no computador.** O clone sozinho não substitui a base privada: o C++ original completo do frontend/motor não está disponível nesta integração. Para recompilar é necessário o APK original local de SHA256 **5cd234d0ac57aa6f1b260db6278087b7d961c671385ecf47871570bc00e78814** e as ferramentas locais indicadas. Uma cópia separada do APK foi guardada em `E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira`, fora da pasta de compilação. Para retornar exatamente a esta entrega, use o APK congelado de SHA256 **54681d24...**, não uma recompilação arbitrária.

O repositório `TurboRetroEmu`, a pasta `E:\TurboEdenEngine` e APKs com nomes “motor-teste”, “loading-teste”, “sobrevoo” ou “voo” não identificam este ponto estável. Não substituir este snapshot por aqueles materiais. Nunca desinstalar/limpar os dados para atualizar; preservar jogos, saves e configurações.
