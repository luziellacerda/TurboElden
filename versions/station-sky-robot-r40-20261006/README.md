# R40 — céu e robô

APK preparado em G: `TurboStations-Ceu-Robo-R40-20261006.apk`, SHA da803b3eb7c0fb24b272795449c5527d752f71e8809d132cae3300071a3c5678. Não instalado isoladamente; R41 o usa como base.

Azul afeta somente céu e iluminação branca das nuvens. Interface original preta mantida. Seletor de tema no canto inferior direito. Robô Lottie acima do Jogar online percorre sua animação original em loop a velocidade normal (30 atualizações visuais/s), para quando não visível. Sem worker/timer extra ou alterações de motores.

Fonte completa native/;build/test/package_r40.py e verify_sky_gl.py, evidências e build-result.json. Restauração depende dos objetos/assets R39 e W16/W22 identificados no native-build-input.json, com hashes congelados.115072 checks de helpers/renderer simulado; regressões de pesquisa/folders/ribbon/geometry e shader GLES2 real PC passaram. Não prova visual/FPS no Android. SO d7839c709ab4e241a74355fcfa49dbb222328b0e61eb198ed74892cca38d788b.13.179 entradas preservadas sobreR39. Ler resultado/recibos antes de atribuir instalação.
