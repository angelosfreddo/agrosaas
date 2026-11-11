# ATIVIDADE: MODELAGEM DE IA DA FARMTECH SOLUTIONS
## Recomendacao Inteligente de Culturas Agricolas com Algoritmos de Aprendizado Supervisionado

**Instituicao**: FIAP - Faculdade de Informatica e Administracao Paulista  
**Curso**: Analise e Desenvolvimento de Sistemas (Turma 1TIAO - 2026)  
**Fase 3**: Capitulo 11 - A primeira tecnica de aprendizado de maquina  
**Aluno**: Angelo Guilherme Sfreddo (RM: 566580)  

---

## 1. APRESENTACAO DA ATIVIDADE

Esta atividade avaliativa do Capitulo 11 da Fase 3 contempla o desenvolvimento de uma solucao completa de Inteligencia Artificial para a startup **FarmTech Solutions**.

O objetivo e analisar uma base de dados real de sensoriamento agricola (`produtos_agricolas.csv`) com 2.200 observacoes de campo e 22 culturas agricolas perfeitamente balanceadas (100 amostras cada), identificar o perfil ideal edafoclimatico, comparar o perfil geral com tres culturas distintas e construir, validar e comparar **5 modelos preditivos** baseados em algoritmos supervisionados diferentes.

---

## 2. ESTRUTURA DE DIRETORIOS

```text
modelagemIA_FarmTech/
|-- data/
|   `-- produtos_agricolas.csv      # Dataset original com 2.200 linhas e 8 colunas
|-- notebooks/
|   |-- AngeloGuilhermeSfreddo_RM566580_fase3_cap11.ipynb # Notebook executado (oficial)
|   |-- AngeloGuilhermeSfreddo_RM566580_fase3_cap2.ipynb  # Copia espelho de seguranca
|   |-- AngeloSfreddo_RM566580_fase3_cap11.ipynb          # Copia espelho de seguranca
|   `-- AngeloSfreddo_RM566580_fase3_cap2.ipynb           # Copia espelho de seguranca
|-- src/
|   `-- gerar_notebook.py           # Script orquestrador de construcao e execucao
|-- README.md                       # Documentacao tecnica completa
`-- requirements.txt                # Dependencias do ecossistema de Data Science
```

---

## 3. DICIONARIO DE DADOS

O conjunto de dados abrange as seguintes variaveis:
- `N`: quantidade de Nitrogenio no solo (mg/kg ou proporcao relativa);
- `P`: quantidade de Fosforo no solo (mg/kg);
- `K`: quantidade de Potassio no solo (mg/kg);
- `temperature`: temperatura media da regiao em graus Celsius;
- `humidity`: umidade relativa media do ar na regiao (%);
- `ph`: potencial hidrogenionico do solo (escala de 0 a 14);
- `rainfall`: precipitacao pluviometrica acumulada em milimetros (mm);
- `label`: tipo de cultura recomendada / plantada (variavel alvo / target).

Total de classes (22 culturas):
`rice`, `maize`, `chickpea`, `kidneybeans`, `pigeonpeas`, `mothbeans`, `mungbean`, `blackgram`, `lentil`, `pomegranate`, `banana`, `mango`, `grapes`, `watermelon`, `muskmelon`, `apple`, `orange`, `papaya`, `coconut`, `cotton`, `jute`, `coffee`.

---

## 4. RESUMO DOS ACHADOS E ANALISE VISUAL (6 GRAFICOS)

O notebook contem 6 graficos completos narrados em profundidade:

1. **Grafico 1 (Histogramas e KDE das Variaveis)**:
   - Evidencia a bimodalidade acentuada de Fosforo (P) e Potassio (K), com agrupamentos de culturas que necessitam de concentracoes nutricionais massivas (> 120 para P e > 180 para K);
   - Distribuicao normal de Temperatura (media 25.61 C) e pH (media 6.47, levemente acido a neutro);
   - Distribuicao com cauda longa a direita para Precipitacao (media 103.46 mm, alcancando ate 298.56 mm).

2. **Grafico 2 (Matriz de Correlacao Linear de Pearson)**:
   - Forte correlacao linear positiva entre Fosforo e Potassio (r = 0.736), indicando demandas sinergicas de adubacao em fruteiras de clima temperado;
   - Baixissima correlacao entre as demais variaveis (|r| < 0.10 na maioria dos pares), assegurando que cada sensor contribui com informacao ortogonal sem risco de instabilidade por multicolinearidade excessiva.

3. **Grafico 3 (Boxplots de Features por Cultura)**:
   - Revela a baixa dispersao intra-cultura e alta variabilidade inter-culturas, confirmando que cada especie vegetal possui uma assinatura edafoclimatica estreita e discriminavel;
   - `rice` destaca-se em precipitacao (> 230 mm), `chickpea` em umidade extremamente baixa (14% a 18%), e `apple`/`grapes` em picos isolados de potassio (K ~200).

4. **Grafico 4 (Dispersao Bivariada de Projecoes de Decisao)**:
   - No plano P vs K, `apple` e `grapes` formam um cluster isolado no quadrante superior direito;
   - No plano Temperatura vs Umidade, `chickpea` isola-se no quadrante frio/seco, enquanto `rice` se projeta na faixa tropical umida.

5. **Grafico 5 (Mapa de Calor em Z-Score das Medias por Cultura)**:
   - Apresenta a assinatura completa das 22 culturas padronizadas em escores Z, identificando claramente quais culturas sao hiper-exigentes ou hipo-tolerantes a cada fator.

6. **Grafico 6 (Importancia Relativa das Variaveis - Feature Importances)**:
   - O algoritmo de Floresta Aleatoria atribui a maior capacidade de discriminacao a Precipitacao Pluviometrica (22.8%), seguida por Umidade do Ar (22.1%), Fosforo no Solo (19.3%), Potassio (16.2%), Nitrogenio (10.9%), Temperatura (4.8%) e pH (3.9%).

---

## 5. O PERFIL IDEAL E COMPARATIVO DAS 3 CULTURAS DISTINTAS

### 5.1 O Perfil Medio Geral (Baseline)
- Nitrogenio (N): 50.55 kg/ha (+/- 36.92)
- Fosforo (P): 53.36 kg/ha (+/- 32.99)
- Potassio (K): 48.15 kg/ha (+/- 50.65)
- Temperatura: 25.62 C (+/- 5.06)
- Umidade do Ar: 71.48% (+/- 22.26)
- pH do Solo: 6.47 (+/- 0.77)
- Precipitacao Pluviometrica: 103.46 mm (+/- 54.96)

*Nota agronomica: Nao existe solo universalmente ideal. A produtividade otima ocorre no casamento entre a demanda ecofisiologica da especie e as condicoes de campo.*

### 5.2 Comparativo das 3 Culturas Selecionadas contra o Perfil Geral

| Variavel | Media Geral | Arroz (`rice`) | Desvio Arroz (%) | Maca (`apple`) | Desvio Maca (%) | Cafe (`coffee`) | Desvio Cafe (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Nitrogenio (N)** | 50.55 | 79.89 | +58.04% | 20.80 | -58.85% | 101.20 | +100.20% |
| **Fosforo (P)** | 53.36 | 47.58 | -10.84% | 134.22 | +151.52% | 28.74 | -46.14% |
| **Potassio (K)** | 48.15 | 39.87 | -17.20% | 199.89 | +315.15% | 29.94 | -37.82% |
| **Temperatura** | 25.62 C | 23.69 C | -7.52% | 22.63 C | -11.65% | 25.54 C | -0.30% |
| **Umidade** | 71.48% | 82.27% | +15.09% | 92.33% | +29.17% | 58.87% | -17.64% |
| **pH** | 6.47 | 6.43 | -0.68% | 5.93 | -8.34% | 6.79 | +4.96% |
| **Precipitacao** | 103.46 mm | 236.18 mm | **+128.27%** | 112.65 mm | +8.88% | 158.07 mm | **+52.78%** |

**Sintese Agronomica**:
- **Arroz (`rice`)**: Exige solos encharcados e altissima precipitacao (+128.27%), com umidade do ar elevada para evitar estresse evaporativo;
- **Maca (`apple`)**: Planta de clima temperado mais ameno (22.63 C), exigindo solos com concentracoes extremas de Potassio (+315.15%) e Fosforo (+151.52%) para a fase de florada e frutificacao, com baixissima tolerancia a excesso de Nitrogenio (-58.85%);
- **Cafe (`coffee`)**: Cultura perene com alta biomassa foliar, demandando altas cargas de adubacao nitrogenada (+100.20%), chuvas bem distribuidas (+52.78%) e umidade moderada (58.87%) para mitigar proliferacao de ferrugem.

---

## 6. COMPARATIVO DOS 5 MODELOS PREDITIVOS

Todos os modelos foram avaliados em uma particao independente de teste (440 amostras estratificadas) e em validacao cruzada estratificada de 5 folds sobre o conjunto de treino (1.760 amostras), com padronizacao ajustada sem vazamento de dados (`Data Leakage`):

| Posicao | Algoritmo | Familia Matematica | CV Acuracia Media | CV Desvio Padrao | Acuracia Teste | Precisao (W) | Revocacao (W) | F1-Score (W) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Floresta Aleatoria (Random Forest)** | Ensemble (Bagging) | **0.9938** | 0.0061 | **0.9955** | **0.9957** | **0.9955** | **0.9955** |
| **2** | **SVM (Kernel RBF)** | Margem Maxima | 0.9795 | 0.0107 | 0.9841 | 0.9856 | 0.9841 | 0.9840 |
| **3** | **Arvore de Decisao** | Particionamento Recursivo | 0.9852 | 0.0071 | 0.9818 | 0.9830 | 0.9818 | 0.9817 |
| **4** | **KNN (k=5)** | Baseado em Distancia | 0.9653 | 0.0121 | 0.9795 | 0.9804 | 0.9795 | 0.9793 |
| **5** | **Regressao Logistica** | Linear Probabilistico | 0.9682 | 0.0066 | 0.9727 | 0.9740 | 0.9727 | 0.9725 |

O modelo campeao (**Floresta Aleatoria**) alcancou **99.55% de acuracia**, errando apenas 2 das 440 amostras de teste, demonstrando solidez extraordinaria para sistemas de recomendacao agronomica em tempo real.

---

## 7. COMO EXECUTAR OU VISUALIZAR O NOTEBOOK

### 7.1 Visualizacao do Notebook Executado
O arquivo principal contendo todas as saidas e graficos gerados esta em:
`notebooks/AngeloGuilhermeSfreddo_RM566580_fase3_cap11.ipynb`

### 7.2 Execucao Interativa
Para abrir e interagir com o notebook via Jupyter:
```bash
cd /home/angelo/FIAP/fase3/modelagemIA_FarmTech
source /home/angelo/FIAP/.venv/bin/activate
jupyter notebook notebooks/AngeloGuilhermeSfreddo_RM566580_fase3_cap11.ipynb
```

### 7.3 Reexecucao em Lote
Para reexecutar programaticamente todas as celulas do zero:
```bash
python src/gerar_notebook.py
```

---
**FarmTech Solutions - FIAP 2026**
