# R180: GBA por link, controles Wii e retorno GameCube

Candidata incremental sobre o APK R179 exato
`aad5358bc1920a94eda414cf3edcccd5acd46daaaa54eed73ed4c005aec7032d`.
O proprietário reprovou a experiência GameCube de oito quadros e pediu
GBA/Wii/GameCube preparados para testes, seguidos de auditoria de bytes,
recursos, encerramento e endpoints. Não solicitar novas senhas durante sua
ausência. Não confundir preparação, cadastro protegido e partida física.

## Diferença permitida

- Restaura os três tipos de política/sessão Dolphin da referência assinada
  R173/R176 e remove o helper de oito quadros. A sessão produtiva volta aos
  bytes anteriores ao ensaio; GameCube declara buffer cinco, Wii conserva cinco.
- A apresentação aceita controles Wii já verificados. O defeito anterior
  devolvia classificação pendente mesmo com perfil assinado reconhecido.
- GBA usa o gpSP oficial em `5819380c2ffb0900219d700a382ee68c464ebb99`.
  O módulo Android tem nome próprio e segmentos de 16 KiB; o emulador não foi
  modificado. O mGBA offline continua idêntico.
- Um GBA e um controle P1 por participante. A comunicação é o netpacket
  oficial. Saves online persistem por conteúdo na pasta privada do app;
  nenhum save offline é importado ou sobrescrito.
- O lançamento de outras plataformas devolve a configuração original.
  Não acrescenta thread, timer, polling, shader, wakelock ou trabalho por quadro.

Seis entradas anteriores podem mudar: Manifest, classes35, registro de motores
e os três wrappers de identidade. Duas entradas são adicionadas: core gpSP e
CFG de sete controles, que reutiliza imagens já existentes. As outras 13.855
entradas e 39 DEX devem manter SHA-256. Núcleos anteriores, opções PSX/N64/Wii,
correção do atualizador, fotos R179, pacote, assinatura e dados permanecem.
R172 estável/backup/tags são imutáveis. Não promover esta candidata por testes
de compilação, HTTP ou geração de quadros em um harness.

## Receitas e provas

`recipe/build_gpsp.py` exige o checkout oficial fixado. `recipe/build.py` verifica
o doador, a fonte congelada, projeções de classes e o APK inteiro. `signing/`
exige a autoridade original recebida; não contém chave nem senha. O kit inclui
os bytes exatos dos cinco owners, licenças GPL e referências da fonte.

`tests/GbaWiiPolicyProbe.java` verifica P1 independente, limites, integridade das
configurações externas ao GBA, persistência privada e recusa de diretórios
inválidos. `tests/gpsp_core_probe.c` executa o núcleo original com conteúdo local,
ABI, imagem/áudio e limites de pacotes em processo isolado. Nunca são incluídos
no produto. Não equivalem a partida real entre dois Android.

O catálogo visível foi conciliado: 99 GBA, sete Wii e 20 GameCube
(21 registros GameCube, incluindo o conteúdo ocultado anteriormente).
O gpSP implementa link para dez dos 99 GBA presentes; os outros 89 exigem
suporte adicional de link e não recebem aprovação fictícia. A lista por edição
e os testes devem ficar no mesmo retorno existente do servidor.

## Aplicação

O serviço de produção e os aparelhos continuam na revisão realmente conferida
até existir recibo de aplicação e instalação. O registro e a ativação da API
são protegidos pelo Linux. Se não houver autorização não interativa, concluir
pacote, qualificação isolada e auditoria; não abrir autenticação sem o proprietário.
Depois registrar os IDs exatos e instalar por USB antes de testar salas novas.
O trabalho visual e de velocidade do atualizador continua adiado.

Fontes: [gpSP fixado](https://github.com/libretro/gpsp/tree/5819380c2ffb0900219d700a382ee68c464ebb99),
[interface netpacket](https://github.com/libretro/gpsp/blob/5819380c2ffb0900219d700a382ee68c464ebb99/libretro/libretro.c),
[documentação Dolphin](https://dolphin-emu.org/docs/guides/netplay-guide/).
