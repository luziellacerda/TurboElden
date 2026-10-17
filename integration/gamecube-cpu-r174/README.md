# R174 candidata: processamento do GameCube online

O teste R173 permitiu entrar e jogar Mario Kart nos dois aparelhos. O usuário
relatou queda de quadros e lentidão. A R172 estável continua preservada.

## Evidência e hipótese a testar

Em 20 segundos da partida, o Motorola executou 14,83 s na thread de CPU e
14,63 s na de vídeo. Dos 4,88 s de sono da CPU, 4,81 s terminaram por ação
da thread de vídeo; apenas 0,017 s tiveram o cliente nativo de rede como
despertador. O Samsung apresentou esperas maiores pelo cliente de rede.
O relay permaneceu em estado de partida, mesmo epoch e duas conexões durante
as 240 amostras. Isso localiza a maior espera observada no pipeline do
Motorola; não prova que todo atraso de rede ou de outros jogos inexiste.

O SurfaceFlinger do Motorola apresentou cerca de 44–45 quadros/s em duas
janelas. Um teste temporário a 60 Hz não trouxe melhora nas cenas observadas;
a configuração original da tela foi restaurada. Essas janelas não repetem
uma corrida idêntica e não são um benchmark controlado de desempenho.

O [Dolphin oficial](https://github.com/dolphin-emu/dolphin/blob/5102a0339c2177575378107b76541e47cc52122d/Source/Android/app/src/main/res/values/strings.xml)
alerta que Dual Core no netplay pode causar problemas de desempenho. No
modo determinístico com Dual Core, o [FIFO](https://github.com/dolphin-emu/dolphin/blob/5102a0339c2177575378107b76541e47cc52122d/Source/Core/VideoCommon/Fifo.cpp)
também sincroniza o processamento de CPU e vídeo. A candidata testa
`Core.CPUThread=false` somente no GameCube online. Melhora física ainda não
comprovada; não promover esta candidata por causa da compilação ou do HTTP.

## Diferença delimitada

- Doa o APK R173 exato e preserva sua correção de entrada nas salas.
- Compila somente `StationDolphinCpuPolicy`; acrescenta duas instruções ao
  método efetivo de inicialização, após `configured=true` e antes de conectar.
  Mantém o restante do bytecode da sessão e suas classes auxiliares.
- Usa a API nativa já existente: camada CurrentRun 4 para definir a opção,
  camada Active 3 para confirmar o valor. Se não confirmar, falha antes de
  iniciar a conexão oficial. Nunca chama `save` nem escreve preferências offline.
- Wii recebe zero chamadas ao ajuste; PSX inputDelay8 e N64 são preservados.
  Resolução, qualidade gráfica, renderer, clock, áudio, buffers, transporte,
  controles, ROMs, saves e configurações de rede não são alterados.
- A versão e os marcadores de identidade precisam avançar porque o DEX35
  compartilhado muda. Os núcleos e dependências reais permanecem idênticos.

Os testes de contrato usam fixtures separadas, nunca incluídas no APK. A
receita confere a API NativeConfig real do doador, todas as classes fora do
escopo, os quarenta DEX, assinatura original e alinhamento. Binários e provas
privados ficam fora do Git. Cadastro, instalação e teste físico têm recibos
próprios; não executar os operadores históricos R173 novamente.

## Comparação física exigida

Mesmos dois celulares, Mario Kart local VS em sala nova e mesma região/edição.
Medir a apresentação e as esperas de CPU/vídeo na R174 e registrar o relato de
movimento, som e controles. Uma única corrida não homologa todos os jogos.
Se não melhorar, preservar a evidência e reverter o ajuste em uma revisão
sucessora de teste, mantendo dados e certificado. Não desinstalar para fazer
downgrade nem substituir a R172 estável automaticamente.
