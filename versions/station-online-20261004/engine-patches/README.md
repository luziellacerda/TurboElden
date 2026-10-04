# Patch de reprodução

Usar apenas `retroarch-station-all.patch`, consolidado sobre RetroArch69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576, com fontes normalizados para LF. Reaplicação sobre o ZIP oficial e igualdade do texto final dos seis arquivos comprovadas em evidence/retroarch-patch-replay.json. Os três patches incrementais são históricos, não devem ser reaplicados.

Inclui ALooper_pollOnce para NDKr28, argumentos diretos host/connect, remoção de serviços públicos opcionais e callback de socket realmente aberto. `application-process-guard.patch` é separado e pertence ao DEX original do app, não ao RetroArch. Execução Android pendente.
