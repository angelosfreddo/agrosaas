# Ir Além 1 — Recomendação no Campo: Display LCD no ESP32

**Projeto:** FarmTech Solutions — Safra do Conhecimento Cibernético (Fase 4)  
**Aluno:** Angelo Guilherme Sfreddo (RM: 566580) — Turma: 1TIAO  

---

## 1. Objetivo
Levar as previsões do modelo de Inteligência Artificial e os alertas de ocorrências de campo (pragas/geadas) diretamente ao operador de campo através de um display LCD 16x2 conectado a um microcontrolador ESP32 via I2C, integrando a inteligência de software ao hardware da fazenda.

---

## 2. Componentes e Ligações (Wokwi)
- **Microcontrolador:** ESP32 DevKit V4
- **Display:** LCD 16x2 I2C (SDA -> GPIO 21, SCL -> GPIO 22, Endereço 0x27)
- **Sensor de Umidade do Ar / Solo:** DHT22 (GPIO 15) e Potenciômetro Analógico (GPIO 34)
- **Sinalizadores:**
  - LED Verde (GPIO 2): Lavoura estável / Bomba desligada
  - LED Azul (GPIO 4): Bomba de irrigação acionada pela recomendação da IA
  - LED Vermelho (GPIO 5): Alerta ativo de praga ou dano climático na lavoura

---

## 3. Protocolo de Mensagem Serial
A mensagem enviada da estação central para o ESP32 segue o formato padronizado:
```text
CMD|IRRIGAR:<0_ou_1>|SOLO:<SECA|MODERADA|UMIDA>|ALERTA:<TIPO_OCORRENCIA>
```

**Exemplo prático de comando:**
```text
CMD|IRRIGAR:1|SOLO:SECA|ALERTA:PRAGA_LAGARTA
```

---

## 4. Instruções de Execução no Wokwi
1. Acesse [https://wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32);
2. Cole o conteúdo de [`sketch.ino`](sketch.ino) na aba de código;
3. Cole o conteúdo de [`diagram.json`](diagram.json) na aba de conexões;
4. Adicione a biblioteca `LiquidCrystal I2C` e `DHT sensor library` no Library Manager;
5. Inicie a simulação (botão verde de Play);
6. No campo de entrada do **Serial Monitor** (na parte inferior), cole o comando:
   `CMD|IRRIGAR:1|SOLO:SECA|ALERTA:PRAGA_LAGARTA` e aperte Enter;
7. Observe o display LCD alternar a cada 3 segundos entre:
   - **Tela 1:** Leituras dos sensores (`Umid: XX% Solo` / `Temp: XX C`);
   - **Tela 2:** Decisão da IA (`IA:IRRIGAR [SECA]` / `Alt:PRAGA_LAGAR`);
8. O LED azul acende confirmando a ativação da irrigação recomendada pela IA e o LED vermelho sinaliza o alerta de praga.

