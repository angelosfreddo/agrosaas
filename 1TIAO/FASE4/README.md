# FarmTech Solutions - Fase 4: Safra do Conhecimento Cibernetico

Projeto academico desenvolvido para o curso de Inteligencia Artificial da FIAP (Turma 1TIAO).

- **Aluno:** Angelo Guilherme Sfreddo
- **RM:** 566580
- **Turma:** 1TIAO - FIAP
- **Ano:** 2026
- **Video Demonstrativo (YouTube):** [https://youtu.be/S4xxspncWF8](https://youtu.be/S4xxspncWF8)
- **Repositorio GitHub:** [https://github.com/angelosfreddo/agrosaas/tree/main/1TIAO/FASE4](https://github.com/angelosfreddo/agrosaas/tree/main/1TIAO/FASE4) *(Compartilhado com `fiap-tutoria`)*

---

## Sumario Executivo

A Fase 4 da solucao **FarmTech Solutions** representa a transicao da coleta simples de telemetria para a tomada de decisao inteligente e a protecao de ativos informacionais criticos. 

A solucao foi dividida em duas frentes fundamentais obrigatorias e duas frentes do programa Ir Alem:

1. **Parte 1 (Obrigatorio) - Modelo Preditivo e Painel de Monitoramento:**
   - Construcao e preparacao do dataset com 2.880 leituras horarias migradas da Fase 3.
   - Treinamento e comparacao de modelos preditivos no Scikit-Learn com 5-Fold Stratified Cross-Validation.
   - Confronto agronomico entre o modelo inteligente e a regra fixa da Fase 2 (`umidade < 30%`), demonstrando reducao de estresse hidrico em solos com 30% a 50% de umidade.
   - Dashboard interativo em Streamlit com visualizacao de series temporais de NPK, pH e umidade, simulador de inferencia em tempo real e operacoes CRUD de ocorrencias de campo.

2. **Parte 2 (Obrigatorio) - Memoria e Seguranca dos Dados:**
   - Modelo relacional completo (8 tabelas: culturas, talhoes, sensores, leituras, irrigacao, ocorrencias, previsoes e auditoria).
   - Diagrama Entidade-Relacionamento (DER), script SQL DDL e dicionario de dados detalhado.
   - Analise de riscos ciberneticos com matriz de probabilidade versus impacto.
   - Tres contramedidas implementadas: isolamento de credenciais em `.env`, autenticacao com salted SHA-256 e trilha de auditoria com hash criptografico de integridade e deteccao automatizada de adulteracao.

3. **Ir Alem 1 (Opcional) - Recomendacao no Campo com ESP32 e Display LCD:**
   - Prototipo Wokwi com firmware C++ para ESP32 e display LCD 16x2 I2C.
   - Recepcao serial de comandos preditivos do modelo em Python e alternancia automatica de exibicao entre telemetria fisica e decisao da IA.

4. **Ir Alem 2 (Opcional) - Descoberta de Perfis de Solo por Clusterizacao K-Means:**
   - Modelo nao supervisionado avaliando Metodo do Cotovelo e Coeficiente de Silhueta ($k=2..7$).
   - Segmentacao agronomica em 3 clusters (Solo Equilibrado, Solo com Deficit de Nitrogenio, Solo com Acidez e Deficit de Potassio).
   - Visualizacao grafica e integracao nativa ao Streamlit.

---

## Arquitetura do Repositorio

```text
farmtech-fase4/
|-- assets/
|   `-- diagramas/
|       |-- der_farmtech_fase4.png
|       |-- dispersao_clusters_solos.png
|       |-- matriz_confusao_modelo.png
|       `-- metodo_cotovelo_kmeans.png
|-- data/
|   `-- farmtech_fase4.db
|-- docs/
|   |-- analise_riscos_seguranca.md
|   |-- dicionario_de_dados.md
|   |-- roteiro_video.md
|   `-- modelagem/
|       |-- der_modelo_logico_farmtech_fase4.png
|       `-- modelo_relacional_farmtech_fase4.sql
|-- IR_ALEM/
|   |-- IR_ALEM_1_ESP32_LCD/
|   |   |-- README.md
|   |   |-- diagram.json
|   |   |-- enviar_recomendacao_serial.py
|   |   |-- libraries.txt
|   |   `-- sketch.ino
|   `-- IR_ALEM_2_CLUSTERIZACAO/
|       |-- README.md
|       `-- clusterizacao_solos.py
|-- models/
|   |-- kmeans_perfis_solo.joblib
|   |-- modelo_irrigacao_farmtech.joblib
|   `-- scaler_irrigacao.joblib
|-- notebooks/
|   `-- pipeline_ml_irrigacao.ipynb
|-- src/
|   |-- app_dashboard.py
|   |-- database.py
|   |-- security.py
|   `-- train_model.py
|-- .env
|-- .env.example
|-- .gitignore
|-- entrega_fase4.txt
|-- README.md
`-- requirements.txt
```

---

## Instrucoes de Instalacao e Execucao

### 1. Pre-requisitos e Ambiente Virtual

Recomenda-se o uso de Python 3.10 ou superior.

```bash
# Navegar para a pasta do projeto
cd /home/angelo/FIAP/fase4/farmtech-fase4

# Ativar o ambiente virtual (ou criar um novo: python3 -m venv .venv && source .venv/bin/activate)
source /home/angelo/FIAP/.venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuracao de Variaveis de Ambiente

Copie o arquivo de exemplo e ajuste as configuracoes de seguranca conforme necessario:

```bash
cp .env.example .env
```

Configuracoes padrao de seguranca no `.env`:
- `ADMIN_USER=admin`
- `ADMIN_PASSWORD_HASH=3a28d48666e6786d973db885dd645df7cd1e6fb14ed337417e3c8a9559f0e08c` *(senha correspondente: `farmtech2026`)*
- `APP_SECRET_SALT=farmtech_cybersecurity_secret_salt_2026`

### 3. Inicializacao do Banco de Dados

Caso queira reconstruir a base a partir do zero ou rodar testes de integridade:

```bash
python src/database.py
```

### 4. Treinamento e Avaliacao do Modelo Preditivo (Scikit-Learn)

Para executar o pipeline de treino, validacao cruzada em 5 folds e exportacao dos modelos `.joblib`:

```bash
python src/train_model.py
```

Resultados gerados:
- Modelo salvo em `models/modelo_irrigacao_farmtech.joblib`.
- Grafico de matriz de confusao salvo em `assets/diagramas/matriz_confusao_modelo.png`.
- Tabela `FT4_PREVISAO_MODELO` populada no banco relacional.

### 5. Execucao do Painel Streamlit

Para iniciar o dashboard com autenticacao e CRUD completo:

```bash
streamlit run src/app_dashboard.py
```

Acesse no navegador: `http://localhost:8501`.
Credenciais de acesso padrao:
- **Usuario:** `admin`
- **Senha:** `farmtech2026`

### 6. Execucao das Frentes do Programa Ir Alem

- **Ir Alem 1 (ESP32 LCD):**
  Consulte os diagramas e codigo em [IR_ALEM/IR_ALEM_1_ESP32_LCD/README.md](file:///home/angelo/FIAP/fase4/farmtech-fase4/IR_ALEM/IR_ALEM_1_ESP32_LCD/README.md).
  Para testar a transmissao serial local:
  ```bash
  python IR_ALEM/IR_ALEM_1_ESP32_LCD/enviar_recomendacao_serial.py
  ```

- **Ir Alem 2 (Clusterizacao K-Means):**
  Consulte as analises em [IR_ALEM/IR_ALEM_2_CLUSTERIZACAO/README.md](file:///home/angelo/FIAP/fase4/farmtech-fase4/IR_ALEM/IR_ALEM_2_CLUSTERIZACAO/README.md).
  Para re-executar a analise de clusters e gerar curvas de Elbow/Silhouette:
  ```bash
  python IR_ALEM/IR_ALEM_2_CLUSTERIZACAO/clusterizacao_solos.py
  ```

---

## Resultados do Modelo Preditivo (Parte 1)

O modelo avaliou quatro arquiteturas distintas via validacao cruzada estratificada em 5 folds:

| Algoritmo | Acuracia Media | F1-Score Medio | Desvio Padrao |
| :--- | :---: | :---: | :---: |
| **Random Forest Classifier** | **100.00%** | **1.0000** | $\pm 0.0000$ |
| **Gradient Boosting Classifier** | **100.00%** | **1.0000** | $\pm 0.0000$ |
| **Decision Tree Classifier** | **100.00%** | **1.0000** | $\pm 0.0000$ |
| **Regressao Logistica** | **99.26%** | **0.9856** | $\pm 0.0048$ |

### Comparativo com a Regra Fixa da Fase 2:
- **Concordancia:** 66.5% das leituras.
- **Divergencia Positiva (Ganho Agronomico):** O modelo inteligente identificou 193 situacoes em que a umidade do solo estava entre 30% e 50%, mas com deficit nutricional severo e alta temperatura. A regra rigida da Fase 2 (`umidade < 30%`) deixou a plantacao sofrer deficit hidrico, enquanto o modelo preditivo antecipou a irrigacao.

---

## Seguranca Cibernetica e Auditoria (Parte 2)

As tres contramedidas implementadas sao:
1. **Credenciais Fora do Codigo:** Todas as senhas, hashes e salts residem no `.env`, ignorado pelo git.
2. **Controle de Acesso:** Sessao protegida no Streamlit com comparacao de hashes SHA-256 com salt de aplicacao.
3. **Trilha de Auditoria com Verificacao de Integridade:** Cada ocorrencia gravada no banco recebe um hash criptografico:
   $$\text{Hash} = \text{SHA256}(\text{ID} \parallel \text{DataHora} \parallel \text{Talhao} \parallel \text{Tipo} \parallel \text{Severidade} \parallel \text{Descricao})$$
   O sistema permite auditoria instantanea e detecta pontualmente registros alterados via SQL direto ou ataques de banco de dados.

Para executar o teste de deteccao de adulteracao:
```bash
python src/security.py
```

---

## Documentos Complementares

- [Dicionario de Dados](file:///home/angelo/FIAP/fase4/farmtech-fase4/docs/dicionario_de_dados.md)
- [Analise de Riscos Ciberneticos](file:///home/angelo/FIAP/fase4/farmtech-fase4/docs/analise_riscos_seguranca.md)
- [Roteiro de Gravacao do Video](file:///home/angelo/FIAP/fase4/farmtech-fase4/docs/roteiro_video.md)
- [Script DDL Relacional SQL](file:///home/angelo/FIAP/fase4/farmtech-fase4/docs/modelagem/modelo_relacional_farmtech_fase4.sql)
- [Caderno Jupyter de Treinamento](file:///home/angelo/FIAP/fase4/farmtech-fase4/notebooks/pipeline_ml_irrigacao.ipynb)

---

## Integrantes do Grupo

- Angelo Guilherme Sfreddo (RM: 566580) - Turma: 1TIAO

