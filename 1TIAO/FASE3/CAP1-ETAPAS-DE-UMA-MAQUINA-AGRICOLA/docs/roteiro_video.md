# Roteiro dos Videos Demonstrativos (Ate 4 Minutos) - Fase 3

**Aluno:** Angelo Guilherme Sfreddo (RM: 566580) - Turma 1TIAO  
**Visibilidade obrigatoria no YouTube:** Nao Listado (*Unlisted*)  
**Duracao maxima de cada video:** 4 minutos  

---

## 1. Roteiro do Video Principal (Parte 1 e Parte 2 - Obrigatorio)

### [00:00 - 00:35] Abertura e Exportacao do Wokwi
1. Apresentar o repositorio GitHub privado da **FarmTech Solutions** (`1TIAO/FASE3/CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA`) e identificar o integrante (Angelo Guilherme Sfreddo - RM 566580).
2. Mostrar brevemente o circuito da Fase 2 no Wokwi com o firmware atualizado (`src/iot_esp32/sketch.ino`), explicando que cada ciclo do loop equivale a 1 hora simulada e imprime uma linha CSV no Monitor Serial.
3. Mostrar o arquivo `data/raw/monitor_serial_wokwi.txt` e o CSV bruto consolidado `data/raw/leituras_brutas.csv` (2.881 linhas cobrindo 4 meses, de janeiro a abril de 2026, com a coluna `origem` distinguindo `WOKWI` e `SIMULADO`).

### [00:35 - 01:45] Parte 1: Tratamento com Pandas/NumPy, Indicadores e Graficos
1. No terminal, executar:
   ```bash
   python src/python/tratamento_dados.py
   ```
2. Destacar no relatorio impresso no terminal:
   - remocao de 5 duplicatas, tratamento de 22 leituras `"nan"` do DHT22, 4 leituras de umidade fora de `0..100%` e 13 leituras de pH fora de `0..14`;
   - reducao de ruido com media movel de 6 horas em `umidade_suavizada` e `ph_suavizado`;
   - indicadores de manejo: 38 acionamentos da bomba, 282 horas totais ligada e 1.410.000 litros (1.410 m3) de agua aplicados considerando a vazao de 5.000 L/h.
3. Executar e abrir os 4 graficos gerados em `docs/graficos/`:
   - `01_evolucao_umidade_ph_tempo.png` (evolucao de umidade e pH com media movel e evento de calagem em abril);
   - `02_relacao_leituras_acionamento_bomba.png` (ciclos de histerese 40%-60%, boxplot por acao e consumo mensal);
   - `03_distribuicao_sensores.png` (histogramas com KDE, violinplot mensal e proporcao de NPK);
   - `04_mapa_calor_correlacao.png` (heatmap de correlacao de Pearson destacando `r = -0,350` entre umidade e bomba).

### [01:45 - 03:45] Parte 2: Banco de Dados Oracle, Carga Repetivel e Consultas
1. Mostrar no `README.md` as 6 informacoes relevantes de gestao e os dados necessarios para cada uma.
2. Mostrar o script `src/sql/ddl_fase3.sql` com as tabelas `FT3_MANEJO_CULTURA`, `FT3_LEITURA_SENSOR`, `FT3_ACIONAMENTO_BOMBA` e `FT3_AVALIACAO_FASE2`.
3. Executar a carga em Python:
   ```bash
   python src/python/carga_oracle.py
   ```
   Apontar na tabela final que a 1a e a 2a carga seguidas mantem exatamente a mesma contagem (6 culturas/talhoes, 2.880 leituras, 38 acionamentos e 2 avaliacoes da Fase 2, com **0 duplicatas** gracas ao `MERGE INTO`).
4. Executar as consultas de gestao:
   ```bash
   python src/python/consultas_oracle.py
   ```
   Mostrar os resultados das 6 consultas SQL respondendo sobre volume mensal de agua, variacao do pH, top 10 dias de irrigacao, deficit de nutrientes, consumo de insumos por cultura (Fase 1) e perdas na colheita (Fase 2).

---

## 2. Roteiro do Video Ir Alem 1 (ESP32 Eficiente - Ate 4 Minutos)
1. Abrir lado a lado `IR-ALEM/src/esp32_otimizado/sketch_original_fase2.ino` e `sketch_otimizado.ino`.
2. Explicar as otimizacoes: `constexpr uint8_t` nos pinos, `uint16_t` no ADC do LDR (`0..4095`), ponto fixo em decimos (`uint8_t phDec` e `uint16_t umidadeDec`) eliminando `double` de 64 bits na FPU do ESP32, empacotamento de 7 `bool` em 1 `uint8_t estadoGlobal` (bitmask) e strings unificadas em `PROGMEM`.
3. Executar no terminal:
   ```bash
   python IR-ALEM/src/esp32_otimizado/verificar_otimizacao.py
   Rscript IR-ALEM/src/analise_estatistica_r.R
   ```
4. Mostrar a imagem `IR-ALEM/docs/comparativo_compilacao_esp32.png` (reducao de 62,5% nas variaveis do sketch, -10,6% em `.rodata`, -3,4 KB de Flash e 784/784 cenarios de teste com logica de irrigacao 100% identica).

---

## 3. Roteiro do Video Ir Alem 2 (MongoDB NoSQL - Ate 4 Minutos)
1. Mostrar o script `IR-ALEM/src/mongodb_nosql/carga_consultas_mongo.py` e explicar como cada linha do CSV bruto (`data/raw/leituras_brutas.csv`) vira um documento JSON na colecao `farmtech_solutions.leituras_brutas_esp32`.
2. Abrir `IR-ALEM/data/exemplo_documento_mongodb.json` e mostrar a diferenca entre um documento normal e um documento com falha bruta do sensor DHT22 (`"nan"`), que recebe o subdocumento `diagnostico_bruto` sem quebrar o esquema.
3. Executar no terminal:
   ```bash
   python IR-ALEM/src/mongodb_nosql/carga_consultas_mongo.py
   ```
4. Apresentar os resultados das 5 consultas (faixa critica de umidade, fertirrigacao, anomalias brutas e agregacoes `$group`) e concluir com a tabela comparativa MongoDB vs Oracle documentada em `IR-ALEM/README.md`.

