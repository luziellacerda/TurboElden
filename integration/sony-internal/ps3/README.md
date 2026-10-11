# PS3 interno: owner mínimo com o core oficial aPS3e 2.43

Esta integração contém Java do owner, declarações JNI verificadas e receitas. Não contém APK, bibliotecas binárias, firmware, jogos, chaves de jogos ou imagens. O core original é um artefato privado; sua reconstrução completa não é alegada. A branch oficial associada ao release não coincide integralmente com a interface Java do APK 2.43, portanto as assinaturas JNI foram extraídas do APK exato.

## Composição

- Application: `org.emulationstation.frontend.sony.Ps3Application`, selecionada pela factory antes de executar inicializadores de outros emuladores.
- Activity privada: `org.emulationstation.frontend.sony.Ps3Activity`, processo `:station_ps3`, ARM64, Android28+, singleTask e configuração de tela tratada pelo owner.
- `operation=play|settings|prepare`; `play` é o padrão.
- `game_uri`/Intent.data: ISO local por contentURI com permissão de leitura; `game_path`: ISO ou diretório local com PARAM.SFO/EBOOT real.
- `decryption_key_uri` opcional: arquivo local pertencente ao usuário, passado ao JNI real. Não se obtêm nem inventam chaves. ISO criptografado sem chave válida pode ser recusado pelo core.
- PKG não é anunciado como abertura direta PS3 nesta integração. O dispatcher atual da Station aceita ISO para PS3.

O contexto deve usar o package da Station e o processo dedicado. `Ps3Application.onCreate` não extrai nem carrega bibliotecas. `Ps3Bootstrap.prepare` faz o trabalho em uma única thread e publica o owner somente após a conclusão do JNI. Reentrar em configurações reutiliza esse owner; não chama a implementação problemática `load_library` do launcher externo.

O template StationPsxOnlineActivity do manifesto R130 não declara launchMode. A composição precisa adicionar explicitamente `android:launchMode="singleTask"` ao Ps3Activity (resourceID0x0101001d, valor inteiro2); copiar o template sem esse atributo não garante um único owner. O Java rejeita pedidos concorrentes enquanto prepara ou executa um jogo. Envios ao worker e seu encerramento compartilham um lock, e callbacks após encerramento são descartados.

## Artefatos privados exatos

O descritor `sony/ps3/module.json`, com pin `StationSonyAssetPins.PS3_MANIFEST_SHA256`, é produzido pela composição comum. `StationSonyAssets.prepare` confere e extrai para `no_backup/station-sony/ps3/<moduleId>`. Somente `StationSonyAssets.loadNative` carrega as bibliotecas declaradas, por caminho absoluto.

APK oficial 2.43: SHA256 `c5a58fb056ae333b8bd6ed69e6bfacdd1e5bf7e0ac2134456a0622bd94a3e466`, 40122859bytes. Os sete SO, SONAMEs, DT_NEEDED e estruturas JNI exatas estão em `evidence/official-contract.json`. `libe.so` original tem SHA256 `5d8fb9b0c2e849df795be50ae767e4443617d7b6af7a9dd2970a21b022e278f3` e não depende de libc++ compartilhada. Nenhum SO da Station é substituído. As quatro bibliotecas de hooks são preservadas como arquivos privados, mas não são carregadas no perfil padrão, que usa Vulkan do sistema.

Inputs adicionais: config/config.yml original, licenses.html original, 59 arquivos Icons/ui e PUP4.93 privado. patch.yml pode ser preservado pela composição, mas não é aplicado automaticamente. Ícones são copiados para userdata/config/Icons/ui conforme a inicialização oficial. O arquivo de configuração existente e os saves permanecem no diretório estável `no_backup/station-sony/ps3/userdata`, separado do runtime versionado.

A solicitação humana de incluir o firmware em assets autoriza este input privado para o instalador local. Nenhum byte desse arquivo entra no repositório. `Prepared.assetFile("PS3UPDAT.PUP")` deve fornecer exatamente 206197916bytes, SHA256 `158471fd834f8ea8036136b6aab43cd86c7ba73d79ca30e0af3c0fe0001cf365`, magic SCEUF. Não há download, link de rede, wizard ou menu de instalação no owner. O JNI `install_firmware(fd)` importa automaticamente. Somente retorno true junto de arquivos SPRX reais permite gravar o recibo e o marcador upstream `.installed`; presença de um asset não significa firmware instalado nem jogo executado.

## Compilação e guardas

Compilar os Java desta pasta junto da API comum e da classe de pins gerada, com o SDK Android atual e minAPI28. As declarações `aenu.*` não podem ser renomeadas nem receber carga estática de bibliotecas por nome. Depois do D8, executar `recipe/verify_jni.py --dex <DEX PS3 compilado> --out <recibo privado>`; ele compara cinco classes nativas e cinco estruturas JNI com o contrato oficial exato. A receita não precisa do APK inteiro no output.

`generate_owner_assets.py` gera somente nomes de arquivos e texto Java a partir do APK/pinned XML, sem mídias. A localização nativa é instalada no ambiente antes de carregar libe.so, preservando os textos usados pelos overlays do core. Não é necessário mesclar os resources0x7f, AndroidX, Compose ou o DEX original de 7010classes.

O owner renderiza por SurfaceView original do Android e usa os valores ControlId reais da versão2.43. Controles físicos escondem apenas a camada estática de toque. Não há timer gráfico nem limite30fps imposto ao gameplay. Pause/resume/surface/quit são serializados no worker; eventos de controle usam a entrada nativa original. Ao encerrar um jogo, o owner termina somente seu processo dedicado, como o ciclo original por jogo; não encerra o frontend nem limpa dados.

## Evidência e limites

Até a composição final, isto é implementação de fonte. Compilação, extração, importação de firmware, Surface, controle, gameplay, velocidade e compatibilidade são etapas distintas. Não há prova de jogo real desta integração neste recibo. PS3 em Android continua dependente da capacidade da CPU/GPU e da compatibilidade do core; preparado automaticamente não significa que todo título seja executável.

Fontes primárias: [release oficial aPS3e2.43](https://github.com/aenu1/aps3e/releases/tag/2.43), [código oficial aPS3e](https://github.com/aenu1/aps3e), [software oficial do sistema PS3](https://www.playstation.com/en-us/support/hardware/ps3/system-software/), [licença oficial do sistema PS3](https://www.playstation.com/en-us/legal/ps3-system-software-license-agreement/). Preservar o aviso WTFPL dos wrappers oficiais e licenses.html do artefato na composição privada.
