# Metadados de jogos — R39 — 06/10/2026

Fonte pública: https://gamesdb.launchbox-app.com/Metadata.zip. Snapshot e SHA da fonte em `evidence`/backup de metadados. Estes XMLs contêm fatos (nome, plataforma, máximo de jogadores, avaliação e votos), não ROMs, links de download nem autorização para publicar jogos.

O catálogo de download continua vindo do servidor Station autenticado. Estes arquivos não criam plataformas nem jogos no catálogo. O índice nativo gerado procura plataforma + título/alias exato, com normalização conservadora. IDs atuais têm prioridade. Casos ambíguos não são adivinhados.

## Cobertura verificável

Catálogo atual: 2212 itens; 2.211 com jogadores, 2.211 com nota. As duas lacunas são títulos diferentes: jogadores de Super Mario World (hack Mega Drive Chuanpu/Jazz) e nota de Dragon’s Heaven (development board, Neo Geo). Consulte `current-metadata-pending.json`.

2.096 correspondências públicas únicas. Notas públicas exigem votos > 0 e são convertidas de 0–5 para 0–1 no XML/0–1000 no índice. Outros valores existentes do XML são preservados com procedência própria; não representam necessariamente uma média pública. Traduções BR herdam a avaliação da edição-base quando documentado no audit.

Preparação futura: 72 plataformas, 72033 registros de metadados, 46152 com ambos os campos. 15132 sem avaliação e 17173 sem jogadores na fonte (grupos podem se sobrepor). Ausência permanece explícita; nunca preencher com zero/cinco estrelas ou número inventado.

Inclui plataformas clássicas até Xbox 360 e mantém em grupo separado os sistemas mais recentes já presentes no aplicativo (3DS, Wii U, Vita e Switch). Não representa uma lista completa de todos os jogos já lançados.

Para acrescentar/corrigir: consultar fonte verificável, registrar alias exato por plataforma se necessário, executar pipeline e testes, conferir diferenças do índice e recompilar. Não usar `DatabaseID` como URL de página: o site e o dump podem ter identificadores diferentes.

| Plataforma | Jogos | Com ambos | Sem nota | Sem jogadores |
|---|---:|---:|---:|---:|
| 3do | 386 | 276 | 5 | 108 |
| 3ds | 1707 | 616 | 409 | 949 |
| amigacd32 | 406 | 222 | 130 | 118 |
| arcade | 7180 | 4538 | 778 | 2342 |
| arcadia | 62 | 59 | 1 | 2 |
| astrocade | 51 | 50 | 0 | 1 |
| atari2600 | 1298 | 857 | 426 | 53 |
| atari5200 | 148 | 140 | 8 | 1 |
| atari7800 | 163 | 118 | 43 | 5 |
| atomiswave | 34 | 31 | 1 | 3 |
| cdi | 283 | 107 | 19 | 164 |
| channelf | 46 | 44 | 1 | 1 |
| colecovision | 552 | 370 | 167 | 24 |
| dreamcast | 911 | 710 | 104 | 112 |
| fds | 270 | 260 | 8 | 3 |
| gameandwatch | 317 | 308 | 0 | 9 |
| gamecom | 23 | 23 | 0 | 0 |
| gamecube | 811 | 675 | 47 | 93 |
| gamegear | 412 | 398 | 11 | 5 |
| gb | 1605 | 1083 | 316 | 264 |
| gba | 2367 | 1499 | 342 | 600 |
| gbc | 1567 | 781 | 392 | 453 |
| intellivision | 180 | 170 | 5 | 7 |
| jaguar | 128 | 106 | 18 | 5 |
| jaguarcd | 46 | 37 | 5 | 5 |
| loopy | 10 | 6 | 0 | 4 |
| lynx | 162 | 108 | 53 | 8 |
| mastersystem | 555 | 446 | 89 | 26 |
| megadrive | 2128 | 1405 | 656 | 115 |
| model2 | 35 | 34 | 1 | 1 |
| model3 | 29 | 28 | 1 | 1 |
| n64 | 800 | 576 | 202 | 44 |
| n64dd | 13 | 13 | 0 | 0 |
| naomi | 154 | 145 | 5 | 4 |
| naomi2 | 21 | 20 | 1 | 1 |
| nds | 4576 | 2696 | 807 | 1490 |
| neogeo | 180 | 167 | 6 | 7 |
| neogeocd | 112 | 80 | 7 | 26 |
| nes | 3843 | 2835 | 851 | 275 |
| ngage | 74 | 64 | 7 | 5 |
| ngp | 10 | 9 | 0 | 1 |
| ngpc | 84 | 75 | 8 | 1 |
| odyssey2 | 96 | 82 | 3 | 13 |
| pcengine | 343 | 331 | 4 | 8 |
| pcenginecd | 446 | 364 | 22 | 72 |
| pcfx | 73 | 65 | 5 | 3 |
| pico | 262 | 92 | 28 | 168 |
| pokemonmini | 42 | 39 | 0 | 3 |
| ps2 | 4783 | 2779 | 911 | 1730 |
| ps3 | 2606 | 1593 | 367 | 894 |
| psp | 2041 | 1580 | 236 | 269 |
| psvita | 1190 | 451 | 248 | 673 |
| psx | 4649 | 3891 | 367 | 466 |
| pv1000 | 13 | 13 | 0 | 0 |
| saturn | 1194 | 1133 | 54 | 8 |
| scv | 29 | 29 | 0 | 0 |
| sega32x | 63 | 53 | 7 | 4 |
| segacd | 232 | 225 | 4 | 4 |
| sg1000 | 112 | 101 | 10 | 2 |
| snes | 2959 | 2332 | 491 | 184 |
| supergrafx | 5 | 5 | 0 | 0 |
| supervision | 79 | 63 | 11 | 6 |
| switch | 6609 | 3375 | 2731 | 1255 |
| vectrex | 103 | 79 | 21 | 12 |
| videopacplus | 86 | 51 | 7 | 28 |
| virtualboy | 75 | 71 | 0 | 4 |
| wii | 2297 | 1859 | 110 | 357 |
| wiiu | 819 | 644 | 42 | 152 |
| wonderswan | 113 | 109 | 2 | 2 |
| wonderswancolor | 97 | 92 | 5 | 1 |
| xbox | 1143 | 908 | 45 | 214 |
| xbox360 | 5735 | 1558 | 3471 | 3305 |
