# Evidências R120

## Desta revisão

- build-r120.json e package-r120.json: compilação, payloads e comparação integral R119.
- switch-static-audit.json, original-launch-profile-table-r120.json e device-launch-routes-r120.json: referências estáveis/rotas e XML físico, somente leitura.
- launch-matrix-r120.json: cada plataforma, aliases, motor e disponibilidade; não gameplay.
- controller-presence-r120.json: 68 verificações isoladas.
- component-factory-isolated-r120.json: 43 verificações Java + 1.505 AXML.
- online-presentation-guards-r120.json: 13 guardas preservando métodos das salas.
- installation-motorola-r120.json, post-install-observation-r120.json e publication-r120.json são criados somente após concluir as etapas correspondentes.

## Histórico

Arquivos sem R120 ou identificados R119/R118/R117/R116 pertencem à base herdada. Não demonstram instalação, gameplay, temperatura ou validação visual R120. Diretórios privados, capturas/logs pessoais e binários são ignorados no Git.

Arquivos *-pre-alias.json são os recibos do artefato intermediário desta revisão. A instalação final usa o hash de package-r120.json; não selecionar o instalador intermediário.
