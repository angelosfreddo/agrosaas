# ROTEIRO DE GRAVACAO DO VIDEO (MAXIMO 5 MINUTOS)

**Objetivo:** Gravacao de tela (Streamyard, OBS, Loom ou gravador de tela simples) demonstrando o funcionamento das aplicacoes Python e R.

---

### Cronograma do Video (Total: ~4 minutos e 30 segundos)

#### 1. Introducao (0:00 - 0:40)
- **O que falar:** "Ola professor(a)! Somos da equipe de desenvolvimento da Startup FarmTech Solutions. Este e o projeto da Fase 1 de Agricultura Digital."
- **O que mostrar:** Tela inicial do VS Code ou Terminal no diretorio do projeto.
- **Destaques:** Apresentar os integrantes e mencionar as duas culturas escolhidas (Cafe e Milho).

---

#### 2. Demonstracao da Aplicacao Python (0:40 - 2:30)
- **Acao:** No terminal, execute: `python3 src/python/main.py`
- **Passo a Passo no Menu:**
  - **Opcao 2 (Saida de dados):** Exiba a lista inicial de vetores pre-carregados (IDs 1 a 5). Explique que os dados de area e insumo estao armazenados em vetores paralelos.
  - **Opcao 1 (Entrada de dados):** Cadastre um novo registro (ex: Cultura Cafe, comprimento 100m, largura 50m, dosagem 200 mL/m, 10 ruas). Mostre o calculo automatico da area e dos litros de insumo.
  - **Opcao 3 (Atualizacao de dados):** Escolha uma posicao do vetor (ex: indice 0) e altere a area ou quantidade de insumo.
  - **Opcao 4 (Delecao de dados):** Elimine um registro por indice para comprovar a delecao no vetor.
  - **Opcao 2 (Re-exibir):** Mostre a tabela atualizada para comprovar todas as alteracoes CRUD.
  - **Opcao 5 (Sair):** Encerre o programa e mostre a mensagem de exportacao para o arquivo CSV (`data/dados_fazenda.csv`).

---

#### 3. Demonstracao das Aplicacoes em R (2:30 - 3:50)
- **Acao 1 (Estatistica Basica):** No terminal, execute: `Rscript src/r/analysis.R`
  - **O que falar:** "Agora na aplicacao em R, lemos o arquivo CSV gerado pelo Python para calcular as estatisticas basicas: Media de area (ha), Desvio Padrao, Mediana, Minimo e Maximo, alem da analise comparativa agrupada por cultura."
- **Acao 2 (Diferencial 'Ir Alem' - API Meteorologica):** No terminal, execute: `Rscript src/r/weather.R`
  - **O que falar:** "No requisito 'Ir Alem', desenvolvemos em R a conexao via API publica Open-Meteo sem chave. O script coleta em tempo real a temperatura, velocidade do vento, condicao do tempo e emite uma recomendacao agronomica para pulverizacao."

---

#### 4. Encerramento (3:50 - 4:15)
- **O que falar:** "Todos os arquivos (Python, R, resumo do artigo da Embrapa em A4 e este link de video) foram organizados no pacote ZIP para entrega na plataforma. Muito obrigado!"

---

### Dicas Importantes para Gravacao
1. Use o Streamyard ou OBS Studio / gravador de tela nativo.
2. Teste o microfone antes de iniciar.
3. Certifique-se de que a fonte do terminal esteja legivel.
4. Apos gravar, faca o upload no YouTube, selecione a opcao "Nao Listado" (Unlisted) nas configuracoes de visibilidade e cole a URL no arquivo link_video.txt.
