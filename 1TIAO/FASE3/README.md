# FIAP - Fase 3: Banco de Dados Estruturado, Python Cientifico, NoSQL e Modelagem de IA (FarmTech Solutions)

**Aluno:** Angelo Guilherme Sfreddo (RM: 566580) - Turma 1TIAO

---

## Entregas da Fase 3

### [Cap 1 - Etapas de uma Maquina Agricola](./CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA/README.md)
- **Parte 1 (Python Cientifico e Visualizacao):** Exportacao das leituras do Monitor Serial do Wokwi (ESP32), complemento de historico para 4 meses (2.880 horas, de janeiro a abril de 2026), limpeza e filtragem de ruido por media movel com Pandas e NumPy, calculo de indicadores de manejo hidrico e geracao de quatro paineis graficos com Matplotlib e Seaborn.
- **Parte 2 (Oracle Database e Persistencia):** Levantamento de seis informacoes relevantes de gestao, criacao de quatro tabelas relacionais (`FT3_MANEJO_CULTURA`, `FT3_LEITURA_SENSOR`, `FT3_ACIONAMENTO_BOMBA`, `FT3_AVALIACAO_FASE2`), carga repetivel (`MERGE INTO`) integrando dados das Fases 1, 2 e 3, e execucao de seis consultas SQL de gestao.
- **Ir Alem 1 (ESP32 Eficiente):** Otimizacao de tipos de variaveis (`uint8_t`, `uint16_t`, bitmask, ponto fixo em decimos e `PROGMEM`), reduzindo em 62,5% as variaveis do sketch e preservando 100% da logica em 784 cenarios testados, alem de analise estatistica complementar em R.
- **Ir Alem 2 (MongoDB NoSQL):** Armazenamento das 2.881 leituras brutas como documentos JSON no MongoDB via `pymongo`, execucao de cinco consultas/agregacoes NoSQL e comparacao pratica com o Oracle Database.

Acesse a documentacao completa em [`CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA/README.md`](./CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA/README.md) e os desafios extras em [`CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA/IR-ALEM/README.md`](./CAP1-ETAPAS-DE-UMA-MAQUINA-AGRICOLA/IR-ALEM/README.md).

---

### [Cap 11 - Modelagem de IA da FarmTech Solutions](./CAP11-MODELAGEM-IA-FARMTECH/README.md)
- **Analise Exploratoria e Descritiva:** Inspecao completa da base `produtos_agricolas.csv` (2.200 observacoes balanceadas entre 22 culturas agricolas e 7 variaveis de solo e clima) com seis graficos estatisticos narrados.
- **Perfil Ideal e Comparativo de Culturas:** Definicao do perfil medio geral e comparacao estatistica/visual de Arroz (`rice`), Maca (`apple`) e Cafe (`coffee`) frente ao baseline da fazenda.
- **Modelagem Preditiva (5 Algoritmos):** Pipeline em Scikit-Learn com divisao estratificada e validacao cruzada de 5 folds sem vazamento de dados, comparando Floresta Aleatoria (`99,55%` de acuracia no teste), SVM RBF (`98,41%`), Arvore de Decisao (`98,18%`), KNN (`97,95%`) e Regressao Logistica (`97,27%`).

Acesse a documentacao completa em [`CAP11-MODELAGEM-IA-FARMTECH/README.md`](./CAP11-MODELAGEM-IA-FARMTECH/README.md) e o notebook executado em [`CAP11-MODELAGEM-IA-FARMTECH/notebooks/AngeloGuilhermeSfreddo_RM566580_fase3_cap11.ipynb`](./CAP11-MODELAGEM-IA-FARMTECH/notebooks/AngeloGuilhermeSfreddo_RM566580_fase3_cap11.ipynb).

