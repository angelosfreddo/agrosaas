# Roteiro de Gravacao - FarmTech Solutions (Fase 2)

Utilize este roteiro como base para não esquecer nenhum detalhe importante durante o seu vídeo de apresentação de até 5 minutos.

---

## 1. Introdução (Apresentação do Projeto)
* **Fala Sugerida:** "Olá, aqui é o Angelo da equipe FarmTech Solutions. Nesta Fase 2 do nosso projeto, focamos em evoluir a gestão agrícola usando Internet das Coisas (IoT). O desafio foi criar um protótipo de sistema de irrigação inteligente e automatizado que tomasse decisões com base em sensores ambientais e dados externos."

## 2. Apresentação do Circuito (Wokwi)
* **O que mostrar:** Mostre a tela do Wokwi com o circuito montado.
* **Explique as Substituições Didáticas:**
  * **DHT22:** Mede a umidade do solo (abaixo de 40% a bomba liga).
  * **Relé Azul:** Simula a nossa bomba d'água de irrigação.
  * **3 Botões Verdes:** Representam os sensores de Nutrientes (N, P e K). Pressionados = nível OK. Soltos = nível Baixo.
  * **Sensor LDR (Luz):** Simula o nosso pH. Mapeamos de 0 a 14. O ideal é ficar entre 6 e 7.

## 3. Demonstração Prática da Lógica C/C++
* **Ação 1 (A Bomba):** Dê play no Wokwi. Altere a umidade do DHT22 para menos de 40% e mostre o Relé ligando. Depois suba para 60% e mostre o Relé desligando.
* **Ação 2 (Fertirrigação):** Com a bomba ligada, solte um dos botões verdes. Mostre no monitor serial a mensagem de `"INICIANDO FERTIRRIGAÇÃO"` (injetando água + nutriente que falta).
* **Ação 3 (Alerta de pH):** Arraste o medidor do LDR até o pH ficar muito ácido. Mostre no monitor o `"ALERTA: pH desbalanceado. Realize correção do solo."`

## 4. O Programa "Ir Além 1" - API Python
* **O que mostrar:** Mostre o código ou execute o script `clima_api.py` no terminal.
* **Fala Sugerida:** "Para irmos além e economizarmos água, criamos uma integração com Python consumindo a API meteorológica gratuita do Open-Meteo. Se a probabilidade de chuva nas próximas horas for alta, o sistema manda bloquear a irrigação."
* **Ação:** Mostre como o Python orienta a digitar o comando `1`. Vá no Wokwi, clique no terminal escuro, aperte `1` e `ENTER`. Mostre a mensagem de "Bomba Bloqueada por previsão de chuva".

## 5. O Programa "Ir Além 2" - Data Science com R
* **O que mostrar:** Mostre o script `analise_irrigacao.R`.
* **Fala Sugerida:** "Para fechar, aplicamos conceitos de Data Science com R. Simulei uma base de dados histórica do nosso solo e gerei a estatística descritiva (Média, Desvio Padrão, Mínimos e Máximos). Usei a tendência da média móvel dos últimos 3 dias para tomar uma decisão preditiva sobre ligar ou não a bomba hoje."

## 6. Encerramento
* **O que mostrar:** A tela do repositório no GitHub com as pastas organizadas (`fase1` e `fase2`) e o `README.md`.
* **Fala Sugerida:** "Toda a documentação, scripts e a lógica agronômica desenvolvida estão versionados em nosso GitHub, separando de forma organizada as fases do projeto. Muito obrigado!"

---
**Boa Gravação!**
