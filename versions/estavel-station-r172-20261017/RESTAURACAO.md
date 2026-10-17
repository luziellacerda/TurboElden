# Restauração do checkpoint R172

1. Leia `MANIFESTO-ESTAVEL.json` e `VERIFICACAO-FINAL.json` na cópia privada.
   Confira o SHA-256 do APK contra
   `4a92627952a4f9673ff402667825fcb1f926aaf85a44bef7882559f000c56c5b`.
   `INVENTARIO-SHA256.json` fixa arquivos e links do backup; os bundles Git
   foram verificados pelo Git e os commits congelados estão incluídos.
2. Use o APK assinado guardado em `apk/TurboStations-Premium-R172-ESTAVEL.apk`.
   Não recompile ou reassine para fazer esta restauração. Fora de uma partida
   ou download ativo, atualize preservando os dados quando a versão Android
   instalada for compatível com a versionCode14. Não desinstale, limpe dados
   ou force downgrade de um aparelho que já tenha versão posterior.
3. Recupere o código com `git clone -b estavel-station-r172-20261017` seguido
   do caminho de `codigo/TurboElden-R172-ESTAVEL.bundle` e da pasta de destino.
   O bundle `Servidor-pix-R172-ESTAVEL.bundle` segue o mesmo procedimento.
   Tags antigas não devem ser movidas para coincidir com esta revisão.
4. O APK contém os motores exatos cujo cadastro R172 está em
   `servidor/cadastro-r172`. O kit exato e a release efetiva da API estão no
   backup. Compare com o servidor vigente antes de qualquer recuperação;
   não execute novamente operadores históricos nem sobrescreva cadastros,
   licenças ou catálogo mais recentes. A transação protegida do Station usa
   autenticação Linux e `scan.lock`, preservando todas as versões anteriores.
5. Para uma compilação sucessora, os insumos exatos estão em `compiler` e as
   receitas no commit congelado8317792. Conserve a assinatura e os hashes.
   Os recibos originais são evidência histórica imutável; a cópia não executa
   automaticamente receitas ou publicação. Uma reconstrução em outro PC deve
   ser validada antes de ser tratada como byte idêntica ou instalada.

A aprovação estável é do proprietário para o cenário observado. Permanecem
os limites do piloto descritos no manifesto. A exportação do cadastro não
inclui banco de licenças, credenciais de produção, ROMs ou todo o PC.
