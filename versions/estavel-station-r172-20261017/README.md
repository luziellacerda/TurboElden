# TurboStations R172 estável — 17/10/2026

Referência estável de recuperação aprovada pelo proprietário: “salva backup
como estavel”, depois de relatar “tivemos grandes melhoras”. Tag e ramo
`estavel-station-r172-20261017` preservam este ponto. A fonte congelada que
produziu o APK é `8317792fa231831f788cb10b7061bb11bc9fa97d`; o commit que
registra a estabilidade é posterior e não corresponde a outra compilação.

## Cópia privada

`/mnt/DADOS/station-estavel-r172-20261017` contém o APK original assinado,
cópia independente do doador R171, classpaths/recibos, assinatura original,
SDK36/build-tools36, NDKr28c/JDK21, kit R172, cadastro exportado do servidor e
release efetiva da API, provas de instalação/partida e bundles Git dos dois
repositórios. São cópias verificadas por SHA-256, no mesmo volume local; o
inventário e a verificação final estão nessa pasta. Dados privados e binários
não vão para o Git. Este checkpoint não é um backup do banco de licenças ou
de todos os sistemas deste PC.

## Identidade e teste observado

- APK `4a92627952a4f9673ff402667825fcb1f926aaf85a44bef7882559f000c56c5b`,
  2.714.238.050 bytes, versão14/`1.0.8-R172`, certificado original preservado.
- Moto g52 e Samsung A56: hashes do base.apk conferidos individualmente,
  atualização preservando UID e dados.
- Capcom vs.SNK VS: avanço nativo equivalente~59,9quadros/s e áudio~99,7–99,9%,
  contra~46,2/~77% na R171; relato humano de grande melhora. Não é medição de
  FPS renderizado ou teste de todos os jogos, controles/saída e anfitriões.
- Apenas PSX inputDelay4→8; custo nominal adicional~67ms de controle. Mesmos
  core/BIOS/clock/render/áudio; frameskip desligado e lógica N64 preservada.
- Servidor R172 efetivo:107 owners/18.864 perfis/13.457 modos, catálogo100/4.744;
  cadastro e consultas assinadas local/pública conferidos, sem restart.

[Manifesto](MANIFESTO-ESTAVEL.json) · [Restauração](RESTAURACAO.md).

Esta designação salva o ponto aprovado. Não remonta o APK, reinstala aparelhos,
publica oferta geral no atualizador ou modifica uma partida ativa. Tags e
referências estáveis anteriores permanecem disponíveis.
