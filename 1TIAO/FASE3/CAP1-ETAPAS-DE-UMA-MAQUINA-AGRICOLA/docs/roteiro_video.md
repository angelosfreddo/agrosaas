# Roteiro dos Videos Demonstrativos (Ate 4 Minutos) - Fase 3

**Aluno:** Angelo Guilherme Sfreddo (RM: 566580) - Turma 1TIAO  
**Visibilidade obrigatoria no YouTube:** Nao Listado (*Unlisted*)  
**Duracao maxima de cada video:** 4 minutos  

---

## 1. Roteiro do Video Principal (Parte 1 e Parte 2 - Obrigatorio)

### [00:00 - 00:35] Abertura e Exportacao do Wokwi

**O que mostrar na tela:**
1. Pagina do repositorio privado no GitHub (`1TIAO/FASE3/CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA`).
2. O arquivo `src/iot_esp32/sketch.ino` (ou simulacao no Wokwi).
3. Os arquivos `data/raw/monitor_serial_wokwi.txt` e `data/raw/leituras_brutas.csv`.

**Sugestao do que falar:**
> "Ola, eu sou Angelo Guilherme Sfreddo, RM 566580, da turma 1TIAO da FIAP, e este e o projeto da Fase 3 da FarmTech Solutions: Etapas de uma Maquina Agricola.  
> Na Fase 2, o nosso circuito ESP32 lia umidade, pH e nutrientes NPK para acionar a bomba, mas tudo ficava apenas no Monitor Serial do Wokwi e se perdia ao encerrar a simulacao.  
> Aqui na Fase 3, atualizamos o firmware `sketch.ino` com um relogio simulado onde cada ciclo equivale a 1 hora, imprimindo uma linha CSV no Serial. Exportamos as leituras iniciais do Wokwi para `monitor_serial_wokwi.txt` e complementamos em Python para formar um historico bruto de 4 meses, de janeiro a abril de 2026, com 2.881 linhas em `leituras_brutas.csv`, identificando na coluna `origem` o que veio do Wokwi e o que foi simulado."

---

### [00:35 - 01:45] Parte 1: Tratamento com Pandas/NumPy, Indicadores e Graficos

**O que mostrar na tela:**
1. Terminal executando `python src/python/tratamento_dados.py` (mostrando o relatorio impresso).
2. Pasta `docs/graficos/` abrindo os 4 graficos em sequencia.

**Sugestao do que falar:**
> "Agora passo para a Parte 1, rodando `tratamento_dados.py` com Pandas e NumPy.  
> Como podem ver no relatorio, o script converte todos os tipos, remove 5 linhas duplicadas, trata 22 falhas `nan` do sensor DHT22 e limpa leituras fisicamente impossiveis, como 4 umidades fora de 0 a 100% e 13 valores de pH fora de 0 a 14, fechando uma serie horaria continua de 2.880 registros.  
> Aplicamos uma media movel de 6 horas para suavizar o ruido dos sensores e calculamos os indicadores de manejo: considerando uma vazao de 5.000 litros por hora, tivemos 38 acionamentos da bomba, 282 horas ligada e 1.410.000 litros aplicados no periodo.  
>
> Nos graficos gerados com Matplotlib e Seaborn:  
> - No **Grafico 1**, vemos a serie bruta versus a media movel de 6h, com o controle de histerese entre 40% e 60% de umidade e a queda gradual do pH ate abril, quando ha correcao por calagem.  
> - No **Grafico 2**, damos um zoom de 15 dias mostrando a bomba ligando abaixo de 40%, o bloqueio preventivo por previsao de chuva no dia 3 de janeiro, o boxplot das decisoes do firmware e o consumo mensal de agua.  
> - No **Grafico 3**, temos as distribuicoes de umidade concentradas na faixa segura de 44% a 60% e a disponibilidade dos nutrientes P, K e N.  
> - E no **Grafico 4**, o mapa de calor de correlacao de Pearson confirma `r = -0,350` entre umidade e bomba ligada, sem chegar a -1 justamente pela faixa de histerese e pelos bloqueios por chuva."

---

### [01:45 - 03:45] Parte 2: Banco de Dados Oracle, Carga Repetivel e Consultas

**O que mostrar na tela:**
1. Secao de Requisitos no `README.md` (tabela das 6 informacoes relevantes).
2. Arquivo `src/sql/ddl_fase3.sql`.
3. Terminal executando `python src/python/carga_oracle.py` conectado ao Oracle da FIAP (mostrando a tabela de 0 duplicatas).
4. Terminal executando `python src/python/consultas_oracle.py` (ou prints/CSVs em `docs/evidencias/`).

**Sugestao do que falar:**
> "Na Parte 2, partimos do levantamento de 6 perguntas relevantes de gestao documentadas no README para modelar 4 tabelas relacionais no `ddl_fase3.sql`: `FT3_MANEJO_CULTURA`, `FT3_LEITURA_SENSOR`, `FT3_ACIONAMENTO_BOMBA` e `FT3_AVALIACAO_FASE2`, todas com chave primaria, constraints e tipos adequados.  
>
> Agora executando `carga_oracle.py` conectado ao Oracle da FIAP (`oracle.fiap.com.br:1521/ORCL`), o programa le nao so o CSV tratado desta fase, mas tambem integra os dados de culturas e insumos da Fase 1 e os arquivos JSON e de log da Fase 2. Como toda insercao usa `MERGE INTO` com bind variables, ao rodar a carga duas vezes seguidas vemos exatamente os mesmos totais: 6 registros de manejo, 2.880 leituras, 38 acionamentos e 2 avaliacoes da Fase 2, com **zero duplicatas**.  
>
> Por fim, executando `consultas_oracle.py`, temos as respostas das 6 consultas de gestao direto do banco Oracle: o volume mensal de agua aplicado somando 1.410 metros cubicos com 23 ciclos de fertirrigacao; a variacao mensal do pH e as horas em alerta de acidez; o ranking dos 10 dias mais criticos liderado por 10 de janeiro com 10 horas de bomba ligada; a relacao entre deficit de NPK e acoes do sistema; o consumo de insumos por cultura trazido da Fase 1; e o historico de perdas de colheita do talhao T01 vindo da Fase 2.  
> Com isso, os dados da fazenda deixam o Monitor Serial e passam a formar uma base historica organizada e pronta para os modelos preditivos da Fase 4. Obrigado!"

---

## 2. Roteiro do Video Ir Alem 1 (ESP32 Eficiente - Ate 4 Minutos)

**O que mostrar na tela:**
1. `IR-ALEM/src/esp32_otimizado/sketch_original_fase2.ino` e `sketch_otimizado.ino`.
2. Terminal rodando `python IR-ALEM/src/esp32_otimizado/verificar_otimizacao.py` e `Rscript IR-ALEM/src/analise_estatistica_r.R`.
3. Imagem `IR-ALEM/docs/comparativo_compilacao_esp32.png` e arquivo `IR-ALEM/docs/evidencia_analise_r.txt`.

**Sugestao do que falar:**
> "Ola, sou Angelo Guilherme Sfreddo, RM 566580, e neste video apresento o desafio Ir Alem 1: otimizacao de memoria do firmware do ESP32 e analise estatistica complementar em R.  
>
> Comparando o firmware original da Fase 2 com o `sketch_otimizado.ino`, fizemos cinco melhorias pensadas para a arquitetura de 32 bits do ESP32:  
> 1. Trocamos `#define` e `int` dos 6 pinos por `constexpr uint8_t`, sem alocar RAM.  
> 2. Trocamos `int` de 4 bytes por `uint16_t` de 2 bytes na leitura do ADC de 12 bits do LDR.  
> 3. Passamos umidade e pH para aritmetica inteira em decimos (`uint16_t` e `uint8_t`), eliminando literais `double` de 64 bits que nao tem suporte em hardware na FPU do ESP32.  
> 4. Compactamos 7 variaveis `bool` em uma unica mascara de bits de 1 byte (`uint8_t estadoGlobal`).  
> 5. Unificamos textos repetidos na memoria Flash com `PROGMEM` e macro `F()`.  
>
> Rodando `verificar_otimizacao.py`, o script compila os dois firmwares com `g++ -Os`, mede as secoes e testa automaticamente 784 combinacoes de sensores. Como mostra o grafico `comparativo_compilacao_esp32.png`, reduzimos as variaveis da aplicacao em 62,5% (de 16 para 6 bytes), o segmento `.rodata` caiu 10,6%, a Flash total reduziu 3,4 KB e todas as 784 decisoes do pino da bomba foram 100% identicas ao firmware original.  
> Tambem executamos o script `analise_estatistica_r.R`, que confirma umidade media de 53,57%, pH medio de 6,08, correlacao de -0,3501 entre umidade e bomba e acionamento em 80,95% das horas abaixo de 40%, sendo o restante bloqueado preventivamente pela previsao de chuva. Obrigado!"

---

## 3. Roteiro do Video Ir Alem 2 (MongoDB NoSQL - Ate 4 Minutos)

**O que mostrar na tela:**
1. `IR-ALEM/src/mongodb_nosql/carga_consultas_mongo.py`.
2. `IR-ALEM/data/exemplo_documento_mongodb.json`.
3. Terminal executando `/home/angelo/FIAP/.venv/bin/python IR-ALEM/src/mongodb_nosql/carga_consultas_mongo.py` (ou ativar a `.venv` antes e rodar `python IR-ALEM/src/mongodb_nosql/carga_consultas_mongo.py`).
4. Saida gerada no proprio terminal ou o arquivo de texto gerado em `IR-ALEM/docs/evidencia_consultas_mongodb.txt` (nao se executa o `.txt`; ele apenas guarda o relatorio que o script acabou de gerar).
5. Tabela comparativa em `IR-ALEM/README.md`.

**Sugestao do que falar:**
> "Ola, sou Angelo Guilherme Sfreddo, RM 566580, e neste video apresento o desafio Ir Alem 2: armazenamento das leituras brutas do ESP32 em banco NoSQL com MongoDB.  
>
> Diferente da Parte 2 no Oracle, em que precisamos limpar e tratar os dados antes de gravar por causa das constraints `NOT NULL` e `CHECK`, aqui ingerimos diretamente o CSV bruto com 2.881 leituras na colecao `farmtech_solutions.leituras_brutas_esp32` via `pymongo`.  
>
> Como vemos em `exemplo_documento_mongodb.json`, cada leitura vira um documento JSON preservando os valores originais, com o subdocumento aninhado `sensores` agrupando S1, S2 e S3. E nos 39 registros que vieram com falha `nan` do DHT22 ou fora da faixa fisica, o codigo anexa dinamicamente o subdocumento `diagnostico_bruto` sem exigir `ALTER TABLE` e sem criar colunas nulas nos demais documentos.  
>
> Rodando `carga_consultas_mongo.py`, executamos 5 consultas NoSQL: filtros `find` para umidade critica abaixo de 40%, ciclos de fertirrigacao e auditoria das 39 falhas brutas, alem de pipelines `aggregate` com `$group` por acao do sistema e resumo mensal.  
> Por fim, na comparacao documentada no `IR-ALEM/README.md`, concluimos que os dois bancos sao complementares: o **MongoDB** e mais conveniente na entrada bruta da telemetria IoT e para evoluir sensores sem alterar esquema, enquanto o **Oracle** e mais conveniente apos a limpeza, para `JOIN` entre tabelas de manejo, colheita e leituras prontas para Machine Learning. Obrigado!"
