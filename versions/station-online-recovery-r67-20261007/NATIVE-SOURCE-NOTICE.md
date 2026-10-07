# Origem do runtime

RetroArch upstream `69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576`; [fonte e licença upstream](https://github.com/libretro/RetroArch/tree/69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576). Manter os avisos/copyright/licenças existentes. Hooks Station desta pasta são publicados sob GPL-3.0-or-later juntamente com a receita e patches, para reprodução da fonte modificada.

Os patches `retroarch-station-all.patch` e `retroarch-station-auto-password.patch` foram conservados byte a byte da entrega TurboElden250a3e51a2876175155d148235af1fc402b84d08. `retroarch-station-recovery.patch` equivale à aplicação de `recipes/patch_native.py` sobre essa base; conferência por SHA no manifesto. O patch atua no runtime, não modifica os cores/libretro incluídos. Esses cores conservam suas licenças e fontes apontadas nos manifests das engines anteriores.
