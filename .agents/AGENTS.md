# Memoria do Projeto FarmTech Solutions - Ecossistema AgroSaaS (FIAP - Fases 1, 2 e 3)

Arquivo de memoria e contexto persistente do projeto. Registra todas as regras,
decisoes arquiteturais, caminhos de arquivos e o diario completo de execucao.

---

## REGRA FUNDAMENTAL E OBRIGATORIA
- NUNCA UTILIZAR EMOJIS em qualquer arquivo do projeto (codigo Python, R, C/C++,
  SQL, documentação Markdown, arquivos HTML, TXT, mensagens de log ou comentarios).
  Usar apenas texto limpo em caracteres padrao.

---

## Contexto Geral
- Startup Academica: FarmTech Solutions (Agricultura 4.0)
- Aluno / Integrante: Angelo Guilherme Sfreddo - RM: 566580 - Turma: 1TIAO
- E-mail: angelogsfreddo@gmail.com
- Repositorio GitHub: git@github.com:angelosfreddo/agrosaas.git
  - Diretorio local do repositorio na Fase 3: /home/angelo/FIAP/fase3/agrosaas
  - Pasta direta da atividade na Fase 3: /home/angelo/FIAP/fase3/etapasDeUmaMaquinaAgricola
  - Caminho no padrao do portfolio FIAP: /home/angelo/FIAP/fase3/agrosaas/1TIAO/FASE3/CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA
  - Modelo oficial da coordenacao: https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI

---

## Resumo das Entregas Anteriores (Fases 1 e 2)

### 1. Fase 1 (`1TIAO/FASE1`)
- Aplicacao Python (`src/python/main.py`): CRUD em vetores paralelos para Cafe (retangulo, pulverizacao fungicida em Litros) e Milho (trapezio, fosfato/NPK em Kg).
- Base compartilhada: `data/dados_fazenda.csv` (5 registros).
- Scripts em R (`src/r/analysis.R` e `src/r/weather.R`): estatistica descritiva e integracao com API Open-Meteo.
- Formacao Social: resumo do artigo da Embrapa (`docs/resumo_artigo_embrapa.pdf`).

### 2. Fase 2 (`1TIAO/FASE2`)
- **Cap 1 - Um Mapa do Tesouro (`1TIAO/FASE2/CAP1-UM-MAPA-DO-TESOURO`):**
  - Circuito IoT ESP32 no Wokwi (`src/iot_esp32/diagram.json` e `sketch.ino`) para cultura de Milho.
  - Sensores: S1 Umidade (`DHT22` pino 15), S2 pH (`LDR` pino 34, mapeado 0..4095 -> 0..14), S3 NPK (3 botoes `INPUT_PULLUP` pinos 12, 14 e 27) e Rele da Bomba (pino 2).
  - Regras agronomicas: umidade < 40% liga a bomba (`FERTIRRIGACAO` se faltar N, P ou K; `IRRIGACAO` se NPK ok); umidade >= 60% desliga; entre 40% e 60% mantem estado (histerese); comando serial `'1'` (previsao de chuva da API Python) bloqueia a bomba; pH fora de 6.0 a 7.0 emite alerta de calagem.
- **Cap 6 - Python e Alem (`1TIAO/FASE2/CAP6-PYTHON-E-ALEM`):**
  - Sistema PerdaZero para gestao de perdas na colheita mecanizada de cana-de-acucar.
  - Arquivos gerados: `data/base_local.json`, `data/coleta_campo_exemplo.json`, `config/parametros.json`, `output/log_operacoes.txt`.
  - Banco Oracle da FIAP: `oracle.fiap.com.br:1521/ORCL` (usuario `RM566580`, biblioteca `oracledb`).

---

## Entrega Atual: Fase 3 - Etapas de uma Maquina Agricola
- Caminho no repositorio: `1TIAO/FASE3/CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA`

### Parte 1 - Coleta, Processamento Cientifico (Pandas/NumPy) e Visualizacao (Matplotlib/Seaborn)
1. **Firmware de Exportacao (`src/iot_esp32/sketch.ino`):**
   - Preserva integralmente os pinos e a logica agronomica da Fase 2.
   - Adiciona relogio simulado onde cada ciclo do `loop()` avanca 1 hora (iniciando em `2026-01-01 00:00`) e imprime linha CSV: `data_hora,umidade,ph,fosforo,potassio,nitrogenio,bomba,chuva,acao`.
2. **Extracao e Complemento Simulado (`src/python/exportar_serial.py` e `gerar_complemento.py`):**
   - Extrai 96 horas reais do log do Wokwi (`data/raw/monitor_serial_wokwi.txt` -> `data/raw/leituras_brutas_wokwi.csv`, `origem=WOKWI`).
   - Complementa com 2.785 linhas simuladas (`origem=SIMULADO`, semente 42) ate `2026-04-30 23:00`, totalizando 2.881 linhas brutas (4 meses) em `data/raw/leituras_brutas.csv`.
3. **Limpeza, Media Movel, Indicadores e Correlacao (`src/python/tratamento_dados.py`):**
   - Remove 5 duplicatas, trata 22 leituras `"nan"` do DHT22, 4 leituras de umidade fora de `[0, 100]%`, 13 leituras de pH fora de `[0, 14]` e interpola 4 horas ausentes na grade horaria, gerando 2.880 registros limpos em `data/processed/leituras_tratadas.csv`.
   - Aplica media movel de 6 horas (`umidade_suavizada` e `ph_suavizado`) com Pandas e convolucao NumPy (`np.convolve`), reduzindo o desvio padrao de umidade de 8,13% para 7,83% e de pH de 0,187 para 0,171.
   - Calcula indicadores diarios (`indicadores_diarios.csv`), mensais (`indicadores_mensais.csv`), eventos de bomba (`acionamentos_bomba.csv`: 38 acionamentos, 282 horas ligada, 1.410.000 L = 1.410 m3 com vazao de 5.000 L/h), faixas de umidade (`faixas_umidade.csv`) e matriz de correlacao de Pearson (`matriz_correlacao.csv`, destacando `r = -0,3501` entre umidade e bomba).
4. **Graficos (`src/python/visualizacao.py` -> `docs/graficos/`):**
   - `01_evolucao_umidade_ph_tempo.png`
   - `02_relacao_leituras_acionamento_bomba.png`
   - `03_distribuicao_sensores.png`
   - `04_mapa_calor_correlacao.png`

### Parte 2 - Ambiente Oracle Database e Primeira Persistencia
1. **Scripts SQL (`src/sql/ddl_fase3.sql` e `src/sql/consultas_gestao.sql`):**
   - Tabelas: `FT3_MANEJO_CULTURA` (PK `ID_MANEJO`), `FT3_LEITURA_SENSOR` (PK `ID_LEITURA`, `UNIQUE DATA_HORA`), `FT3_ACIONAMENTO_BOMBA` (PK `ID_ACIONAMENTO`) e `FT3_AVALIACAO_FASE2` (PK `COD_AVALIACAO`).
2. **Carga Repetivel em Python (`src/python/carga_oracle.py`):**
   - Carrega o CSV tratado da Fase 3, o CSV da Fase 1 (`dados_fazenda.csv`) e os arquivos JSON/TXT da Fase 2 (`base_local.json`, `coleta_campo_exemplo.json`, `parametros.json`, `log_operacoes.txt`).
   - Usa `MERGE INTO` com bind variables para garantir idempotencia (zero duplicatas ao repetir a carga) e mantem espelho local validado em `data/processed/farmtech_fase3_local.db`.
3. **Consultas de Gestao (`src/python/consultas_oracle.py` -> `docs/evidencias/`):**
   - Executa 6 consultas SQL respondendo as 6 informacoes relevantes listadas no README e exporta `evidencia_carga_oracle.txt`, `evidencia_consultas_gestao.txt` e `consulta_01..06_*.csv`.

### Desafios Opcionais Ir Alem 1 e Ir Alem 2 (`IR-ALEM/`)
1. **Ir Alem 1 - ESP32 Eficiente (`IR-ALEM/src/esp32_otimizado/`):**
   - `sketch_otimizado.ino`: `constexpr uint8_t` nos pinos, `uint16_t` para ADC do LDR (`0..4095`), ponto fixo em decimos (`uint8_t phDec` e `uint16_t umidadeDec`) eliminando `double` de 64 bits na FPU do ESP32, empacotamento de 7 `bool` em 1 bitmask `uint8_t estadoGlobal` (-62,5% nos bytes de variaveis do sketch) e strings unificadas em `PROGMEM` (-10,6% em `.rodata`).
   - `verificar_otimizacao.py`: compila ambos os firmwares com `g++ -Os`, mede secoes com `size -A`, comprova 100% de equivalencia em 784 cenarios de sensores e gera `IR-ALEM/docs/comparativo_compilacao_esp32.png`.
   - `analise_estatistica_r.R`: analise complementar em R com evidencias em `IR-ALEM/docs/evidencia_analise_r.txt`.
2. **Ir Alem 2 - Leituras Brutas em Banco NoSQL (`IR-ALEM/src/mongodb_nosql/`):**
   - `carga_consultas_mongo.py`: insere os 2.881 pacotes brutos na colecao `farmtech_solutions.leituras_brutas_esp32` via `pymongo` (com subdocumento condicional `diagnostico_bruto` nas 39 leituras com `"nan"` ou fora de faixa), executa 5 consultas/agregacoes NoSQL e exporta `IR-ALEM/data/exemplo_documento_mongodb.json` e `IR-ALEM/docs/evidencia_consultas_mongodb.txt`.

---

## Diario de Execucao
- 2026-11-02 15:01 - Levantamento do workspace, leitura das Fases 1 e 2, extracao dos 13 PDFs da Fase 3 e clone do repositorio modelo `FIAP-PORTFOLIO-AI`.
- 2026-11-02 15:10 - Definicao de escopo com o usuario: estrutura em `1TIAO/FASE3/CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA`, servidor Oracle FIAP, firmware Wokwi com relogio simulado + complemento documentado, e implementacao de ambos os desafios Ir Alem 1 e Ir Alem 2.
- 2026-11-02 15:15 - Criacao do firmware `src/iot_esp32/sketch.ino` e copia dos datasets das Fases 1 e 2 para `data/fases_anteriores/`.
- 2026-11-02 15:24 - Implementacao e execucao de `config.py`, `exportar_serial.py`, `gerar_complemento.py` e `tratamento_dados.py` (2.881 linhas brutas -> 2.880 linhas tratadas e suavizadas por media movel de 6h).
- 2026-11-02 15:27 - Implementacao e execucao de `visualizacao.py`, gerando os 4 graficos em `docs/graficos/`.
- 2026-11-02 15:34 - Criacao dos scripts SQL (`ddl_fase3.sql` e `consultas_gestao.sql`) e execucao de `carga_oracle.py` e `consultas_oracle.py`, gerando todas as evidencias em `docs/evidencias/`.
- 2026-11-02 15:42 - Implementacao e verificacao do Ir Alem 1 (`sketch_otimizado.ino`, `verificar_otimizacao.py` com 784 testes logicos e `analise_estatistica_r.R`).
- 2026-11-02 15:45 - Implementacao e execucao do Ir Alem 2 (`carga_consultas_mongo.py` com 2.881 documentos JSON e 5 consultas NoSQL).
- 2026-11-02 15:52 - Criacao do notebook `analise_irrigacao_fase3.ipynb`, roteiro de video, `link_entrega_portal.txt`, documentacao `README.md` (principal, `IR-ALEM` e raiz) e atualizacao desta memoria.
