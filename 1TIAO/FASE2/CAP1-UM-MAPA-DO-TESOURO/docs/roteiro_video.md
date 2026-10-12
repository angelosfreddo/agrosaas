# ROTEIRO DE GRAVACAO DO VIDEO - FASE 2 (MAXIMO 5 MINUTOS)

**Objetivo:** Gravacao de tela (Streamyard, OBS, Loom ou gravador de tela nativo) demonstrando o prototipo IoT da Fase 2 (ESP32 no Wokwi), a integracao com a API climatica em Python e a analise estatistica de dados em R.

---

### Cronograma Geral (Duracao Total: ~4 minutos e 30 segundos)

| Etapa | Tempo Estimado | Conteudo Principal |
| :--- | :--- | :--- |
| 1. Introducao | 0:00 - 0:45 | Apresentacao da equipe, Startup FarmTech Solutions e contexto da cultura (Milho) |
| 2. Simulacao IoT no Wokwi | 0:45 - 2:30 | Sensores (DHT22, LDR pH, Botoes NPK), Rele Azul e Fertirrigacao |
| 3. Ir Alem 1: Integracao Python | 2:30 - 3:30 | Execucao do script de previsao de chuva e comando Serial no ESP32 |
| 4. Ir Alem 2: Data Science em R | 3:30 - 4:10 | Execucao do script R, media movel e recomendacao preditiva |
| 5. Encerramento | 4:10 - 4:30 | Consideracoes finais e estrutura do repositorio GitHub |

---

### Passo a Passo Detalhado para o Video

#### 1. Introducao (0:00 - 0:45)
- **O que falar:**
  "Ola professor e avaliadores! Somos da equipe da Startup FarmTech Solutions. Dando continuidade a Fase 1 do nosso projeto de Agricultura Digital, apresentamos agora a Fase 2: o Sistema de Irrigacao Inteligente e Fertirrigacao Automatizada. Escolhemos a cultura do Milho (Zea mays), fundamentada nos parametros agronomicos da Embrapa Milho e Sorgo."
- **O que mostrar:**
  - Aba aberta no navegador com o simulador Wokwi pronto para execucao.

---

#### 2. Prototipo IoT no Simulador Wokwi (0:45 - 2:30)
- **Acao 1 - Iniciar a simulacao:**
  - Clique no botao Play (verde) no Wokwi.
  - Aponte os componentes na tela: ESP32, sensor DHT22 (umidade), 3 botoes verdes (N, P e K), sensor LDR (pH) e o rele azul (bomba d'agua).
- **Acao 2 - Demonstrar a regra de Umidade e Acionamento da Bomba:**
  - "O sensor DHT22 simula a umidade do solo. Segundo a Embrapa, o nivel critico de estresse hidrico no milho ocorre abaixo de 40%."
  - Mova o slider do DHT22 para 35%. Mostre no Monitor Serial a mensagem e o LED do Rele Azul acendendo.
  - Mova o slider do DHT22 para 65% (acima de 60%). Mostre o Rele Azul desligando para evitar desperdicio e saturacao da raiz.
- **Acao 3 - Demonstrar a Fertirrigacao com os Botoes NPK:**
  - "Os 3 botoes verdes monitoram a disponibilidade de Nitrogenio, Fosforo e Potassio."
  - Deixe a umidade abaixo de 40% (ex: 35%) com algum nutriente em falta (botao solto / nivel baixo).
  - Mostre no Monitor Serial a acao: 'INICIANDO FERTIRRIGACAO (Injetando Agua + Nutrientes)'.
  - Pressione os botoes indicando nutrientes presentes e mostre o sistema migrando para 'IRRIGACAO COMUM (Apenas Agua)'.
- **Acao 4 - Demonstrar o Monitoramento de pH via LDR:**
  - "Utilizamos o sensor LDR mapeado na escala de 0 a 14 para representar o pH do solo. A faixa ideal do milho e de 6.0 a 7.0."
  - Mova o cursor de luminosidade do LDR para gerar um pH abaixo de 6.0 ou acima de 7.0.
  - Mostre o aviso no Monitor Serial: 'ALERTA: pH desbalanceado. Realize a correcao do solo.'

---

#### 3. Ir Alem 1: Integracao Python com API Publica (2:30 - 3:30)
- **O que falar:**
  "Para evitar irrigacoes desnecessarias, criamos um modulo em Python que consome a API publica da Open-Meteo para prever chuvas nas proximas 12 horas."
- **Acao:**
  - Abra o terminal e execute:
    `python3 agrosaas/fase2/python/clima_api.py`
  - Aponte a resposta da API mostrando a probabilidade de chuva obtida.
  - Quando a previsao acusar chuva, o script orienta o envio do comando '1' via Serial.
  - Volte ao Monitor Serial do Wokwi, digite `1` e pressione Enter.
  - Mostre a mensagem no ESP32: 'COMANDO RECEBIDO: Previsao de Chuva! Irrigacao Suspensa.' e o bloqueio imediato do rele da bomba.
  - Em seguida, envie `0` no Serial para demonstrar a liberacao do sistema de volta a operacao normal.

---

#### 4. Ir Alem 2: Data Science em R (3:30 - 4:10)
- **O que falar:**
  "Como diferencial analitico, desenvolvemos um script em R para analise estatistica de series historicas do solo."
- **Acao:**
  - No terminal, execute:
    `Rscript agrosaas/fase2/r_analysis/analise_irrigacao.R`
  - Mostre a saida no terminal: media, desvio padrao, valores minimos e maximos dos ultimos 10 dias.
  - Destaque o calculo da media movel dos ultimos 3 dias (tendencia) e a tomada de decisao automatizada do algoritmo prescrevendo se a bomba deve ser acionada.

---

#### 5. Encerramento (4:10 - 4:30)
- **O que falar:**
  "Nosso projeto cumpriu todos os requisitos fundamentais e opcionais solicitados na Fase 2: prototipo funcional com ESP32, integracao via API meteorologica em Python e inteligencia analitica com R. Todo o codigo, diagramas e documentacoes estao organizados no GitHub da equipe. Muito obrigado!"

---

### Checklist antes de Publicar
1. Verifique se o video nao ultrapassou 5 minutos.
2. Certifique-se de que a voz esta clara e o monitor serial esta visivel.
3. Suba o video no YouTube na modalidade 'Nao Listado' (Unlisted).
4. Copie a URL do video gerado e cole dentro do arquivo `fase2/docs/link_video.txt` e no `fase2/README.md`.
