# Roteiro de Gravacao do Video Demonstrativo - Fase 4
## FarmTech Solutions - Safra do Conhecimento Cibernetico

- Duracao maxima estipulada: Ate 4 minutos (240 segundos)
- Formato: Gravacao de tela com narracao em audio ou legendas
- Visibilidade no YouTube: Nao listado (Unlisted)
- Aluno: Angelo Guilherme Sfreddo (RM: 566580)
- Turma: 1TIAO - FIAP

---

### Cronograma e Roteiro Segundo a Segundo

#### Bloco 1: Abertura e Visao Geral da Fase 4 (00:00 - 00:35 | 35 segundos)
- Visual na tela:
  - Exibir a tela inicial do Dashboard Streamlit (com login efetuado) ou o arquivo README.md do repositorio.
- Fala sugerida do apresentador:
  "Ola a todos! Meu nome e Angelo Guilherme Sfreddo, RM 566580 da turma 1TIAO da FIAP. Apresento a solucao da Fase 4 do projeto FarmTech Solutions: Safra do Conhecimento Cibernetico.
  Nesta fase, evoluimos a solucao com duas frentes obrigatorias e duas frentes do programa Ir Alem:
  Primeiro, substitumos a regra fixa de irrigacao por um modelo preditivo treinado com Scikit-Learn e criamos um dashboard interativo em Streamlit com integracao CRUD.
  Segundo, desenhamos o modelo relacional de dados definitivo, com MER, DER e dicionario de dados, e implementamos contramedidas ciberneticas de controle de acesso, variaveis de ambiente e verificacao de integridade por hash SHA-256."

---

#### Bloco 2: Modelo Preditivo Scikit-Learn e Validacao Cruzada (00:35 - 01:25 | 50 segundos)
- Visual na tela:
  - Alternar para o terminal e executar: `python src/train_model.py` (ou mostrar o Jupyter Notebook `notebooks/pipeline_ml_irrigacao.ipynb`).
  - Mostrar os resultados da validacao cruzada estratificada (5-folds) e a matriz de confusao.
  - Mostrar o grafico de dispersao e o confronto com a regra fixa da Fase 2.
- Fala sugerida do apresentador:
  "A partir do historico de 2.880 leituras horarias estruturado na Fase 3, treinamos um modelo de classificacao com Random Forest e Gradient Boosting para prever a real necessidade de acionamento da irrigacao.
  Utilizamos validacao cruzada estratificada em 5 folds, alcancando acuracia e F1-Score superiores a 99%.
  Ao confrontar o modelo treinado com a regra estatica da Fase 2, que apenas acionava a bomba com umidade estritamente abaixo de 30%, o modelo de Machine Learning identificou 193 cenarios em que o solo estava entre 30% e 50% de umidade sob forte demanda evapotranspirativa e deficit nutricional. O modelo inteligente evitou estresse hidrico severo na lavoura, provando sua superioridade agronomica."

---

#### Bloco 3: Dashboard Interativo Streamlit e Operacoes CRUD (01:25 - 02:25 | 60 segundos)
- Visual na tela:
  - Navegar pelo Streamlit aberto no navegador (`localhost:8501`).
  - Aba 1 (Visao Geral): mostrar os cards de metricas (leituras, talhoes, status de bomba, alertas) e os graficos de serie temporal de umidade e nutrientes (N, P, K, pH).
  - Aba 2 (Previsoes IA): mostrar a tabela de previsoes geradas e a inferencia em tempo real simulando valores nos sliders.
  - Aba 3 (Ocorrencias de Campo): preencher o formulario ao vivo (cadastrar uma ocorrencia: Talhao 1, Tipo Praga, Severidade Alta, 'Lagarta do cartucho identificada em ronda visual') e clicar em 'Gravar Ocorrencia'. Mostrar a atualizacao imediata na tabela do banco.
- Fala sugerida do apresentador:
  "No painel Streamlit, o gestor agricola acompanha a variacao em tempo real de umidade, pH e macronutrientes NPK, com filtros dinamicos por talhao e periodo.
  Na aba de previsoes, o operador pode simular parametros de solo e receber a decisao imediata do modelo treinado.
  Na aba de ocorrencias de campo, implementamos o ciclo completo de cadastro: o operador registra presenca de pragas ou geadas observadas em rondas, associando talhao, data, gravidade e observacoes tecnicas, tudo persistido imediatamente no banco de dados SQLite/Oracle."

---

#### Bloco 4: Seguranca Cibernetica e Teste de Integridade (02:25 - 03:05 | 40 segundos)
- Visual na tela:
  - Aba 4 do Streamlit (Seguranca Cibernetica & Auditoria).
  - Destacar o mascaramento e leitura de variaveis de ambiente (.env).
  - Mostrar a trilha de auditoria na tabela `FT4_LOG_SEGURANCA`.
  - Clicar no botao 'Executar Verificacao Criptografica de Integridade (SHA-256)' e demonstrar o status verde 'Nenhuma Adulteracao Detectada'.
  - Mostrar o teste simulado de adulteracao rodando via terminal ou funcao no painel: `python src/security.py`.
- Fala sugerida do apresentador:
  "Para a frente de seguranca cibernetica, adotamos tres contramedidas cruciais:
  1. Credenciais fora do codigo-fonte atraves de variaveis de ambiente em arquivo .env protegido no .gitignore.
  2. Autenticacao com senha protegida por hash criptografico SHA-256 com salt aleatorio de aplicacao.
  3. Trilha de auditoria com geracao de hash de integridade SHA-256 para cada registro de ocorrencia. Em caso de manipulacao maliciosa direta no banco de dados, o algoritmo recalcula a assinatura e aponta exatamente o registro adulterado."

---

#### Bloco 5: Demonstracao do Programa Ir Alem e Encerramento (03:05 - 04:00 | 55 segundos)
- Visual na tela:
  - Ir Alem 1: Mostrar rapidamente o Wokwi (`IR_ALEM/IR_ALEM_1_ESP32_LCD/diagram.json` e `sketch.ino`) e o script `enviar_recomendacao_serial.py`, exibindo a alternancia das telas do LCD 16x2 I2C entre status dos sensores e a recomendacao vinda da IA ('IA: IRRIGAR', 'RISCO: CRITICO').
  - Ir Alem 2: Mostrar a Aba 5 do Streamlit ou o script `IR_ALEM/IR_ALEM_2_CLUSTERIZACAO/clusterizacao_solos.py` com o grafico do Metodo do Cotovelo e o agrupamento K-Means em 3 perfis agronomicos de solo.
  - Tela final: Repositorio GitHub organizado conforme as diretrizes FIAP.
- Fala sugerida do apresentador:
  "No programa Ir Alem, fomos em duas frentes:
  No Ir Alem 1, integramos o ESP32 com display LCD I2C 16x2 recebendo as recomendacoes da IA via comunicacao serial, permitindo que o operador de campo veja na hora se a bomba deve ser acionada.
  No Ir Alem 2, aplicamos clusterizacao nao supervisionada com K-Means e Metodo do Cotovelo para mapear automaticamente tres perfis de fertilidade de solo nos talhoes.
  Todos os codigos, esquematicos, DDLs e documentacao estao disponiveis no repositorio privado do GitHub compartilhado com o perfil fiap-tutoria. Muito obrigado!"

---

### Dicas para a Gravacao
1. Mantenha a resolucao da tela em 1080p (Full HD).
2. Utilize softwares gratuitos como OBS Studio ou o proprio gravador do sistema operacional.
3. Teste o microfone antes de gravar para assegurar audio claro e sem ecos.
4. Faca o upload no YouTube selecionando 'Nao listado' para que apenas quem tem o link consiga assistir.
5. Copie a URL do YouTube e atualize o arquivo `entrega_fase4.txt` e o `README.md`.

