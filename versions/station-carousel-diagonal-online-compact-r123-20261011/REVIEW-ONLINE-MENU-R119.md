# R119 — interface online sem o menu do RetroArch

## Escopo e diagnóstico

A abertura online da R118 inicia `StationRetroActivity`, uma `NativeActivity` privada no processo `:station_netplay`, com a biblioteca `station_retroarch`. `StationRoomsActivity` passa ROM, core e configuração por lançamento interno validado; não abre um aplicativo externo do RetroArch.

O manifest do APK R118 exato (`960b62397fdff20491a5b842dcab0451fade5d786beb84c40e6a9d91ae456e42`) registra o SNES normal como `com.imagine.BaseActivity`, processo `:snes`, biblioteca `snes9x_explus`. O online usa o core `libstation_bsnes.so` dentro do runtime de netplay. São motores distintos; esta revisão mantém ambos e não substitui o motor online pelo standalone.

Havia três caminhos para a interface do RetroArch: `StationRetroLaunch` selecionava explicitamente `menu_driver=rgui`; os overlays PSX/N64/arcade possuíam descritores `menu_toggle`; alguns perfis upstream associavam Menu/Guide a essa ação. A Activity já tinha seu painel próprio em `⋮`/Voltar, mas só interceptava `KEYCODE_BACK`. Esses fatos demonstram caminhos possíveis no código; não identificam qual foi acionado na tela relatada, pois não houve leitura física nesta revisão.

Os overlays SNES/Mega Drive do próprio APK R118 já são `station-local/snes.cfg` e `station-local/megadrive.cfg`: SNES tem nove controles de jogo e Mega Drive possui páginas de três/seis botões. Suas imagens e posições ficam intactas. Não se afirma igualdade visual completa entre todos os controles offline e online sem conferência por plataforma.

## Alterações de produção

Somente dois Java foram alterados:

- `StationRetroLaunch.java`: sessão online usa `menu_driver=null`, `input_menu_toggle_gamepad_combo=0` e `input_menu_toggle`, `_btn`, `_axis` com valor `nul`.
- `StationRetroLaunch.copyAssets/onlineMenuOnly`: neutraliza apenas ações `menu_toggle` nas cópias privadas de CFG de `station-online`. Nos perfis copiados, somente os bindings dessa ação recebem `nul`. Nos descritores de overlay, somente o token dessa ação é retirado; sem outras ações, o token torna-se `nul`, que o parser reconhece como ausência de binding. O restante do descriptor, PNGs, imagens, geometria, troca de páginas e bindings de jogo é preservado. A comparação do cache ocorre depois da transformação, evitando regravar o CFG a cada lançamento.
- `StationRetroActivity.dispatchKeyEvent`: Back, Menu e Guide (`KEYCODE_BUTTON_MODE`) abrem o painel próprio na liberação da tecla. A/B/X/Y, direcional, Start, Select, ombros e eixos continuam sendo enviados ao input nativo. `⋮`, confirmação humana de saída, recuperação e ownership da sessão permanecem como antes.

Não se altera autoconfig original, identidade de controle, assinatura da aplicação, validação/autenticação, engine IDs, cores, runtime, slots, protocolo, preferências gráficas, economia de menus, template offline ou dados de jogo. `StationAndroidControllerProfile.prepare`, inclusive sua adaptação BSP-D3/Xbox condicionada às capacidades reais do Android, continua executando no mesmo ponto.

## Base oficial e correspondência exata

Upstream: RetroArch commit `69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576`.

- [Driver null oficial](https://github.com/libretro/RetroArch/blob/69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576/menu/menu_driver.c): existe um driver sem renderização, incluído na lista de drivers.
- [Runloop oficial](https://github.com/libretro/RetroArch/blob/69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576/runloop.c): a alternância por hotkey é bloqueada quando `menu_driver` é `null`.
- [Overlays Libretro](https://docs.libretro.com/guides/libretro-overlays/): descritores de overlay são a interface de entrada, separados do core.

A fonte correspondente privada fornecida com o runtime foi lida sem extrair/modificar arquivos. O runtime dessa entrega e o runtime dentro do APK R118 têm o mesmo SHA-256: `81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc`.

Os seguintes hashes da fonte correspondente conferem com seu `CORRESPONDING-SOURCE-MANIFEST.json`:

| Arquivo | SHA-256 | Evidência de leitura |
| --- | --- | --- |
| `menu/menu_driver.c` | `379adc9bcefd1d44bbd82f6ca3417723a98d3ace97937b7ca0ea668554118e94` | Driver null nas linhas 273–343. |
| `runloop.c` | `13179287191fe00a76c6d35ddc75374388543b2c05607b14dc8c6efef135a012` | Linha 6004 bloqueia hotkey para driver null. |
| `configuration.c` | `67d33a5933bd3464df2c7846b05e644ca9d4da7596258e6814dcc782bdbffdca` | Linhas 6758–6763 e 6847–6852 aceitam `nul` como AXIS_NONE/NO_BTN. |
| `tasks/task_overlay.c` | `0276b2511af2cac813ae2172f042b9cd8e2bdd51774372e4b59fe4ce6ec49883` | Linhas 349–353 ignoram o token de ação `nul`. |

## Limitações e estado

O driver null dessa versão não tem `context_reset`; `menu_driver_init` pode registrar `Unable to init menu driver`. Em `retroarch.c:1733` isso é um log, não uma ordem de encerramento da emulação. A mensagem deve ser distinguida de falha real de core/ROM. Não se recompila o runtime para silenciar esse aviso.

Nenhum teste, compilação, operação de aparelho, início de sala ou gameplay foi executado por esta revisão de fonte. A compilação final e a conferência física pertencem à entrega R119. Não há alegação de correção já validada em partida, melhoria térmica ou funcionamento confirmado do BSP-D3.

Hashes dos Java após a alteração:

- `StationRetroLaunch.java`: `6552e3e58bd0ca4423a0d5358d6e76e0cf8ffccef04ae67c549c37974259dbdc`.
- `StationRetroActivity.java`: `a7f4816cad3e506a19e91fe72d5ade2aca1e295ae7ad79d2be22f102fedc3acc`.
