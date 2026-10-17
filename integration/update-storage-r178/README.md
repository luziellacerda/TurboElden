# R178: correção da consulta de espaço do atualizador

Os dois aparelhos R176 falharam com `SecurityException` antes do download.
O Android implementa `Files.getFileStore` lançando essa exceção. A prova USB
nos Android 33 e 36 reproduziu a recusa e confirmou `File.getUsableSpace`.

Esta sucessora da R177 troca apenas essa chamada em `StationAppUpdater`.
GameCube continua com buffer oito e seleção de CPU da R173. O protocolo,
a autorização, o conteúdo baixado, a assinatura e a confirmação do Android
são conservados. A R176 precisa receber a primeira correção por USB, pois
seu próprio atualizador não consegue baixar.

A receita fixa o APK R177, limita a mudança à classe real em classes28.dex,
confere todos os outros tipos e entradas e renova as identidades que vinculam
o APK. Os núcleos nativos reais e classes35.dex são preservados.

Referência: https://android.googlesource.com/platform/prebuilts/fullsdk/sources/+/refs/heads/androidx-constraintlayout-release/android-35/sun/nio/fs/UnixFileSystemProvider.java
