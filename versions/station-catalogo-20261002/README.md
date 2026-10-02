# Cliente Station no TESTE — 02/10/2026

Pedido do mantenedor: deixar o aplicativo neste ponto, no ramo `versao-funcional`. A pasta que gera o APK continua local. Este Git guarda o cliente Java e a receita. APK, `.so`, `.PUP`, BIOS, ROMs, `keys.txt` e catálogo não entram.

## Pasta de compilação

`E:\ESTUDO APK\work\native-carousel\implementation`

O cliente Station está em `station-security-20261001`. O APK canônico fica em `side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk`. O carrossel nativo é compilado na mesma pasta `implementation`.

## O que este ponto faz

- A lista visível sai de `no_backup/station-catalog.json`, gravada depois da sessão Station. O catálogo assado do APK não é servido como lista.
- Pedido a Miami, Sambox, Squareweb, `?e=` ou `?s=` para na hora. `drawers.json` antigo responde só a lista Station.
- Capa: `GET /v1/station/covers/{coverId}` com o Bearer da sessão. O endereço no carrossel fica em `station.invalid`.
- Jogo: endereço `station.invalid`, baixado só quando a pessoa inicia um arquivo que ainda não existe.
- Campo de senha, `LoginActivity` e `libturbo_carousel.so` não mudaram neste ponto.
- `classes8.dex` permanece o da leva do nome. A troca está em `classes5.dex` (`StationTransfer` ao lado de `HttpBridge`).

## TESTE no Samsung

Pacote `org.turboramastation.frontend`. Instalação `adb install -r --no-incremental` no `RQCY30751WY`, dados mantidos.

- APK SHA-256 `c11b98bf0df770ed78a285a38fb897317a5b6ee496ba6b121e2d52304a400a9a` (1 898 675 962 bytes)
- `classes8.dex` `21c267c81008b9002c58b2f0c4578cb1fd7e98d3d5d4f70e74e3471e07117a6b` (71 668 bytes)
- `classes5.dex` `e86cfd517bc874c5605e924d09a91ece36a652c335fb48893eb5d817afb45647` (75 488 bytes)
- Cemu estável conferido pelo empacote: `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`
- `classes24.dex` não foi trocado

Na abertura com a licença já gravada no aparelho, o log mostrou `catalog items=996`. A lista publicada tem 8 plataformas e 996 capas em `station.invalid`. A capa focada respondeu `404 STATION_COVER_NOT_FOUND`. Não houve pedido ao Miami nesse arranque.

## Receita

Na pasta `station-security-20261001`:

```
python build_station_transfer.py
```

O script compila `StationTransfer` para `classes5` e chama `package_station_login.py`. O empacote recusa `miami`, `sambox`, `?e=` e `?s=` em `classes8`. Assinatura debug, `zipalign -f -P 16 4`.
