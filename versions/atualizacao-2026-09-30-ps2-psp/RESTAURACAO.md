# Pastas exatas e reconstrução

## Arquivos locais

| Conteúdo | Caminho |
| --- | --- |
| Fontes ativos | `E:\ESTUDO APK\work\native-carousel\implementation` |
| Integração PS2 | `E:\ESTUDO APK\work\native-carousel\implementation\ps2-integration` |
| Integração PSP | `E:\ESTUDO APK\work\native-carousel\implementation\psp-integration` |
| APK PS2 intermediário | `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-PS2-ARMSX2-2.7.2.apk` |
| APK final instalado | `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-PSP-PPSSPP-1.20.4.apk` |
| Estável preservada | `E:\ESTUDO APK\estaveis\2026-09-30-dolphin-flycast\TurboramaStation-ESTAVEL-dolphin-flycast.apk` |

Consulte MANIFESTO.json para todos os hashes. Atualização final em avaliação; não substituir a identidade da estável.

## Dependências e ordem

1. Materializar os fontes da tag estável usando seu `restaurar_fontes.py` em uma pasta nova em E:. Sobrepor `snapshot/implementation` desta revisão. A base binária privada, mídias e a assinatura original são necessárias: clonar o Git sozinho não reconstrói o aplicativo completo.
2. Usar os doadores oficiais identificados em `ps2-integration/provenance.json` e `psp-integration/provenance.json`. Conferir seus hashes antes de decodificar. Preservar licenças incluídas em `upstream`.
3. Ferramentas: Python 3, JDK17, Apktool 3.0.3, Android build-tools35, android.jar34, LLVM e NDKr28c. Os caminhos estão nos scripts. Adaptar os caminhos conscientemente quando restaurar em outra pasta. Temporários sempre em E:.
4. Para cada integração: decodificar o doador em `current-decoded`. Criar `frontend-sparse.apk` com AndroidManifest.xml, resources.arsc, classes.dex e res/ da base e decodificar em `frontend-decoded`. Os inventários `base-classes.json` foram obtidos de todos os DEX da base, não somente do sparse.
5. Executar `prepare.py`, depois `integrate.py`, nessa ordem, para gerar recursos separados, manifesto e ponte Java. `prepare.py` recria `merged`; não executá-lo depois de integrar. Compilar `merged` com Apktool para `merged-template.apk`, cache framework e temporários em E:.
6. Para PS2 usar como base o APK estável exato 55cd54a3. Para reconstruir o módulo intermediário PS2, colocar `intermediate-ps2/native_carousel.cpp` na raiz dos fontes, com `native_ps2.h` e dependências da estável. Executar `build_native.py`, depois `ps2-integration/package.py`.
7. Para PSP, restaurar `snapshot/implementation/native_carousel.cpp` desta revisão, com os dois headers novos; executar `build_native.py`. Preparar/integrar PSP usando a base PS2 exata 6e76035e; executar `psp-integration/package.py` após compilar o template.
8. Os scripts publicados de empacotamento usam `TURBORAMA_KEYSTORE`, `TURBORAMA_KEY_ALIAS`, `TURBORAMA_STORE_PASSWORD` e `TURBORAMA_KEY_PASSWORD` no ambiente. Valores e chave não são publicados. Essa parametrização é a única alteração de publicação nos scripts de empacotamento; a cópia ativa local foi preservada.
9. Os scripts exigem hashes exatos da base. Uma reconstrução pode produzir APK com hash diferente por metadados/assinatura; não remover silenciosamente as verificações. Para repetir a saída PSP documentada, usar o intermediário PS2 privado identificado no manifesto.

Os motores oficiais não foram recompilados integralmente do C++; a ponte Java e o módulo nativo próprios foram compilados. O C++ completo do frontend original não está disponível no Git.

## Restauração no aparelho

Somente fora de uma partida, instalar o APK escolhido com a mesma assinatura por atualização (`adb install -r`). Não desinstalar, limpar dados ou sobrescrever saves. A entrada pública é `org.emulationstation.frontend/.auth.LoginActivity`; a sessão é recuperada pelo aplicativo. A estável continua disponível no caminho acima.

## Pendências

Conferir configurações, abertura de jogo e retorno no PSP. PS2 tem jogo e retorno observados, mas não benchmark. Não rotular esta atualização como estável antes da aprovação do mantenedor. Handoffs antigos dentro da base são históricos; esta revisão e seu manifesto identificam o APK instalado agora.
