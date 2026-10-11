# R124 — vídeos completos e ações no rodapé

Fonte completa derivada da R123 publicada (`76a8e34a1aa202dd277f0a1ed043beb436629209`). A montagem usa a R122 exata com as fontes atuais completas; não restaura Activities antigas. Candidato sem promoção estável.

## Alterações

- **Vídeos:** limite fixo de oito texturas deixava três das onze células do modo De lado sem imagem. O orçamento acompanha somente os vídeos únicos visíveis, entre oito e treze frames, com descarte de frames fora da janela ao reduzir o conjunto. Reta e Diagonal mantêm oito. Um único decoder, 720 × 720 RGB565, vídeos locais/uma passagem e menus 30 fps preservados. Onze frames usam cerca de 2,97 MiB adicionais; o teto transitório de treze usa cerca de 4,94 MiB adicionais. Nenhuma redução térmica foi medida nesta revisão.
- **Sua sala / Estou pronto:** ações no rodapé da coluna de textos; nomes, ocupação, sinopse e orientação organizados acima. Alvos de 48 dp, ações lado a lado quando cabem. Em telas baixas/fontes grandes, a rolagem já existente permite alcançar todos os botões. A capa e sua TextureView permanecem anexadas; reconstruir o rodapé não encolhe/reexpande a superfície a cada atualização.
- **Saída online:** título, ícone e consequência da saída mais claros; Continuar e Sair no rodapé separado dos textos. A chamada humana original e a confirmação foram mantidas. Menus pertencentes a outros processos de emulação não foram alterados.

## Escopo e conferências

Apenas três fontes produtivas diferem da R123: `StationRoomsActivity.java`, `StationExitPanel.java` e `native_system_video720.h`. O APK muda apenas `classes35.dex` e `libturbo_carousel.so` em relação à R123. `classes28.dex` e o frontend recompilado são idênticos à R123. Runtime `81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc`, manifesto, engines, controles, autoridade online, downloads, LEDs, cache e regras de economia permanecem preservados.

Provas isoladas executadas na R124: 746.220 verificações do orçamento real de frames; 32.755 de reuso/rodapé; 3.203 casos e 23.202 verificações de ações/start; 61 guardas do menu; 280 casos e 8.120 verificações de saída, mais dez guardas. As duas classes completas compilaram contra API34. Revisão independente conferiu 17 métodos de autoridade, 13 de lifecycle/reuso e quatro dependências da capa. Esses resultados não substituem pixels Android, gameplay, fontes ampliadas, ANR ou medição térmica.

## Artefato

APK local: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R124-20261011.apk`. SHA256 `aeeb2f8167a442db5a58b990cf6d45b613fab42b1e7a9bbc0bf3214b260420c4`, 2,217,098,632 bytes. Assinatura original v2/v3 e alinhamento 16 KiB conferidos. Instalado diretamente no Motorola; hash integral e dados originais preservados. Aprovação visual final e gameplay não declarados.

Fontes/staging/Java/recibos compilados em E:. Os binários nativos e temporários de montagem ficam em G: porque E: tinha somente42 MB livres; nenhum build anterior foi apagado. APK, imagens, objetos privados, chaves, seriais e logs do telefone ficam fora do Git. As receitas não executam testes automaticamente; `tests/` contém as provas correspondentes e provas herdadas históricas.

## Observação no Motorola

Abertura autenticada observada. No carrossel De lado, a capa principal e as dez pequenas apareceram, sem célula vazia nessa captura. Isso não valida reprodução contínua de todos os vídeos. Conferência física final do rodapé Sua sala e do painel de saída permanece pendente; provas isoladas e compilação constam acima. Nenhuma sala ou partida foi criada/iniciada pelo agente.
