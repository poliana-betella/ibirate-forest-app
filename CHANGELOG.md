# Changelog

Todas as mudancas notaveis deste projeto serao documentadas neste arquivo.

O formato e baseado em Keep a Changelog (https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao Versionamento Semantico (https://semver.org/lang/pt-BR/).

## [1.6.0] - 2026-11-07

### Corrigido
- Fuso UTM agora é identificado automaticamente a partir da localização do imóvel (SIRGAS 2000 / UTM 18S–25S e 18N–22N; WGS 84 / UTM fora do Brasil). Antes, projetos em coordenadas geográficas sempre usavam o fuso 23S (EPSG:31983), distorcendo os buffers de imóveis em outros fusos; e projetos em CRS métrico usavam o CRS do projeto mesmo que fosse de outro fuso.
- O seletor de largura do rio não é mais travado em "< 10 m" quando "Analisar Uso Consolidado" está marcado. Antes, a camada 1_APP saía sempre com 30 m nesse modo, mesmo em rios mais largos.
- Faixa de recomposição em curso d'água para imóveis acima de 4 módulos fiscais segue o Decreto 7.830/2012 (art. 19, § 4º): 20 m para 4 a 10 MF em rios de até 10 m; nos demais casos, metade da largura do rio, com mínimo de 30 m e máximo de 100 m. Antes, rios com mais de 10 m eram tratados como se tivessem até 10 m.
- Erros da análise passam a aparecer na barra de mensagens do QGIS (antes só eram impressos no console e o usuário não via).
- Ao desativar o plugin, o painel lateral também é removido.

### Adicionado
- Campo de largura exata do curso d'água, exibido só quando a regra de "metade da largura" se aplica, com validação contra a faixa de largura selecionada.
- Prévia da faixa de recomposição que será aplicada (rio e nascente) antes de gerar a análise.
- Validação de entradas (camada do imóvel obrigatória; ao menos uma camada de rios ou nascentes) e resumo das distâncias e do CRS usados ao final.

## [1.5.0] - 2026-03-17

### Adicionado

Plugin QGIS "Ibirate - APP Analises": geracao automatizada de buffers de Area de Preservacao Permanente (APP) e faixas de recomposicao (Uso Consolidado), conforme o Codigo Florestal Brasileiro (Lei no 12.651/2012).

Deteccao automatica de UTM/CRS metrico para calculo de buffers sem distorcao de escala.

Calculadora auxiliar de Modulos Fiscais (MF) e atalho para consulta de referencia na Embrapa.

Preenchimento automatico das camadas de entrada a partir da selecao ativa no painel de camadas do QGIS.

### Alterado

Limpeza de arquivos de template gerados automaticamente (Plugin Builder) que nao eram usados pelo plugin.

### Removido

README.html gerado automaticamente, substituido por README.txt.
