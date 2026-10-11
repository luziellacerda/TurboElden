# Configurações compactas e acesso aos emuladores Sony

O menu aberto pelo robô usa uma apresentação compacta de jogos: fundo escuro uniforme, destaque discreto na aba selecionada, separadores finos e valores em azul. As abas nativas, suas ações, os valores salvos e a rolagem continuam no mesmo motor.

O título, o controle de cor/Lottie, **Online** e **Voltar** dividem o cabeçalho. A faixa de cor separada foi removida para abrir espaço às opções. A coluna de abas ficou mais estreita; a coluna de opções ganhou largura. As linhas têm menos espaço entre si e fundos visualmente mais finos, mantendo a área lógica mínima de **48dp** calculada pelo código original. O número de linhas visíveis depende da resolução e densidade reais do aparelho; as demais continuam acessíveis por rolagem.

Na primeira linha da coluna direita, acima das opções, ficam duas ações lado a lado: **PS3 • ABRIR EMULADOR** e **PS4 • ABRIR EMULADOR**. Seus fundos estáticos têm detalhes azuis e violetas discretos. Essa linha pertence aos botões Sony: o início das opções, seu recorte, sua altura de rolagem e suas áreas de toque foram deslocados juntos para baixo dela. As opções nativas não desenham nem capturam toques sobre essa faixa.

**Efeitos gráficos** permanece visível na coluna esquerda e chama o mesmo painel original. A escolha **Com loop / Sem loop**, implementada separadamente, deve ficar nas opções de vídeos desse painel, junto do desligamento existente. Seu escopo é apenas o vídeo da célula em destaque no carrossel principal de plataformas; coleções não entram nesse comportamento. Esta receita de apresentação não muda preferências nem reprodução de vídeo.

## Desenho e estado do renderer

Na implementação anterior, o fundo Sony era desenhado depois do texto de Efeitos gráficos, e o segundo fundo depois do primeiro texto Sony. A primitiva `settingsConsoleCard` transforma seus vértices usando a matriz corrente; esses caminhos não repunham a matriz depois da chamada de fonte. A captura anterior mostrou os textos Sony sem fundos visíveis. Essa sequência é um risco concreto de estado compartilhado; a inspeção não prova uma causa única para o sintoma físico.

Agora cada fundo manual repõe a matriz original imediatamente antes de desenhar. Todos os fundos manuais são desenhados antes de seus textos. A mesma primitiva estática, programa e conjunto de vértices do frontend são reutilizados. Não há shader, framebuffer, filtro, animação, alocação por quadro ou rotina de fundo nova.

Os textos Sony continuam pertencendo ao modal: recebem a mesma exclusão de desenho automático usada por `settingsEffectsLabel`. Seu desenho manual ocorre somente com configurações abertas. A inversão exata da alteração de duas condições em `textRenderHook` continua exigida, evitando que esses textos apareçam sobre a sinopse ao voltar de outro aplicativo.

## Acesso externo

| Ação | Aplicativo conferido | Entrada pública |
|---|---|---|
| PS3 | aPS3e 2.43, versionCode 43 | `aenu.aps3e.QuickStartActivity` |
| PS4 | Bachata S4 0.2.4, versionCode 26100114 | `com.bachatas4.android.MainActivity` no pacote `com.bachatas4.android.github` |

As ações abrem o emulador oficial para o usuário escolher suas configurações. As telas internas de configurações não são exportadas e não são chamadas diretamente. O PS3 exige Android 9/ARM64 e o PS4 Android 12/ARM64. Assinatura, versão, aplicativo habilitado e componente exportado/habilitado continuam conferidos pela política original.

O Intent externo é construído do zero: `ACTION_MAIN`, `CATEGORY_LAUNCHER` e componente explícito. Não inclui URI, MIME, extras, ClipData, grants, importação PKG ou lançamento de jogo. A operação interna `station.operation=settings` é tratada antes da verificação DEMO/arquivo. Se o aplicativo não estiver instalado, a tela oferece sua página oficial mediante toque. Não há instalação automática nem motores online Sony.

JNI ocorre somente ao concluir um toque Sony. A preparação dos guardas usa o Worker existente; o encaminhamento Android é postado na UI sem esperar pela thread de renderização. O vídeo/música do frontend pausa no encaminhamento, como no acesso anterior. Controles, autenticação, sessão, economia, caches, LEDs e orçamento de quadros não são alterados pelo redesenho.

## Ligação à compilação

`recipe/patch_sony_activity.py` transforma exclusivamente a Activity Sony original conferida. A política e o manifesto R128 permanecem iguais. Depois de reproduzir e conferir o nativo R128, o compilador chama:

```python
final_cpp, settings_header, settings_flags = settings_patch.patch_settings(
    changed_native, resolved['d0/native_settings.h'].read_bytes())
(native_out/'native_settings.h').write_bytes(settings_header)
native_source.write_bytes(final_cpp)
native_check['sonySettingsMenuReceipt'] = settings_flags
```

O `.cpp` recebe apenas a exclusão dos dois textos Sony no guard existente. Seu include entre aspas encontra o header gerado ao lado dele; o header original não é escrito. O build continua conferindo exports, alinhamento nativo e identidade das fontes, e deve renovar as identidades compartilhadas do novo pacote.

O patch exige SHA-256 original `7d7e4d388319594d7bfc934105d1d09c75af09a3887f4b1f8bb1dcf14d9b3abb`, âncoras únicas e inversão byte a byte. O recibo informa explicitamente cabeçalho compartilhado, faixa Sony superior, viewport separado, área lógica de 48dp, matriz reposta por fundo e desenho de fundos antes de textos.

Nesta alteração foram inspecionadas a fonte e a sintaxe da receita. A compilação e a conferência física do novo desenho ficam a cargo da execução final; a observação da versão anterior não valida este redesenho.
