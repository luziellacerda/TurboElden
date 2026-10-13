# Downloads diretos protegidos — candidata sobre R139

**Servidor direto ativo; APK candidato compilado unsigned, ainda sem assinatura,
instalação ou medição física de velocidade.** Não substituir a R139 instalada
por este artefato sem a chave original e a conferência da assinatura.

`StationHttp` usa `downloads-station.lzgames.com.br` somente no GET canônico de
artefato. As demais rotas continuam em `app.lzgames.com.br`, com o pin antigo.
A origem nova conserva a validação da CA pública, hostname e pin SPKI próprio.
Bearer, assinatura da requisição e correlação são preservados; redirects continuam
proibidos. Não há IP externo fixo no fonte, fallback do mesmo grant, aumento de
permissões ou mudança na autorização da API. O servidor atualiza seu registro DNS
automaticamente quando o IPv4 público muda e renova o certificado conservando a chave.

O donor assinado é a R139 exata:
`19acdeceef86bc66c2475300cbd142da783850c02f5a9e2068d8652ef8523164`.
Certificado Android original exigido:
`7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

O transporte deriva da fonte histórica R124 preservada
(`StationHttp.java` SHA256 `9f897c3d30465f9bc77b4d71d02a051746788b7a9aade4b8e0a25ba3ef8a4460`).
Só as famílias HTTP e a nova identidade de download entram no overlay D8. A classe
`StationHttp$ResponseBody` é copiada do donor para conservar o controle original
de EOF/tamanho e a reutilização da conexão. `ScopedHttpDex.java` compara o smali
canônico, com debug e valores estáticos, de todas as 266 classes preservadas.
Partição final: 272 classes, contra 271 no donor.

O fingerprint dos wrappers existentes vincula DEX28. Por isso `build_wrappers.py`
renova seus marcadores e quatro IDs PSX/N64/GameCube/Wii, mantendo todas as políticas
e as sete fontes PSX originais por SHA. Exige o mesmo NDK r28c e compara exports,
dependências, SONAME e alinhamento 16 KiB. N64/Dolphin são marcadores de identidade;
nenhum core de emulador é recompilado. Os nove descritores RetroArch da R139 ficam
exatos. Esses quatro IDs novos ainda não foram registrados no servidor.

`package_direct.py` reutiliza o assembler clássico existente com cinco substituições
estritas: DEX28, três wrappers e `engines.json`. Verifica o mapa de 345 payloads
vinculados, freeze das fontes, políticas e hashes antes/depois da montagem e faz
leitura independente de todas as entradas. Preserva 13.855 entradas, 39 DEX, Manifest,
recursos, controles, opções, JNI do frontend, runtime RetroArch, catálogo e capacidade
NES atualmente instalada. Não inclui testes, fixtures, SDK, chaves, ROMs ou BIOS novos.

## Evidência atual

- Java8/API36 compilado; JAR produtivo fechado com quatro classes, D8/API28 sem avisos.
- 43 checks de host: seleção da origem, prova/sessão, pooling, cancelamento,
  método/path inválidos e recusa de redirects/Location.
- Três handshakes TLS reais com o certificado público do serviço: origem/pin corretos
  aceitos; pin diferente e hostname diferente recusados.
- DEX28 compilado; 266 classes preservadas por comparação canônica.
- Três wrappers renovados com NDK r28c, exports/dependências originais e LOAD 16 KiB.
- APK unsigned montado e todas as entradas relidas; ZIP clássico, sem ZIP64.
- Zipalign 16 KiB passou e os cinco payloads alterados foram conferidos novamente.

APK unsigned inicial: SHA256
`4165acec63b1ec33d9532afb4b5a78b9d84a595fa333cc029882ecb684c4bade`,
2.712.262.321 bytes. Este SHA identifica a montagem anterior ao zipalign e à assinatura;
não é o hash de um APK instalável ou publicado. Materiais privados permanecem fora do Git.

Artefato alinhado ainda unsigned: SHA256
`d8ac31fa84ea1a8bf704878bf740e03599524d342474ef12ecc9a757ed08c805`,
2.713.640.743 bytes. Assinatura e atualização USB seguem pendentes.

## Conclusão necessária no aparelho

Receber a chave original do operador, alinhar/assinar e conferir o certificado v2/v3
e todas as entradas finais. Instalar por atualização no aparelho autorizado ocioso,
preservando UID/dados/Keystore/licença/jogos/saves. Não interromper partida ou download.
Atualizar o manifesto USB somente após definir o APK final assinado.

Conferir autorização, download completo e SHA, grant expirado/reuso recusados,
cancelamento e nova autorização para retomar. Comparar velocidade em rede externa
com origem direta e antiga usando grants diferentes e o mesmo conteúdo. Validar
login/catálogo/capas na origem antiga. Não presumir homologação física ou ganho de
velocidade a partir dos fixtures ou dos testes públicos sem autorização.
