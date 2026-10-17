# Correção de capacidade do catálogo — R175

O servidor já permite 20.000 itens, mas a R173/R174 ainda pede a rota antiga,
limitada a 4.096. Os 100 jogos GBA publicados na revisão 102 ficam fora dessa
primeira parte. O teste antigo de capacidade da integração NES não foi
incorporado ao APK atual.

Esta alteração parte do APK R174 assinado exato. A consulta pede 20.000 itens,
o leitor aceita esse limite e exige uma resposta de rede completa. A resposta
antiga, assinada e incompleta continua disponível para abertura offline; uma
resposta completa substitui o cache e atualiza a interface mesmo sem aumento
da revisão. O plano de capas usa o mesmo limite, com um único trabalhador e
as prioridades/cancelamentos existentes.

Quatro famílias Java são compiladas. Duas alterações pequenas são aplicadas
às classes efetivas da R174: a comparação do catálogo em StationFrontend e a
permissão da consulta GET em StationHttp. Nenhum transporte aninhado ou outra
instrução dessas classes é recompilado. O verificador confere todas as classes
fora desse escopo e as referências nos 40 DEX. Os três invólucros de identidade
dos motores são atualizados para refletir o payload; os núcleos/opções ficam
preservados, incluindo o atraso PSX R172 e a correção GameCube R174.

Saídas privadas: `/mnt/DADOS/station-build-r175-20261017`. A receita exige a
fonte congelada, o APK pai exato, os compiladores reais e a chave original.
Não publica no atualizador geral, não reinicia a API e não modifica ROMs,
licenças, saves, rede ou a referência estável R172.

Os testes exercitam o leitor real em 12.288/20.000 itens, o limite 20.001,
validações de assinatura/domínio/proprietário, cache e recuperação do corte
4.096→catálogo completo na mesma revisão. Exercitam 20.000 capas e os testes
anteriores de prioridade, cancelamento, pausa/retomada e limite de taxa.
Testes no computador não constituem prova de funcionamento no Android.
