Ibiraté - APP Analises
Plugin desenvolvido para automatização de processos de conformidade ambiental, focado na delimitação de Áreas de Preservação Permanente (APP) e faixas de recomposição.

Desenvolvimento Técnico
Este plugin foi desenvolvido por Poliana Cursino Betella e Pedro Cursino Betella Gomes como uma solução de geoprocessamento aplicada às rotinas técnicas da Ibiraté Consultoria.

Funcionalidades
- Cálculo de Precisão: Identificação automática de fuso UTM para garantir buffers de 50m, sem distorções de escala.
- Conformidade Legal: Parâmetros baseados no Código Florestal Brasileiro (Lei nº 12.651/2012).
- Uso Consolidado: Geração dinâmica de áreas de recomposição baseada em Módulos Fiscais.
- Ferramentas de Auxílio: Calculadora de Módulos Fiscais integrada e link para base de dados da Embrapa.

Instalação
- Copie a pasta do plugin para o diretório de plugins do QGIS.
- Ative o "Ibiraté - APP Analises" no Gerenciador de Complementos.

Como Usar o Plugin
- Prepare as Camadas: No QGIS, adicione suas camadas de Nascentes (Ponto) e Cursos d'Água (Linha).
- Selecione o Imóvel: Insira a camada de polígono que representa o Limite do Imóvel.
- Configuração Automática: Clique em "Preencher com Selecionadas" para o plugin identificar as camadas ativas.
- Parâmetros Legais: Selecione a largura do rio ou marque "Analisar Uso Consolidado" para calcular faixas de recomposição baseadas em Módulos Fiscais.
Resultado: O plugin gerará automaticamente as camadas de APP, áreas remanescentes e faixas de uso consolidado, já cortadas no limite do imóvel.

Contato dos Desenvolvedores:
Poliana Cursino Betella | betella.poliana@gmail.com
Pedro Cursino Betella Gomes | pedro.cursino.betella.gomes@gmail.com
www.ibirate.com.br
