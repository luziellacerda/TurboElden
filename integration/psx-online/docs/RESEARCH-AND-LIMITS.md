# Pesquisa, solução aplicada e limites PSX

## O que foi localizado

O core normal foi identificado por SHA256 e pela revisão upstream `ff81ed17a15241d2f3730cdd7585b38e172532ca` do PCSX-ReARMed. Sua interface Libretro e suas opções são disponíveis em fontes primárias. O owner normal, `libmain.so` SHA256 `62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6`, contém LibretroPlayer, renderer/input SDL e o loop usado no modo normal.

A pesquisa nas árvores locais de integração/reconstrução, históricos/ramos acessíveis e referências GitHub não localizou a **fonte C++ exata desse owner normal**. Repositórios aparentados de EmulationStation/Turborama não foram tratados como prova de equivalência com esse ELF. Fontes de hooks visuais antigos e `libmain_hook` do carregamento gráfico Dolphin tampouco foram tratadas como o loop do Player. Esse resultado é delimitado ao acervo e às referências examinadas; não afirma que a fonte inexiste em qualquer lugar.

As [fontes do core na revisão usada](https://github.com/libretro/pcsx_rearmed/blob/ff81ed17a15241d2f3730cdd7585b38e172532ca/frontend/libretro.c) descrevem callbacks e execução Libretro, mas não fornecem a implementação desse frontend normal. A [API Libretro](https://github.com/libretro/RetroArch/blob/master/libretro-common/include/libretro.h) e a [documentação de desenvolvimento de cores](https://docs.libretro.com/development/cores/developing-cores/) definem a fronteira entre frontend/core. Compartilhar essa API não transforma automaticamente um frontend normal em um cliente netplay.

## Solução concreta

O Player original é reutilizado, sem recompilação fictícia do owner. Um adaptador opt-in ARM64/API28 verifica hashes, segmentos ELF, GOT e call sites exatos antes de instalar quatro interceptações em memória no **processo privado PSX**. Nenhum ELF donor é regravado. As verificações e a receita são públicas; a reprodução precisa dos donors exatos locais.

As interceptações atingem `SDL_PollEvent`, `SDL_GetPerformanceCounter`, `dlsym` e o home path do Player. Os return PCs `0x2ae600` e `0x2ae61c` delimitam a checagem de pausa original e o retorno de execução. O adaptador usa o pause byte real para aguardar sem congelar o loop SDL, renderer ou pacing. Endereço, hash ou callback divergente bloqueia a preparação; não há tentativa de adivinhar uma ABI nova.

O core normal recebe seus callbacks originais para amostrar controles; as entradas de dois slots são então servidas pela lease canônica. O `retro_run` original só é chamado uma vez quando existe permissão válida e entrada completa. `ownerComplete` ocorre apenas depois de seu retorno. Falha limpa a lease sem produzir prova de quadro executado. Threads de rede não chamam serialize, unserialize nem executam o core.

Esse cuidado corresponde à separação frontend/core da API Libretro. O processamento de eventos continua no owner, respeitando o requisito de thread da [documentação SDL_PollEvent](https://wiki.libsdl.org/SDL2/SDL_PollEvent). A [documentação Libretro sobre netplay](https://docs.libretro.com/development/retroarch/netplay/) fundamenta a necessidade de entradas por quadro, estado compatível e sincronização; PXL1 é um protocolo Station próprio e não é anunciado como compatível com o wire RetroArch.

## Política determinística atual

- Somente duas portas Standard e jogos individualmente aprovados para essa topologia e BIOS HLE. A revisão não garante HLE para todo o acervo.
- SHA do core, owner, defaults compilados, overrides, perfil e conteúdo fazem parte da identidade. Opções offline, cheats e saves antigos não são delegados à sessão.
- Os 59 defaults reais são conferidos via registro V2; sete overrides têm valores validados. O DRC não é desligado; threads auxiliares, frameskip, multitap e analog combo são desativados pelo perfil atual.
- Pipeline fixo D4: entrada N é destinada a N+4. As primeiras quatro entradas neutras só são preparadas após estado e autorização reais. Não há rollback ou avanço oculto para preencher uma espera.
- O anfitrião organiza os quadros canônicos; cada aparelho emula localmente. Um FRAME só é publicado após o quadro real do anfitrião retornar.
- CUE usa `cue-set-v1`, incluindo tracks. Arquivo/track alterado entre preparo e consumo invalida a partida. CHD/PBP conservam identidade do arquivo de lançamento.

## Autoridade, pausa e estado

RendererReady e CoreReady informam preparo. Nenhum deles é ACK de CPU. READY/resume requer o epoch e serial atuais, ACK no checkpoint real, estado inicial aplicado, filas drenadas e ausência de frame em curso, aplicação de estado, pausa local ou falha. Serial novo revoga a permissão anterior; a decisão Java de controle/resume é serializada.

Copiar dados para uma mailbox limitada permite confirmar transporte. Executar um quadro ou aplicar estado gera COMMIT semântico distinto. Duplicatas/replays têm regras explícitas; bytes aceitos não fabricam Executed. Mudança de epoch invalida filas incompatíveis e recuperação conserva o cursor por snapshot real.

O tamanho do snapshot vem de `retro_serialize_size` após carregamento real, deve ser exato e fica limitado a 16 MiB. Hash, identidade, epoch e serial são verificados antes de decodificar. Aplicação só ocorre no owner pausado e exige `retro_unserialize` positivo. O envelope validado não demonstra segurança de todos os campos internos do decoder.

## Saída e dados

Menu de pausa local solicita barreira global, mantendo heartbeat/autoridade HTTP. Save/load/reset/fast-forward ou encerramento automático não podem criar divergência no processo online. Menus nativos de save/load/exit são guardados antes dos efeitos; o menu Java fornece confirmação humana de saída.

A confirmação positiva autoriza saída; cancelar, falhar, perder Internet, exceder espera, receber SDL_QUIT ou core SHUTDOWN não autoriza. Após confirmação, o close normal é seguido por limpeza opt-in que aguarda threads e executores reais, fecha o Socket WebSocket se necessário e não converte timeout em autorização de matar a partida. O Binder conclui sua liberação na UI; a Activity comprova que a thread SDL capturada terminou antes de finalizar somente seu PID privado. `mSDLThread == null` e WebSocket `isClosed` isolados não são provas suficientes.

Home/system/save são caminhos privados novos de sessão. Licenças, saves offline, configurações de core e bibliotecas normais não são copiados nem apagados. Somente apresentação/controlador selecionado pode ser transferido conforme a lista validada do Launch.

## O que as provas permitem afirmar

Há compilação real ARM64/JNI, montagem de partições DEX completas, análise do ELF donor e testes host/JVM de código produtivo com dependências simuladas explícitas. Os recibos incluem sucesso, hashes, escopo e restrições; [a revisão final](../evidence/OWNER-SESSION-REVIEW.md) resume os contadores.

A verificação [package-final.json](../evidence/package-final.json) concluiu o APK assinado `a350878cca5c1a65c51e79ac13e9e38c2053d76e5404edb515ad1ddd650c3038`: 13.549 entradas preservadas, certificado original v2/v3 e alinhamento 16 KiB. As identidades empacotadas estão em [runtime-final.json](../evidence/runtime-final.json). `notPackaged`, `originalManifestUnchanged` e `apkChanged: false` dos recibos de hooks/assembly isolados expressam o escopo daqueles probes, não ausência de integração no pacote final. Esses campos não substituem a conferência integral do APK.

Não houve execução Android/ROM nas provas desta integração. Portanto continuam pendentes gameplay em dois aparelhos, precisão da amostragem touch/Bluetooth física, compatibilidade de serialize antes do primeiro quadro para cada jogo aprovado, comportamento após reconexão real, latência sustentada, aquecimento e estabilidade prolongada. Pipeline4 reduz espera por quadro nas fixtures, mas não elimina o custo do RTT nem garante 60 fps em toda rede.

A UI e as lógicas de economia, GPU/capas/LED, vídeos locais, preload e 30 fps de apresentação não foram redesenhadas por esse adaptador. A verificação integral confirmou preservação do payload declarado, certificado e bibliotecas normais; isso não substitui avaliação térmica ou gameplay. Ativação do registro do servidor e instalação física exigem evidências próprias e não são inferidas da compilação ou dos IDs finais.
