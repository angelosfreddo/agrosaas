# FarmTech Solutions - Ecossistema AgroSaaS (FIAP)

**[LINK DO REPOSITORIO GITHUB]:** [https://github.com/angelosfreddo/agrosaas](https://github.com/angelosfreddo/agrosaas)

Repositorio central de desenvolvimento da **FarmTech Solutions**, contemplando as entregas de Agricultura Digital desenvolvidas para os modulos da FIAP (Turma 1TIAO).

---

## Estrutura do Repositorio

```
agrosaas/
├── .agents/
│   └── AGENTS.md                                      # Memoria do projeto e diretrizes de desenvolvimento
├── 1TIAO/
│   ├── FASE1/                                         # Fase 1: Gestao de Manejo, Calculo de Areas e Estatistica
│   │   ├── docs/                                      # Resumo cientifico da Embrapa (PDF, ODT, HTML, MD) e roteiro
│   │   ├── src/
│   │   │   ├── python/main.py                         # Aplicacao CRUD via terminal em vetores paralelos (Cafe e Milho)
│   │   │   └── r/
│   │   │       ├── analysis.R                         # Analise estatistica basica (Media, Desvio Padrao, Mediana)
│   │   │       └── weather.R                          # Integracao com a API publica Open-Meteo
│   │   ├── data/dados_fazenda.csv                     # Dataset compartilhado entre Python e R
│   │   └── link_video.txt                             # Link do video demonstrativo da Fase 1 no YouTube
│   └── FASE2/                                         # Fase 2: IoT, Irrigacao Inteligente e Gestao Agricola
│       ├── CAP1-UM-MAPA-DO-TESOURO/                   # Cap 1: Sistema IoT de Irrigacao e Fertirrigacao (ESP32, Python, R)
│       │   ├── src/
│       │   │   ├── iot_esp32/
│       │   │   │   ├── diagram.json                   # Circuito e pinagem montados no simulador Wokwi
│       │   │   │   └── sketch.ino                     # Firmware em C/C++ para o ESP32
│       │   │   ├── api_clima/clima_api.py             # Integracao com Open-Meteo e comando Serial (Ir Alem 1)
│       │   │   └── data_analysis_r/analise_irrigacao.R # Analise estatistica e preditiva em R (Ir Alem 2)
│       │   ├── docs/
│       │   │   ├── circuito_wokwi.png                 # Imagem do circuito montado no Wokwi
│       │   │   └── roteiro_video.md                   # Roteiro passo a passo para o video demonstrativo
│       │   ├── link_video.txt                         # Link do video demonstrativo no YouTube
│       │   └── README.md                              # Documentacao detalhada do Capitulo 1
│       ├── CAP6-PYTHON-E-ALEM/                        # Cap 6: PerdaZero - Gestao de Perdas na Colheita e Oracle
│       │   ├── config/parametros.json                 # Parametros agronomicos e financeiros
│       │   ├── data/                                  # Base local JSON (Offline-First) e exemplos de coleta
│       │   ├── src/                                   # Modulos Python (main, calculos, banco_oracle, validacao)
│       │   ├── IR-ALEM/DIFERENCIAIS.txt               # Descricao dos diferenciais implementados
│       │   └── README.md                              # Documentacao do sistema PerdaZero
│       ├── docs/
│       │   ├── circuito_wokwi.png                     # Imagem do circuito Wokwi
│       │   └── roteiro_video.md                       # Roteiro de gravacao do video da Fase 2
│       └── README.md                                  # Visao geral da Fase 2
└── README.md                                          # Documentacao unificada do repositorio
```

---

## Visao Geral dos Modulos

### Fase 1 (`1TIAO/FASE1`)
- **Culturas Atendidas:** Cafe (talhoes retangulares) e Milho (talhoes trapezoidais).
- **CRUD em Python:** Gerenciamento interativo de areas, dosagem e pulverizacao por ruas com armazenamento em vetores paralelos.
- **Estatistica Descritiva em R:** Analise quantitativa de areas e insumos.
- **Integracao Climatica:** Monitoramento de vento e temperatura via API Open-Meteo.
- **Formacao Social:** Resumo do artigo da Embrapa (CAP8) sobre transformacao digital no campo.

---

### Fase 2 - Cap 1: Um Mapa do Tesouro (`1TIAO/FASE2/CAP1-UM-MAPA-DO-TESOURO`)
- **Cultura Foco:** Milho (*Zea mays*), com parametros fundamentados em estudos da **Embrapa Milho e Sorgo**.
- **Prototipo IoT ESP32 (Wokwi):**
  - **Sensor DHT22 (Umidade do Solo):** Aciona a bomba com umidade < 40% e desliga com >= 60%.
  - **Botoes Verdes (NPK):** Simulam sensores de Nitrogenio, Fosforo e Potassio. Aciona automaticamente o modo de **FERTIRRIGACAO** se houver deficiencia nutricional.
  - **Sensor LDR (pH do Solo):** Mapeado na escala de 0 a 14. Alerta para necessidade de calagem caso saia da faixa ideal (6.0 a 7.0).
  - **Rele Azul (Bomba d'Agua):** Modulo atuador que controla o fluxo hidrico.
- **Ir Alem 1 (Python + API Open-Meteo):** Consulta de previsao de chuva em tempo real e comando Serial (`1` ou `0`) para suspensao preventiva da irrigacao.
- **Ir Alem 2 (Data Science em R):** Analise exploratoria de historico de 10 dias e media movel de 3 dias para prescricao automatica de irrigacao.
- **Video Demonstrativo (YouTube - Nao Listado):** [https://youtu.be/AVC19HA_oGU](https://youtu.be/AVC19HA_oGU)

#### Circuito no Wokwi:
![Circuito Wokwi](./1TIAO/FASE2/CAP1-UM-MAPA-DO-TESOURO/docs/circuito_wokwi.png)

Consulte a documentacao completa em [`1TIAO/FASE2/CAP1-UM-MAPA-DO-TESOURO/README.md`](./1TIAO/FASE2/CAP1-UM-MAPA-DO-TESOURO/README.md).


---

### Fase 2 - Cap 6: Python e Alem (`1TIAO/FASE2/CAP6-PYTHON-E-ALEM`)
- **Sistema PerdaZero:** Solucao para monitoramento e gestao inteligente de perdas na colheita mecanizada de cana-de-acucar.
- **Arquitetura Offline-First + Oracle DB:** Operacao local em JSON com sincronizacao automatica para o banco de dados Oracle da FIAP.

Consulte a documentacao completa em [`1TIAO/FASE2/CAP6-PYTHON-E-ALEM/README.md`](./1TIAO/FASE2/CAP6-PYTHON-E-ALEM/README.md).
