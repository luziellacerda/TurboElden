# Configurações dos emuladores Sony

O menu original aberto pelo robô conserva suas abas, valores, rolagem e ações. No rodapé da coluna de opções há duas ações estáticas, lado a lado: **PS3 — Configurar emulador** e **PS4 — Configurar emulador**. Uma linha dessa coluna é reservada às ações; a rolagem das opções considera o espaço restante. A coluna de abas e os outros emuladores permanecem iguais.

| Ação | Aplicativo conferido | Entrada pública |
|---|---|---|
| PS3 | aPS3e 2.43, versionCode 43 | `aenu.aps3e.QuickStartActivity` |
| PS4 | Bachata S4 0.2.4, versionCode 26100114 | `com.bachatas4.android.MainActivity` no pacote `com.bachatas4.android.github` |

As ações abrem o emulador oficial para que o usuário escolha suas configurações. As telas internas de configurações não são exportadas; a integração não tenta chamá-las diretamente. O PS3 exige Android 9/ARM64 e o PS4 Android 12/ARM64. Assinatura, versão, aplicativo habilitado e componente exportado/habilitado são conferidos antes da abertura, usando a política original sem mudanças.

O Intent externo é construído do zero: `ACTION_MAIN`, `CATEGORY_LAUNCHER` e componente explícito. Não inclui URI, MIME, extras, ClipData, grants, importação PKG ou lançamento de jogo. A operação interna `station.operation=settings` é tratada antes da verificação DEMO/arquivo. Se o aplicativo não estiver instalado, a tela oferece sua página oficial mediante toque do usuário. Não há instalação automática nem novos motores online.

JNI ocorre somente ao concluir o toque em uma das ações. A preparação dos guardas usa o Worker existente; o encaminhamento Android é postado na UI, sem esperar pela thread de renderização. Os dois botões usam as primitivas estáticas e a altura mínima existentes. Não há shader, animação, decoder, timer, polling, rede ou loop de fundo novos. O vídeo/música do frontend pausa no encaminhamento, como nos acessos de configuração já existentes.

## Ligação à compilação

`recipe/patch_sony_activity.py` já é chamado pelo compilador e transforma exclusivamente a Activity Sony original conferida. A política e o manifesto R128 ficam iguais. Não requer classe Java ou namespace adicional.

Depois de reproduzir e conferir o nativo R128, carregar `recipe/patch_sony_settings.py` e chamar:

```python
final_cpp, settings_header, settings_flags = settings_patch.patch_settings(
    changed_native, resolved['d0/native_settings.h'].read_bytes())
(native_out/'native_settings.h').write_bytes(settings_header)
native_source.write_bytes(final_cpp)
native_check['sonySettings'] = settings_flags
```

O `.cpp` permanece idêntico ao que recebeu o patch de arte Sony. Seu include entre aspas encontra primeiro o header gerado ao lado dele. O header original não é alterado. O build deve continuar conferindo o conjunto de exports e o alinhamento nativo, congelar a nova receita com as demais fontes e renovar as identidades compartilhadas. Não reutilizar recibos binários anteriores.

O patch do header exige SHA-256 `7d7e4d388319594d7bfc934105d1d09c75af09a3887f4b1f8bb1dcf14d9b3abb`, âncoras únicas e inversão byte a byte para a fonte original. Isso delimita as alterações de fonte. Não equivale a compilação, abertura física ou gameplay validados.
