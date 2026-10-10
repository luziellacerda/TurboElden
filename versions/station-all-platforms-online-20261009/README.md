# Station — candidata de integração de plataformas

Leia `../../docs/server/HANDOFF-ONLINE-PLATAFORMAS-STATION-20261009.md` para o estado integral. Backup anterior publicado nos dois repositórios; código desta candidata está isolado. Servidor publicado com catálogo31/perfis5176 e 17 plataformas, incluindo PS2/Saturn; veja o recibo atual no mesmo handoff. Canais e instalações dos celulares permanecem anteriores; o APK completo ainda precisa ser montado no PCAPK.

212 Java e DEX compilados, quatro novos cores com fonte/licença e patches, runtime de cinco preservado. N64 e NeoCD passaram na transferência de estado em dois processos. Gameplay Android e APK completo assinado pendentes; Dreamcast quatro, Dolphin Station, Wii U, Switch, PS2 e Saturn ainda precisam de integração nativa no APK. Não anunciar todas as plataformas prontas.

## Receitas

- `recipes/build_java.py`: JDK17/API34/D8 explícitos; mantém client DEX byte idêntico.
- `recipes/test_content_identity.py`: 10 verificações Java/Python da identidade CUE com suas faixas.
- `recipes/test_profiles.py`: 200 verificações do parser/presentação/portas.
- `tests/StationOnlineBiosTest.java.in`: 21 verificações reais do preparador de BIOS; compile com os dois jars da compilação e API34.
- `recipes/build_cores.py`: NDK r28c, fontes fixadas e patch NeoCD; resultados privados em diretório novo.
- `recipes/check_core_state.py`: compara transferência e sequência em dois processos de host. N64 requer `--frames 1200` para vídeo do fixture usado. ROMs/estados ficam privados.
- `recipes/package_candidate.py`: base completa R81 privada e assinatura original; acrescenta motores/controles/licenças, preserva todas as outras entradas. Não instala nem altera canais.

Usar Python 3.12+, saídas novas e, no PCAPK, E:. As bibliotecas já compiladas estão em `native/`; os arquivos de fonte correspondentes e licenças acompanham a entrega. Nenhuma BIOS proprietária ou ROM acompanha o pacote.
