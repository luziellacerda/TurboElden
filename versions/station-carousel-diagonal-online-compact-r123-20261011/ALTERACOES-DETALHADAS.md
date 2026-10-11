# R123 — três estilos de carrossel e menus refinados

## Carrossel

Escolhas Reta/Diagonal/De lado. Reta conserva a geometria anterior; Diagonal inclina apenas células fora de evidência. De lado aplica perspectiva às células não selecionadas usando a matriz do shader existente; toque e recorte seguem a mesma projeção. A revisão solicitada inverte a orientação e apresenta até dez vizinhas, com retorno ao começo da lista e sem duplicatas quando há menos itens. O espaço entre as capas acompanha a largura projetada. Reta e Diagonal mantêm seis vizinhas. A capa principal, resolução, UV/filtros, LEDs e desenho da faixa INSTALADO permanecem.

Apenas De lado com efeitos de células ativos usa até treze prioridades de capas, cobrindo as dez vizinhas, a selecionada e a transição. Os demais estilos mantêm nove. A fila Java e o trabalhador único, uma solicitação nativa de capa por vez, revelação incremental e caches existentes permanecem. Não há novo vídeo, shader, timer ou decoder. Quatro capas adicionais exigem desenhos e texturas adicionais; o consumo resultante não foi medido. Preferência separada e ponte atômica de apresentação; o contrato anterior de mask/mode/revision não é reorganizado.

Referência local: TURBORAMAx/gamecarousel-approved-dashboard.xml com tipo coverflow. O XML não informa o ângulo Y ou a distância de perspectiva; a adaptação Android usa 45 graus e distância focal de 1,2 vezes a largura, escolhas documentadas. O renderer correspondente não está disponível na referência consultada; não é uma alegação de reprodução exata do renderer PC. Ver revisão da geometria e testes R123.

## Configurações de efeitos

Painel reorganizado a partir da captura real do Motorola: cabeçalho compacto, controles alinhados, ambiente e carrossel em seletores segmentados e interruptores em linhas menores. Mantém as opções, valores salvos, retornos e alvos de toque; não redefine preferências por consequência do novo desenho.

## Online

Navegação lateral plana e mais compacta, com ícones, seleção e foco; a revisão remove o preenchimento das caixas inclusive no estado desativado observado. Opções de modo/quantidade recebem o espaçamento interno depois do fundo; ações ficam lado a lado conforme a largura. Sua sala destaca participantes e estado; remove o título e o aviso duplicados. Detalhes ficam disponíveis pelo título. Mantém alvos de toque48dp; layouts estreitos/fontes grandes podem usar quebra segura, sem ocultar controles.

Um único Iniciar na sala envia o mesmo comando. Antes de enviar, o worker revalida participantes/prontidão, identidade do snapshot exibido e transporte. Fingerprint local inclui também membros/prontos dos contratos legados; isto não altera payload ou protocolo. Ready, preparação, criação confirmada, entrada, lançamento e checagens de segurança permanecem. Nenhuma partida é iniciada pela compilação ou instalação.

## Componentes preservados

Base exata R122, incluindo tema Ondas escuro/azul, avisos de espaço e central de downloads. Reuso de capas/TextureView e coordenação GPU R121, loading preto, vídeos locais,30FPS somente menus, cache/preload/lifecycle, runtimes, engines, autenticação, controles e dados permanecem. A biblioteca frontend muda para a ponte UI de estilo e o plano limitado das dez capas visíveis; não é motor novo e não exige registro no servidor. Manifesto/Application/factory existentes mantidos. Nenhuma alteração de servidor.

## Conferência e reprodução

Provas host/compilação são separadas de gameplay e consumo físico. Recibos de versões herdadas são históricos. R123 é candidata, sem promoção dos canais estáveis. Receita exige R122 exata, fontes/inputs congelados e certificado original. Quatro payloads UI podem mudar: DEX28, DEX35, carousel e frontend bridge; todas as outras entradas precisam ser byte idênticas. Temporários em E:, montagem/final em G:. Código/documentos/recibos agregados públicos; APK/mídias/ROM/BIOS/chaves/logs/capturas/dados pessoais locais.
