# Fase 2 - Sistema de Irrigacao Inteligente (FarmTech Solutions)

## Descricao do Projeto
Na Fase 2 do projeto da FarmTech Solutions, desenvolvemos um prototipo IoT no simulador Wokwi utilizando o microcontrolador ESP32. O objetivo e simular um sistema de irrigacao inteligente e autonomo, capaz de monitorar variaveis ambientais e tomar decisoes agronomicas em tempo real.

## Logica de Funcionamento
O sistema se baseia nas seguintes regras agronomicas para o acionamento da bomba de agua (Rele Azul):

1. **Umidade do Solo (Sensor DHT22)**:
   - Se a umidade cair para menos de 40%, o sistema liga a bomba para evitar o estresse hidrico da planta.
   - Se a umidade atingir 60% ou mais, a bomba e desligada para evitar encharcamento da raiz.

2. **Niveis de Nutrientes NPK (Botoes Verdes)**:
   - Os 3 botoes simulam a disponibilidade de Nitrogenio (N), Fosforo (P) e Potassio (K).
   - Se a bomba ligar e algum dos botoes apontar deficiencia, o sistema entra em modo de **FERTIRRIGACAO**, alertando no monitor serial que a agua injetada tambem esta carregando os nutrientes faltantes.

3. **Monitoramento de pH (Sensor LDR)**:
   - O sinal analogico do LDR e mapeado para uma escala de pH (0 a 14).
   - Se o pH sair da faixa ideal (6.0 a 7.0), o sistema emite um alerta para correcao do solo (calagem), avisando que a absorcao de nutrientes esta comprometida.

## Ir Alem 1: Integracao com API (Python)
Para otimizar os recursos hidricos da fazenda, criamos um script em Python (`python/clima_api.py`) que consome a API publica e gratuita do **Open-Meteo**.
Ele avalia a probabilidade de chuva nas proximas 12 horas. Se houver chuva forte prevista, o script orienta o envio do comando `1` via Monitor Serial para o ESP32. O microcontrolador interpreta o comando e imediatamente bloqueia a bomba, economizando agua. O envio do `0` libera a bomba.

## Ir Alem 2: Data Science (R)
Implementamos um script em R (`r_analysis/analise_irrigacao.R`) para aplicar estatistica a tomada de decisao. O script gera e analisa uma serie historica da umidade e temperatura do solo, calculando media, desvio padrao, minimo e maximo. Atraves da media movel de umidade dos ultimos 3 dias (tendencia), o algoritmo prescreve matematicamente a necessidade de acionar a irrigacao, complementando a visao instantanea do IoT.

## Estrutura de Arquivos
- `esp32/sketch.ino`: Codigo C/C++ rodando no ESP32.
- `esp32/diagram.json`: Estrutura do circuito para o simulador Wokwi.
- `python/clima_api.py`: Integracao automatizada com API climatica (Ir Alem 1).
- `r_analysis/analise_irrigacao.R`: Analise estatistica e preditiva (Ir Alem 2).

## Imagem do Circuito
*(Dica: Coloque aqui o print do seu diagrama do Wokwi com a montagem finalizada, renomeando o arquivo de imagem para `circuito_wokwi.png` dentro da pasta `docs` e descomentando a linha abaixo)*
<!-- ![Circuito Wokwi](./docs/circuito_wokwi.png) -->

## Video Demonstrativo
*(Insira o link para o seu video nao-listado do YouTube aqui com o pitch do grupo e a demonstracao rodando)*
[Link do Video no YouTube]
