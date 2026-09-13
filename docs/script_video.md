# ROTEIRO DE GRAVAÇÃO DO VÍDEO (MÁXIMO 5 MINUTOS)

**Objetivo:** Gravação de tela (Streamyard, OBS, Loom ou gravador de tela simples) demonstrando o funcionamento das aplicações Python e R.

---

### ⏱️ Cronograma do Vídeo (Total: ~4 minutos e 30 segundos)

#### 1. Introdução (0:00 - 0:40)
- **O que falar:** "Olá professor(a)! Somos da equipe de desenvolvimento da Startup **FarmTech Solutions**. Este é o projeto da Fase 1 de Agricultura Digital."
- **O que mostrar:** Tela inicial do VS Code ou Terminal no diretório do projeto.
- **Destaques:** Apresentar os integrantes e mencionar as duas culturas escolhidas (**Café** e **Milho**).

---

#### 2. Demonstração da Aplicação Python (0:40 - 2:30)
- **Ação:** No terminal, execute: `python3 src/python/main.py`
- **Passo a Passo no Menu:**
  - **Opção 2 (Saída de dados):** Exiba a lista inicial de vetores pré-carregados (IDs 1 a 5). Explique que os dados de área e insumo estão armazenados em **vetores paralelos**.
  - **Opção 1 (Entrada de dados):** Cadastre um novo registro (ex: Cultura Café, comprimento 100m, largura 50m, dosagem 200 mL/m, 10 ruas). Mostre o cálculo automático da área e dos litros de insumo.
  - **Opção 3 (Atualização de dados):** Escolha uma posição do vetor (ex: índice 0) e altere a área ou quantidade de insumo.
  - **Opção 4 (Deleção de dados):** Elimine um registro por índice para comprovar a deleção no vetor.
  - **Opção 2 (Re-exibir):** Mostre a tabela atualizada para comprovar todas as alterações CRUD.
  - **Opção 5 (Sair):** Encerre o programa e mostre a mensagem de exportação para o arquivo CSV (`data/dados_fazenda.csv`).

---

#### 3. Demonstração das Aplicações em R (2:30 - 3:50)
- **Ação 1 (Estatística Básica):** No terminal, execute: `Rscript src/r/analysis.R`
  - **O que falar:** "Agora na aplicação em R, lemos o arquivo CSV gerado pelo Python para calcular as estatísticas básicas: Média de área (ha), Desvio Padrão, Mediana, Mínimo e Máximo, além da análise comparativa agrupada por cultura."
- **Ação 2 (Diferencial "Ir Além" - API Meteorológica):** No terminal, execute: `Rscript src/r/weather.R`
  - **O que falar:** "No requisito 'Ir Além', desenvolvemos em R a conexão via API pública Open-Meteo sem chave. O script coleta em tempo real a temperatura, velocidade do vento, condição do tempo e emite uma recomendação agronômica para pulverização."

---

#### 4. Encerramento (3:50 - 4:15)
- **O que falar:** "Todos os arquivos (Python, R, resumo do artigo da Embrapa em A4 e este link de vídeo) foram organizados no pacote ZIP para entrega na plataforma. Muito obrigado!"

---

### 💡 Dicas Importantes para Gravação
1. Use o [Streamyard](https://streamyard.com) ou OBS Studio / gravador de tela nativo.
2. Teste o microfone antes de iniciar.
3. Certifique-se de que a fonte do terminal esteja legível.
4. Após gravar, faça o upload no YouTube, selecione a opção **"Não Listado"** (*Unlisted*) nas configurações de visibilidade e cole a URL no arquivo `link_video.txt`.
