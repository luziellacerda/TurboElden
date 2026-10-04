# Subpastas — entrega ao operador

O patch é aditivo sobre os arquivos StationLibrary/StationService conferidos contra o commit do servidor `a4814d453a1f193fcbe40a92c8690c4eb5d41fc9`. Preserva as validações online recentes desse commit. Não aplicar sobre uma base anterior que remova a implantação das salas.

`station-folders.patch` acrescenta apenas `FolderPath` ao índice/projeção assinada. `prepare_station_folder_index.py` gera outro índice usando raízes explícitas, preservando IDs, capas e descritores. Não existe raiz de ROMs presumida no código.

O handoff completo é publicado no **Servidor-pix**, branch `feat/station-subpastas-20261004`, arquivo `docs/station-android/HANDOFF-APP-SUBPASTAS-STATION-20261004.md`. Esse documento é APP → SERVIDOR, não uma resposta nem confirmação de implantação. O operador deve conferir os alvos efetivos e publicar o retorno solicitado.

O retorno anterior `a4814d4` relata as salas online já implantadas. Não confundir essa implantação com o metadado novo de pastas, que ainda depende de aplicação. Este trabalho Windows não implantou serviços Linux.
