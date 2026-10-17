# R171 candidata: latência do Wi-Fi na sessão PSX

Delta motivado pela lentidão reproduzida nos dois aparelhos com a R170 exata.
Na captura de 25 segundos, o motor executou cerca de 47,7 quadros/s, com
intervalos de até 85 ms. O relay encaminhou 4.746 mensagens em mediana de
0,291 ms e máximo de 0,554 ms. Na rede local, independente do túnel e do
emulador, o Samsung apresentou mediana de 34,45 ms e máximo de 111 ms.
Nenhum dos aparelhos mantinha um Wi-Fi lock durante a partida. Estes fatos
justificam um teste controlado; ainda não comprovam uma causa única.

O Android documenta o recurso para jogos em primeiro plano e tela acesa:
[Wi-Fi low latency](https://source.android.com/docs/core/connect/wifi-low-latency).
O sistema desativa a economia de energia do rádio enquanto o recurso está
ativo; as demais otimizações dependem do fabricante. O recurso pode aumentar
consumo de bateria. A temperatura precisa ser comparada em teste físico.

## Diferença produtiva

- `StationPsxSession` controla uma única `StationPsxWifiLatency` no ciclo de
  vida da sessão validada. Pausa local, segundo plano, falha terminal e saída
  humana liberam o recurso. Uma tarefa UI atrasada reavalia o estado atual.
- API 29+: `WIFI_MODE_FULL_LOW_LATENCY`; API 26–28: modo antigo `HIGH_PERF`.
  Não solicita permissão nova, muda a rede, habilita rádio ou faz reconexão.
  Ausência ou recusa do recurso não impede o jogo e não cria tentativas
  periódicas. Sem thread, timer ou trabalho adicional por quadro.
- Core, protocolo, buffer de quatro quadros, controles e opções são idênticos
  à R170. Não há rollback, aceleração de emulação ou alteração térmica nova.

## Montagem delimitada

Base R170 assinada: `42533ba2b53532be38872bcb97a07b0647e5a9b6091b565a1af7292f390be1c3`.
Somente duas famílias no `classes35.dex`; todas as classes externas preservadas
e referências conferidas contra as 40 partições reais. As 39 demais partições,
inclusive atualizador/downloads em `classes28.dex`, ficam byte a byte iguais.
Manifesto: apenas versão 12→13/`1.0.8-R171`, preservando todos os componentes,
permissões e SDK26/34. Registro e três marcadores renovam a identidade do
payload efetivo, mantendo fontes nativas, cores e políticas anteriores.
Exatamente seis entradas substituídas, zero adições/remoções no APK.

O classpath vem da compilação produtiva R170 congelada, com hashes fixos;
fixtures são exclusivas dos testes e não são empacotadas. A assinatura deve
usar a autoridade original recebida. Saídas e segredos ficam fora do Git.

## Provas e limite

Os 111 checks de sessão/launch/recurso e a compilação com SDK36 passaram.
Esses testes não simulam o rádio. É obrigatório conferir o modo efetivo no
Android e comparar quadros nativos, áudio, latência, temperatura e liberação
do recurso. Trocar o APK somente fora de partida ativa e preservar os dados.
Não publicar oferta geral, promover a estável ou afirmar desempenho corrigido
com base apenas na compilação ou no cadastro dos novos IDs.
