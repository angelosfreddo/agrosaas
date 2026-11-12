# Desafios Opcionais Ir Alem 1 e Ir Alem 2 - FarmTech Solutions (Fase 3)

## Identificacao do Integrante
- **Nome Completo:** Angelo Guilherme Sfreddo
- **RM:** 566580
- **Turma:** 1TIAO
- **Links dos Videos Demonstrativos (YouTube - Nao Listado, ate 4 min):**
  - Video Principal (Parte 1 e Parte 2): [https://youtu.be/i0BP7iumE9o](https://youtu.be/i0BP7iumE9o)
  - Video Ir Alem 1 (ESP32 Eficiente): [https://youtu.be/vSLT66K6HfE](https://youtu.be/vSLT66K6HfE)
  - Video Ir Alem 2 (MongoDB NoSQL): [https://youtu.be/XN2zP-8JdFA](https://youtu.be/XN2zP-8JdFA)

---

## Sumario da Pasta `IR-ALEM`

```text
IR-ALEM/
├── data/
│   ├── amostra_colecao_mongodb.json       # Amostra de 25 documentos exportados do MongoDB
│   └── exemplo_documento_mongodb.json     # Comparativo: documento normal vs documento com falha bruta
├── docs/
│   ├── comparativo_compilacao_esp32.png   # Print da compilacao e reducao de memoria (Antes vs Depois)
│   ├── evidencia_analise_r.txt            # Saida da analise estatistica complementar em R
│   ├── evidencia_consultas_mongodb.txt    # Saida completa das 5 consultas e agregacoes no MongoDB
│   └── relatorio_otimizacao_esp32.txt     # Relatorio tecnico das secoes de memoria e teste de equivalencia
├── src/
│   ├── analise_estatistica_r.R            # Script R para estatistica descritiva e correlacao
│   ├── esp32_otimizado/
│   │   ├── sketch_original_fase2.ino      # Firmware original da Fase 2 para comparacao
│   │   ├── sketch_otimizado.ino           # Firmware C/C++ otimizado (tipos enxutos, bitmask, PROGMEM)
│   │   └── verificar_otimizacao.py        # Compilacao automatizada, medicao de secoes e 784 testes logicos
│   └── mongodb_nosql/
│       └── carga_consultas_mongo.py       # Carga do CSV bruto no MongoDB e execucao de 5 consultas NoSQL
└── README.md                              # Documentacao unificada dos desafios Ir Alem 1 e Ir Alem 2
```

---

## IR ALEM 1 - ESP32 Eficiente: Tipos de Variaveis e Otimizacao de Memoria

### 1. Objetivo
Revisar o firmware C/C++ de irrigacao da Fase 2 sob a otica da arquitetura do microcontrolador ESP32 (Xtensa Dual-Core LX6 de 32 bits, dotado de FPU apenas para precisao simples `float` de 32 bits), substituindo tipos superdimensionados por representacoes enxutas em inteiros sem sinal de 8 e 16 bits, empacotamento de flags booleanas em bitmask e armazenamento de strings em Flash (`PROGMEM`), mantendo 100% da logica agronomica de irrigacao.

### 2. Mapeamento e Justificativa Tecnica das Otimizacoes

| Elemento / Variavel | Fase 2 (Original) | Fase 3 (Otimizado) | Justificativa Tecnica e Economia |
| :--- | :--- | :--- | :--- |
| **Pinos de Hardware (6 constantes)** | `#define` / `int` implicito (32 bits) | `constexpr uint8_t` (8 bits, tempo de compilacao) | Os pinos GPIO do ESP32 numeram de 0 a 39, cabendo em 1 byte sem sinal (`0..255`). O `constexpr` permite verificacao de tipo sem alocar bytes em RAM. |
| **Leitura ADC do LDR (`valorLDR`)** | `int valorLDR` (4 bytes, com sinal) | `uint16_t valorLDR` (2 bytes, sem sinal) | O conversor analogico-digital (ADC) do ESP32 tem resolucao de 12 bits (`0` a `4095`), nunca assumindo valores negativos. `uint16_t` (`0..65535`) reduz o uso pela metade (-50%). |
| **Calculo do pH (`0.0` a `14.0`)** | `float pH = (valorLDR / 4095.0) * 14.0;` (usa literais `double` de 64 bits / 8 bytes) | `uint8_t phDec` em decimos (`0` a `140` representando `0.0` a `14.0`) via aritmetica inteira | Em C/C++, literais como `4095.0` e `14.0` sem o sufixo `f` sao `double` (64 bits). Como o ESP32 nao tem FPU de 64 bits em hardware, ele precisa incluir rotinas pesadas de emulacao em software (`__divdf3`, `__muldf3`). Representar o pH em decimos (`uint8_t`, 1 byte) elimina o `double`, economiza 87,5% na variavel e preserva a mesma precisao de 1 casa decimal impressa no Serial. |
| **Leitura de Umidade (`0.0%` a `100.0%`)** | `float umidade` mantida em todas as comparacoes (4 bytes) | `uint16_t umidadeDec` (`0` a `1000` decimos, 2 bytes) | A biblioteca `DHT` retorna `float`, que e validado com `isnan()` e imediatamente convertido para decimos em `uint16_t` (2 bytes), fazendo as comparacoes `< 400` (40.0%) e `>= 600` (60.0%) em inteiros rapidos. |
| **Estados Booleanos (`previsaoChuva`, `N`, `P`, `K` e flags)** | 7 variaveis `bool` independentes (7 bytes) | 1 registrador `uint8_t estadoGlobal` com mascara de bits (`FLAG_N_OK`, `FLAG_P_OK`, `FLAG_K_OK`, `FLAG_CHUVA`) | Cada `bool` em C++ ocupa 1 byte inteiro (8 bits) para guardar 1 unico bit de informacao (desperdicio de 87,5%). Empacotar os estados em mascaras de bits dentro de um unico `uint8_t` reduz 7 bytes para 1 byte. |
| **Strings Literais Repetidas no Serial** | Literais duplicados (`"[OK]"`, `"[BAIXO]"`, separadores de 48 tracos) | `constexpr const char ... PROGMEM` e macro `F()` | Unifica strings repetidas (`STR_SEPARADOR`, `STR_OK`, `STR_BAIXO`) em uma unica alocacao no segmento `.rodata` da Flash, reduzindo o consumo de memoria de programa em 10,6%. |

### 3. Tabela Comparativa de Consumo de Memoria (Antes vs Depois)

| Metrica Medida na Compilacao | Antes (Fase 2 Original) | Depois (Fase 3 Otimizado) | Variacao / Ganho |
| :--- | :---: | :---: | :---: |
| **Variaveis da aplicacao (`loop` + global)** | 16 bytes + promocao `double` (8 B) | **6 bytes** (zero `double`) | **-62,5% (-10 bytes)** |
| **Segmento `.rodata` do Sketch (strings constantes)** | 865 bytes | **773 bytes** | **-10,6% (-92 bytes)** |
| **Tamanho combinado do Sketch (`.text` + `.rodata`)** | 2.010 bytes | **1.962 bytes** | **-2,4% (-48 bytes)** |
| **Flash Total ESP32 (`xtensa-esp32-elf-gcc`)** | 274.916 bytes (21,0%) | **271.492 bytes (20,7%)** | **-3.424 bytes (-3,34 KB)** |
| **RAM Estatica Total ESP32 (DRAM / IRAM)** | 21.588 bytes (6,6%) | **21.508 bytes (6,6%)** | **-80 bytes** |
| **Teste de Equivalencia da Logica de Irrigacao** | 784 cenarios de referência | **784 / 784 identicos** | **100% preservada** |

![Comparativo de Compilacao do ESP32](./docs/comparativo_compilacao_esp32.png)

### 4. Interpretacao da Analise Estatistica em R (`src/analise_estatistica_r.R`)
O script complementar em linguagem R (`IR-ALEM/src/analise_estatistica_r.R`) analisa as 2.880 leituras tratadas exportadas pelo circuito:
- **Umidade do Solo (S1):** apresentou media de **53,57%**, mediana de **52,80%** e desvio padrao de **8,14%**, variando entre o minimo de **35,20%** e o maximo de **79,20%**. Esses numeros confirmam que o controle por histerese do firmware manteve a lavoura de milho quase todo o tempo dentro da faixa segura entre 40% e 60%.
- **pH do Solo (S2):** apresentou media de **6,08**, mediana de **6,07** e desvio padrao de **0,187** (intervalo de **5,60** a **6,55**), refletindo a tendencia de acidificacao gradual em marco/abril e a recuperacao imediata apos a correcao por calagem.
- **Correlacao e Proporcao de Acionamento:** a correlacao de Pearson medida no R confirma a associacao negativa entre umidade e bomba ligada (`r = -0,3501`), seguida pelo efeito inibidor da previsao de chuva (`r = -0,0807`). Na faixa critica (`umidade < 40%`), a bomba esteve ligada em **80,95%** das horas (sendo os 19,05% restantes exatamente as horas em que a API de previsao de chuva bloqueou preventivamente a irrigacao para economizar agua).

### 5. Como Executar o Ir Alem 1
```bash
# 1. Compilar ambos os firmwares, medir secoes de memoria e testar 784 cenarios
python IR-ALEM/src/esp32_otimizado/verificar_otimizacao.py

# 2. Executar a analise estatistica complementar em R
Rscript IR-ALEM/src/analise_estatistica_r.R
```

---

## IR ALEM 2 - Leituras Brutas em Banco NoSQL (MongoDB)

### 1. Objetivo
Armazenar as 2.881 leituras brutas do Monitor Serial do ESP32 diretamente em um banco de dados NoSQL orientado a documentos (**MongoDB**, colecao `farmtech_solutions.leituras_brutas_esp32`), sem exigir limpeza previa, e comparar na pratica a experiencia do modelo de documentos JSON/BSON com o modelo relacional Oracle implementado na Parte 2.

### 2. Estrutura dos Documentos e Flexibilidade de Esquema
Cada ciclo do Monitor Serial e gravado como um documento JSON contendo:
- os campos originais preservados (`data_hora`, `umidade_raw`, `umidade`, `ph_raw`, `ph`, `fosforo`, `potassio`, `nitrogenio`, `bomba`, `chuva`, `acao`, `origem`);
- um subdocumento aninhado `sensores` agrupando `S1_umidade_pct`, `S2_ph_ldr` e `S3_nutrientes` (`P`, `K`, `N`);
- um subdocumento condicional `diagnostico_bruto` adicionado **apenas** nos documentos em que a leitura bruta veio com falha (`"nan"` do sensor DHT22) ou fora dos limites fisicos (`umidade` fora de `0..100%` ou `ph` fora de `0..14`), demonstrando a flexibilidade de esquema (*schema-less*) sem desperdicar colunas nulas nos demais registros.

O arquivo [`data/exemplo_documento_mongodb.json`](./data/exemplo_documento_mongodb.json) apresenta lado a lado um documento normal de fertirrigacao e um documento com falha bruta de sensor.

### 3. Descricao das Consultas e Agregacoes Implementadas
O script [`src/mongodb_nosql/carga_consultas_mongo.py`](./src/mongodb_nosql/carga_consultas_mongo.py) executa cinco operacoes NoSQL:
1. **Consulta 1 (Filtro por faixa de umidade e bomba):** `{"umidade": {"$gte": 0.0, "$lt": 40.0}, "bomba": 1}` — localiza os 34 ciclos brutos em que o solo entrou na faixa critica de estresse hidrico com acionamento da bomba.
2. **Consulta 2 (Filtro por estado e modalidade):** `{"bomba": 1, "acao": "FERTIRRIGACAO"}` — recupera os 23 ciclos em que o sistema injetou agua + nutrientes devido a deficit simultaneo em N, P ou K.
3. **Consulta 3 (Auditoria de falhas brutas de hardware):** `{"diagnostico_bruto.leitura_integra": False}` — recupera diretamente os 39 documentos brutos que apresentaram timeout (`nan`) no DHT22 ou picos eletricos no ADC do LDR.
4. **Consulta 4 (Pipeline de agregacao por acao):** estagios `$match`, `$group` e `$sort` calculando total de ciclos, horas de bomba ligada e medias de umidade e pH para cada estado operacional do firmware.
5. **Consulta 5 (Pipeline de agregacao mensal):** estagio `$group` por `ano_mes` contabilizando leituras brutas, horas de bomba ligada, horas sob previsao de chuva e ocorrencias de deficit de fosforo e potassio.

Os resultados completos encontram-se registrados em [`docs/evidencia_consultas_mongodb.txt`](./docs/evidencia_consultas_mongodb.txt).

### 4. Comparacao Critica: MongoDB (NoSQL) vs Oracle Database (Relacional) no Projeto

| Criterio do Projeto FarmTech | Quando o MongoDB (Documentos) foi mais conveniente | Quando o Oracle (Relacional SQL) foi mais conveniente |
| :--- | :--- | :--- |
| **Ingestao de leituras brutas do ESP32** | **Mais conveniente no MongoDB:** o Monitor Serial gerou 22 leituras `"nan"` (falha de leitura do DHT22) e 17 leituras fora da faixa fisica (`-3.8%`, `134.3%`, `pH 17.85`). No MongoDB foi possivel gravar imediatamente todos os 2.881 pacotes brutos preservando `umidade_raw: "nan"` e anexando o subdocumento `diagnostico_bruto` apenas nos registros defeituosos. | No Oracle, a tabela `FT3_LEITURA_SENSOR` possui constraints `NOT NULL` e `CHECK (UMIDADE_TRATADA BETWEEN 0 AND 100)`. Qualquer tentativa de inserir o CSV bruto diretamente no Oracle falha com erro de constraint, exigindo obrigatoriamente o pipeline previo de limpeza em Pandas. |
| **Evolucao de sensores no circuito** | **Mais conveniente no MongoDB:** se na Fase 4 um novo sensor (ex.: temperatura do ar do DHT22 ou condutividade eletrica) for adicionado ao ESP32, basta passar a incluir o novo campo nos novos documentos JSON, sem alterar os 2.881 documentos antigos e sem executar `ALTER TABLE`. | No Oracle, adicionar um novo sensor exige alterar o esquema formal (`ALTER TABLE FT3_LEITURA_SENSOR ADD ...`), atualizar o `MERGE INTO` e definir valores padrao para o historico passado. |
| **Cruzamento entre sensores, culturas (Fase 1) e perdas de colheita (Fase 2)** | Menos natural no MongoDB: cruzar colecoes separadas exige estagios `$lookup` mais verbosos e nao conta com integridade referencial nativa ao nivel do banco. | **Mais conveniente no Oracle:** a consulta de monitoramento que une `FT3_AVALIACAO_FASE2` e `FT3_MANEJO_CULTURA` por `LEFT JOIN` sobre `CODIGO_TALHAO`, bem como agregacoes analiticas padronizadas (`GROUP BY TO_CHAR(DATA_HORA, 'YYYY-MM')`), sao diretas, legiveis e protegidas por chaves primarias e estrangeiras. |
| **Qualidade para treinar modelos de Machine Learning (Fase 4)** | Bom como *Data Lake / Landing Zone* de telemetria bruta para auditoria de falhas de sensores. | **Mais conveniente no Oracle:** garante tipagem forte, ausencia de nulos nas colunas de treino (`UMIDADE_SUAVIZADA`, `PH_SUAVIZADO`) e unicidade temporal (`UNIQUE (DATA_HORA)`), entregando uma tabela pronta para o Scikit-Learn. |

**Conclusao arquitetural:** as duas tecnologias sao complementares na FarmTech Solutions. O **MongoDB** e ideal na borda de ingestao IoT (*raw telemetry store*) para receber pacotes brutos dos ESP32 sem perda de eventos mesmo quando sensores falham, enquanto o **Oracle Database** e ideal na camada analitica e transacional (*curated warehouse*) apos o tratamento com Pandas/NumPy.

### 5. Como Executar o Ir Alem 2
```bash
# Opcional: apontar para MongoDB Atlas ou instancia local
# export MONGODB_URI="mongodb+srv://usuario:senha@cluster.mongodb.net/"

python IR-ALEM/src/mongodb_nosql/carga_consultas_mongo.py
```

