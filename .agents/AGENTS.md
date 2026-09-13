# Memória do Projeto FarmTech Solutions - Agrosaas (FIAP - Fase 1)

## Contexto Geral
- **Empresa/Startup:** FarmTech Solutions
- **Objetivo:** Desenvolver uma solução para migração de uma fazenda para a Agricultura Digital.
- **Curso/Contexto:** FIAP - Fase 1

---

## 📋 Requisitos e Funcionalidades

### 1. Aplicação Python (`src/main.py` ou `app.py`)
- **Culturas Atendidas (2 tipos):**
  - Cultura 1: Café (Área Retangular / Cálculo por Ruas e Pulverização/Adubação)
  - Cultura 2: Milho (Área Trapezoidal ou Circular / Adubação por Hectare ou Linha)
- **Cálculo de Área de Plantio:**
  - Suporte a figuras geométricas distintas (ex: Retângulo para Café, Trapézio/Círculo para Milho).
- **Manejo de Insumos:**
  - Cálculo de dosagem (ex: mL/metro x metros por rua x quantidade de ruas = Total de Litros/kg necessários).
- **Estruturas de Dados:**
  - Dados organizados obrigatoriamente em vetores/listas.
- **Menu Interativo (Loop `while` + Decisões `if/elif/else`):**
  1. `[1]` Entrada de dados (Cadastrar nova área/manejo).
  2. `[2]` Saída de dados (Exibir relatório/relatórios cadastrados no terminal).
  3. `[3]` Atualização de dados (Editar um registro em uma posição específica do vetor).
  4. `[4]` Deleção de dados (Remover um registro em uma posição específica do vetor).
  5. `[5]` Sair do programa.

---

### 2. Aplicação em R (`src/analysis.R` e `src/weather.R`)
- **Análise Estatística Básica (`analysis.R`):**
  - Leitura dos dados de manejo/área.
  - Cálculo estatístico: Média, Desvio Padrão, Mínimo, Máximo, Mediana.
- **Diferencial ("Ir Além"): Conexão com API Meteorológica (`weather.R`):**
  - Conexão via R (usando `httr` / `jsonlite` ou `curl`) a uma API pública sem chave (ex: Open-Meteo API).
  - Coleta e exibição formatada de dados climáticos no terminal.

---

### 3. Formação Social (Resumo de Artigo)
- **Artigo:** Embrapa - [CAP8.pdf](https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1003485/1/CAP8.pdf)
- **Formatação:**
  - Máximo 1 folha A4
  - Fonte Arial 11
  - Espaçamento 1.0 entre linhas
  - Margens direita e esquerda: 2 cm

---

### 4. Entregáveis e Estrutura do Pacote (.ZIP)
- Código fonte em Python (`.py`)
- Script de análise e API em R (`.R`)
- Resumo do artigo (`.pdf` ou `.docx`)
- `link_video.txt` (Contendo link do vídeo no YouTube - não listado, até 5 min demonstrando a execução)

---

## 🛠️ Tecnologias e Diretrizes de Código
- **Python:** 3.x puro (sem bibliotecas externas pesadas para o menu principal).
- **R:** `jsonlite`, `httr` (para API) e funções nativas de estatística (`mean`, `sd`, `summary`).
- **Git/GitHub:** Versionamento de código colaborativo.
