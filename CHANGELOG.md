# Changelog

Todas as mudancas notaveis deste projeto serao documentadas neste arquivo.

O formato e baseado em Keep a Changelog (https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao Versionamento Semantico (https://semver.org/lang/pt-BR/).

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
