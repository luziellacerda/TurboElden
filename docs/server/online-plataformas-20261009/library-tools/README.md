# Importador automático Station — fonte da publicação de 10/10/2026

Snapshot completo do scanner e dependências Python desta entrega. A produção já está aplicada; consulte o handoff e o relatório `ps2-switch-publicados-20261010.json`. Não reaplicar operadores históricos ou copiar a configuração privada do servidor para o APK.

O scanner usa Python 3/Pillow e a configuração privada indicada pela unidade systemd. PS2 e Switch usam a opção explícita `rawStorage:readonly-hardlink`, `artifactMode:single-rom` e `copyRawOnce:true`. A origem e o armazenamento precisam estar no mesmo volume. A unidade deve executar como root e ter escrita nas duas pastas de origem e no armazenamento protegido; a API mantém seu acesso de leitura. Arquivo publicado vira root/0444. Substituir a ROM pelo nome com um arquivo novo preserva downloads anteriores.

Novos jogos são reconhecidos depois de duas observações estáveis e idade mínima de 20 segundos. Arte deve ficar em `media/revista` com o nome exato da ROM, ou ser vinculada pelo seed. JPEG RGB 480×720 conforme é preservado byte a byte. Metadados vêm de XML/seed/overrides; capas não são escolhidas por proximidade textual.

Registros de identidades, perfis e modos preparados usados na qualificação precisam respeitar o `outputDirectory` da instância. A primeira sombra recusou um arquivo de modos fora da sua própria pasta e foi revertida antes da publicação; a qualificação final usa uma cópia local e preserva o registro de produção.

`tests/test_readonly_raw.py` verifica inode, permissões, escritor aberto, origem substituída, symlink, aliases graváveis, outro volume e cópia padrão. São testes de armazenamento do servidor; não são emulação ou gameplay Android. O lote HTTP usa uma licença sintética própria, que foi removida.
