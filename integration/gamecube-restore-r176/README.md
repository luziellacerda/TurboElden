# R176: retirar o teste R174 e preservar a expansão de catálogo R175

A R174 abriu nos dois mas o proprietário relatou lentidão e aparente piora.
Na corrida, o Moto apresentou27–30quadros/s; a principal CPU-GPU executou
19,740s em19,986s, quase99% de um núcleo. O Samsung esperou o cliente de
netplay. O ajuste foi confirmado nos logs dos dois e a rede manteve duas
conexões nas240amostras. Isso localiza a saturação nesta tentativa; não prova
a causa única da lentidão original nem exclui atrasos em outros recortes.

A compilação de catálogo R175 já estava em andamento independentemente.
Ela é preservada integralmente como doadora desta sucessora, incluindo
classes28.dex e libstation_frontend.so. Não editar ou reinstalar a R175
por consequência desta receita. A versão18 permite atualizar ambos sem
apagar dados; o servidor exige as quatro novas identidades e um kit exato.

Único delta funcional: repor o classes35.dex EXATO da R173, após provar que
somente Session$Session e o helper CPUThread diferem da R175. Assim as duas
instruções de hook e o helper são retirados, e as demais611classes continuam
idênticas. Nenhum core real é recompilado, nenhuma opção é escrita, nenhum
loop, timer, thread ou instrumentação nova é colocado no produto. A correção
de sala completa da R173 permanece.39DEX e13855entradas do R175 preservados.

A [publicação oficial2609](https://dolphin-emu.org/blog/2026/09/24/dolphin-progress-report-release-2609/)
explica o custo do netplay determinístico. A [nota2509](https://dolphin-emu.org/blog/2025/09/16/dolphin-progress-report-release-2509/)
explica por que o Dual Core permaneceu padrão no Android. O teste local
comprovou que núcleo único não resolveu este aparelho. Retirar o ensaio não
é declarar a lentidão original resolvida; a investigação continua.
