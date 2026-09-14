# Memoria do Projeto FarmTech Solutions - Agrosaas (FIAP - Fase 1)

## Contexto Geral
- Startup: FarmTech Solutions
- Objetivo: Desenvolver uma solucao para migracao de uma fazenda para a Agricultura Digital.
- Curso/Contexto: FIAP - Fase 1

---

## REGRA FUNDAMENTAL E OBRIGATORIA
- NUNCA UTILIZAR EMOJIS em qualquer arquivo do projeto, seja no codigo Python, R, scripts de terminal, documentação Markdown, arquivos HTML, TXT, mensagens de log ou comentarios. Usar apenas texto limpo em caracteres padrao.

---

## Requisitos e Funcionalidades

### 1. Aplicacao Python (src/python/main.py)
- Culturas Atendidas (2 tipos):
  - Cultura 1: Cafe (Area Retangular / Calculo por Ruas e Pulverizacao/Adubacao)
  - Cultura 2: Milho (Area Trapezoidal / Adubacao por Hectare)
- Calculo de Area de Plantio:
  - Suporte a figuras geometricas distintas (Retangulo para Cafe, Trapezio para Milho).
- Manejo de Insumos:
  - Calculo de dosagem (mL/metro x metros por rua x quantidade de ruas = Total de Litros/kg necessarios).
- Estruturas de Dados:
  - Dados organizados obrigatoriamente em vetores/listas paralelas.
- Menu Interativo (Loop while + Decisoes if/elif/else):
  1. [1] Entrada de dados (Cadastrar nova area/manejo).
  2. [2] Saida de dados (Exibir relatorio/relatorios cadastrados no terminal).
  3. [3] Atualizacao de dados (Editar um registro em uma posicao especifica do vetor).
  4. [4] Delecao de dados (Remover um registro em uma posicao especifica do vetor).
  5. [5] Sair do programa.

---

### 2. Aplicacao em R (src/r/analysis.R e src/r/weather.R)
- Analise Estatistica Basica (analysis.R):
  - Leitura dos dados de manejo/area.
  - Calculo estatistico: Media, Desvio Padrao, Minimo, Maximo, Mediana.
- Diferencial ("Ir Alem"): Conexao com API Meteorologica (weather.R):
  - Conexao via R (usando jsonlite / httr ou url) a uma API publica sem chave (Open-Meteo API).
  - Coleta e exibicao formatada de dados climaticos no terminal em texto simples (SEM EMOJIS).

---

### 3. Formacao Social (Resumo de Artigo)
- Artigo: Embrapa - CAP8.pdf
- Formatacao:
  - Maximo 1 folha A4
  - Fonte Arial 11
  - Espacamento 1.0 entre linhas
  - Margens direita e esquerda: 2 cm

---

### 4. Entregaveis e Estrutura do Pacote (.ZIP)
- Codigo fonte em Python (.py)
- Script de analise e API em R (.R)
- Resumo do artigo (.pdf, .odt ou .html)
- link_video.txt (Contendo link do video no YouTube - nao listado, ate 5 min demonstrando a execucao)

---

## Tecnologias e Diretrizes de Codigo
- Python: 3.x puro (sem bibliotecas externas pesadas para o menu principal).
- R: jsonlite, httr (para API) e funcoes nativas de estatistica (mean, sd, summary).
- Git/GitHub: Versionamento de codigo colaborativo.
- FORMATACAO: Sem emojis em todo o repositorio.
