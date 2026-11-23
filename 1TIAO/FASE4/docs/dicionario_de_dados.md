# Dicionário de Dados — FarmTech Solutions (Fase 4)

Este documento descreve detalhadamente o esquema de dados definitivo da solução **FarmTech Solutions**, contemplando as entidades, tipos de dados, chaves primárias e estrangeiras, regras de negócio e restrições de integridade.

---

## 1. Tabela `FT4_CULTURA`
Armazena os parâmetros agronômicos de cada cultura monitorada na fazenda.

| Campo | Tipo | Nulo? | Chave | Descrição e Regras |
| :--- | :---: | :---: | :---: | :--- |
| `ID_CULTURA` | INTEGER | Não | PK | Identificador numérico sequencial da cultura |
| `NOME_CULTURA` | VARCHAR(50) | Não | Unique | Nome comercial (ex: Milho, Soja, Café) |
| `VARIEDADE` | VARCHAR(50) | Não | - | Linhagem/cultivar agronômica |
| `CICLO_DIAS` | INTEGER | Não | - | Duração média do ciclo até colheita |
| `UMIDADE_MINIMA_PCT` | REAL | Não | - | Ponto de murcha / estresse hídrico inferior |
| `UMIDADE_MAXIMA_PCT` | REAL | Não | - | Capacidade de campo máxima recomendada |
| `PH_IDEAL_MIN` | REAL | Não | - | Limite inferior de acidez aceitável |
| `PH_IDEAL_MAX` | REAL | Não | - | Limite superior de pH |

---

## 2. Tabela `FT4_TALHAO`
Mapeia as subdivisões físicas e geográficas da propriedade agrícola.

| Campo | Tipo | Nulo? | Chave | Descrição e Regras |
| :--- | :---: | :---: | :---: | :--- |
| `CODIGO_TALHAO` | VARCHAR(20) | Não | PK | Código unívoco do talhão (ex: `TALHAO_01`) |
| `NOME_TALHAO` | VARCHAR(100) | Não | - | Nome descritivo de localização |
| `AREA_HECTARES` | REAL | Não | - | Extensão territorial em hectares |
| `TIPO_SOLO` | VARCHAR(50) | Não | - | Classificação pedológica (ex: Latossolo Vermelho) |
| `ID_CULTURA` | INTEGER | Não | FK | Referência à cultura plantada (`FT4_CULTURA`) |
| `STATUS_OPERACIONAL` | VARCHAR(30) | Não | - | Situação (`EM_PRODUCAO`, `POUSIO`, `PREPARO`) |

---

## 3. Tabela `FT4_SENSOR`
Cadastro dos dispositivos físicos e estações de telemetria instaladas em campo (AICSS).

| Campo | Tipo | Nulo? | Chave | Descrição e Regras |
| :--- | :---: | :---: | :---: | :--- |
| `CODIGO_SENSOR` | VARCHAR(30) | Não | PK | Identificador do hardware (ex: `SNS-UMID-01`) |
| `CODIGO_TALHAO` | VARCHAR(20) | Não | FK | Talhão onde o sensor está instalado |
| `TIPO_SENSOR` | VARCHAR(50) | Não | - | Tipo de variável (`UMIDADE_CAPACITIVA`, `NPK`, `PH`) |
| `MODELO_HARDWARE` | VARCHAR(50) | Não | - | Modelo do componente (ex: `DHT22/Capacitive v1.2`) |
| `DATA_INSTALACAO` | DATE | Não | - | Data de comissionamento em campo |
| `STATUS_ATIVO` | INTEGER | Não | - | 1 para ativo, 0 para inativo |

---

## 4. Tabela `FT4_LEITURA_SENSOR`
Série temporal de monitoramento contínuo das variáveis de solo e clima (2.880 registros históricos).

| Campo | Tipo | Nulo? | Chave | Descrição e Regras |
| :--- | :---: | :---: | :---: | :--- |
| `ID_LEITURA` | INTEGER | Não | PK | Identificador sequencial da leitura |
| `DATA_HORA` | TIMESTAMP | Não | - | Carimbo de data/hora da medição |
| `CODIGO_TALHAO` | VARCHAR(20) | Não | FK | Talhão de origem da leitura |
| `UMIDADE_SOLO` | REAL | Não | - | Umidade volumétrica em percentual (0 a 100%) |
| `PH_SOLO` | REAL | Não | - | Potencial hidrogeniônico (3.5 a 9.0) |
| `FOSFORO_OK` | INTEGER | Não | - | Indicador binário de fósforo (1=Adequado, 0=Deficiente) |
| `POTASSIO_OK` | INTEGER | Não | - | Indicador binário de potássio (1=Adequado, 0=Deficiente) |
| `NITROGENIO_OK` | INTEGER | Não | - | Indicador binário de nitrogênio (1=Adequado, 0=Deficiente) |
| `ESTADO_BOMBA` | INTEGER | Não | - | Estado físico da bomba (1=Ligada, 0=Desligada) |
| `PREVISAO_CHUVA` | INTEGER | Não | - | Previsão meteorológica (1=Chuva prevista, 0=Sem chuva) |
| `ACAO_SISTEMA` | VARCHAR(30) | Não | - | Ação executada (`IRRIGAR`, `REPOUSO`, `ALERTA`) |
| `ORIGEM_DADO` | VARCHAR(30) | Não | - | Origem (`ESP32_WOKWI`, `FASE3_HISTORICO`) |

---

## 5. Tabela `FT4_ACIONAMENTO_IRRIGACAO`
Registro dos ciclos de bombeamento executados pelo sistema automatizado.

| Campo | Tipo | Nulo? | Chave | Descrição e Regras |
| :--- | :---: | :---: | :---: | :--- |
| `ID_ACIONAMENTO` | INTEGER | Não | PK | Código da sessão de irrigação |
| `DATA_HORA_INICIO` | TIMESTAMP | Não | - | Início do fluxo de água |
| `DATA_HORA_FIM` | TIMESTAMP | Sim | - | Término do ciclo |
| `CODIGO_TALHAO` | VARCHAR(20) | Não | FK | Talhão irrigado |
| `DURACAO_MINUTOS` | INTEGER | Não | - | Duração total do acionamento |
| `VOLUME_LITROS` | REAL | Não | - | Volume de lâmina d'água aplicado |
| `MOTIVO_ACIONAMENTO` | VARCHAR(50) | Não | - | Justificativa técnica ou comando do modelo de IA |

---

## 6. Tabela `FT4_OCORRENCIA_CAMPO`
Cadastro de anomalias visuais observadas por operadores e rondas na lavoura.

| Campo | Tipo | Nulo? | Chave | Descrição e Regras |
| :--- | :---: | :---: | :---: | :--- |
| `ID_OCORRENCIA` | INTEGER | Não | PK | Identificador da ocorrência |
| `DATA_HORA` | TIMESTAMP | Não | - | Momento do registro |
| `CODIGO_TALHAO` | VARCHAR(20) | Não | FK | Talhão inspecionado |
| `TIPO_OCORRENCIA` | VARCHAR(50) | Não | - | `PRAGA_LAGARTA`, `QUEIMADURA_GEADA`, `FUNGOS`, etc. |
| `GRAVIDADE` | VARCHAR(20) | Não | - | Nível de risco (`BAIXA`, `MEDIA`, `ALTA`, `CRITICA`) |
| `OBSERVACAO` | TEXT | Não | - | Descrição técnica das folhas e sintomas |
| `OPERADOR` | VARCHAR(50) | Não | - | Usuário que assinou o registro |
| `HASH_INTEGRIDADE` | VARCHAR(64) | Não | - | **Hash SHA-256 criptográfico para detecção de adulteração** |
| `STATUS_TRATAMENTO` | VARCHAR(30) | Não | - | `ABERTO`, `EM_ANALISE`, `TRATADO` |

---

## 7. Tabela `FT4_PREVISAO_MODELO`
Armazena as inferências do modelo de Machine Learning (Random Forest) para auditoria contínua.

| Campo | Tipo | Nulo? | Chave | Descrição e Regras |
| :--- | :---: | :---: | :---: | :--- |
| `ID_PREVISAO` | INTEGER | Não | PK | Código da previsão |
| `DATA_HORA` | TIMESTAMP | Não | - | Momento da inferência |
| `CODIGO_TALHAO` | VARCHAR(20) | Não | FK | Talhão avaliado pela IA |
| `UMIDADE_SOLO_ATUAL` | REAL | Não | - | Leitura de entrada no instante |
| `PH_ATUAL` | REAL | Não | - | pH de entrada |
| `PREDICAO_IRRIGAR` | INTEGER | Não | - | 1 para LIGAR, 0 para MANTER DESLIGADO |
| `PROBABILIDADE_IRRIGAR` | REAL | Não | - | Confiança probabilística da classe (0.0 a 1.0) |
| `CONDICAO_SOLO` | VARCHAR(30) | Não | - | `SECA`, `MODERADA`, `UMIDA` |
| `MODELO_VERSAO` | VARCHAR(50) | Não | - | Versão do artefato Scikit-Learn |
| `DECISAO_REGRA_FASE2` | INTEGER | Não | - | Decisão se fosse aplicada a regra antiga (< 30%) |
| `CONCORDANCIA_REGRA` | INTEGER | Não | - | 1 se IA e Regra Antiga concordaram; 0 se divergiram |

---

## 8. Tabela `FT4_LOG_SEGURANCA`
Trilha de auditoria cibernética imutável para conformidade com segurança da informação.

| Campo | Tipo | Nulo? | Chave | Descrição e Regras |
| :--- | :---: | :---: | :---: | :--- |
| `ID_LOG` | INTEGER | Não | PK | Código sequencial do evento |
| `DATA_HORA` | TIMESTAMP | Não | - | Carimbo temporal do evento |
| `EVENTO` | VARCHAR(50) | Não | - | `LOGIN_TENTATIVA`, `OCORRENCIA_CADASTRO`, `ALERTA_ADULTERACAO` |
| `USUARIO` | VARCHAR(50) | Não | - | Conta responsável |
| `IP_ORIGEM` | VARCHAR(45) | Não | - | Endereço IPv4 / IPv6 da requisição |
| `STATUS` | VARCHAR(20) | Não | - | `SUCESSO`, `FALHA`, `CRITICO` |
| `DETALHES` | TEXT | Sim | - | Contexto técnico do evento |
| `HASH_LOG` | VARCHAR(64) | Não | - | Hash encadeado garantindo a não-repudiação |

