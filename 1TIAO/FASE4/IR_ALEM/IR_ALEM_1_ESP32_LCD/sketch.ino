/*
 * ==============================================================================
 * FIAP - GRADUAÇÃO EM INTELIGÊNCIA ARTIFICIAL
 * PROJETO FASE 4: SAFRA DO CONHECIMENTO CIBERNÉTICO (FARMTECH SOLUTIONS)
 * IR ALÉM 1: RECOMENDAÇÃO DE IA NO CAMPO COM DISPLAY LCD NO ESP32
 *
 * Aluno: Angelo Guilherme Sfreddo (RM: 566580) - Turma: 1TIAO
 *
 * Arquitetura de Hardware (Simulador Wokwi):
 *   - Microcontrolador: ESP32 DevKit V4
 *   - Sensores de Campo:
 *       DHT22 (Umidade e Temperatura do Ar/Solo): GPIO 15
 *       Potenciômetro Analógico (Sensor de Umidade do Solo): GPIO 34
 *   - Atuadores e Sinalizadores:
 *       Display LCD 16x2 I2C (SDA 21, SCL 22, Endereço 0x27)
 *       LED Verde (Irrigação Desligada / Solo OK): GPIO 2
 *       LED Azul (Bomba de Irrigação Ativa): GPIO 4
 *       LED Vermelho (Alerta de Praga/Geada na Lavoura): GPIO 5
 *   - Comunicação:
 *       Serial UART (115200 bps) recebendo comandos e recomendações da IA
 * ==============================================================================
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"

#define PIN_DHT 15
#define TYPE_DHT DHT22
#define PIN_POT_UMID 34

#define PIN_LED_VERDE 2
#define PIN_LED_BOMBA 4
#define PIN_LED_ALERTA 5

DHT dht(PIN_DHT, TYPE_DHT);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Variáveis de Estado da IA Recebidas via Serial
String recomendacaoIA = "DESLIGAR";
String condicaoSolo = "MODERADA";
String ultimoAlertaPraga = "NENHUM";
int acionarBomba = 0;

unsigned long ultimoEnvio = 0;
const unsigned long INTERVALO_LEITURA_MS = 2500;
unsigned long ultimoAlternanciaLCD = 0;
int telaAtual = 0; // 0 = Leituras de Campo, 1 = Recomendação da IA

void processarMensagemSerial(String msg) {
  // Formato de Mensagem Esperado:
  // "CMD|IRRIGAR:1|SOLO:SECA|ALERTA:PRAGA_LAGARTA"
  msg.trim();
  if (msg.startsWith("CMD|")) {
    int idxIrrig = msg.indexOf("IRRIGAR:");
    int idxSolo = msg.indexOf("SOLO:");
    int idxAlerta = msg.indexOf("ALERTA:");

    if (idxIrrig != -1) {
      acionarBomba = msg.substring(idxIrrig + 8, idxIrrig + 9).toInt();
      recomendacaoIA = (acionarBomba == 1) ? "IRRIGAR" : "DESLIGAR";
    }

    if (idxSolo != -1) {
      int fimSolo = msg.indexOf("|", idxSolo);
      if (fimSolo == -1) fimSolo = msg.length();
      condicaoSolo = msg.substring(idxSolo + 5, fimSolo);
    }

    if (idxAlerta != -1) {
      ultimoAlertaPraga = msg.substring(idxAlerta + 7);
    }

    // Registra recebimento no Monitor Serial com timestamp
    Serial.print("[");
    Serial.print(millis());
    Serial.print(" ms] COMANDO IA RECEBIDO: ");
    Serial.print("Recomendacao=");
    Serial.print(recomendacaoIA);
    Serial.print(" | Condicao=");
    Serial.print(condicaoSolo);
    Serial.print(" | Alerta=");
    Serial.println(ultimoAlertaPraga);
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_BOMBA, OUTPUT);
  pinMode(PIN_LED_ALERTA, OUTPUT);

  digitalWrite(PIN_LED_VERDE, HIGH);
  digitalWrite(PIN_LED_BOMBA, LOW);
  digitalWrite(PIN_LED_ALERTA, LOW);

  dht.begin();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("FarmTech Fase 4");
  lcd.setCursor(0, 1);
  lcd.print("Recomendacao IA");
  delay(1500);
  lcd.clear();

  Serial.println("==============================================================================");
  Serial.println("FIRMWARE ESP32 INICIADO - FARMTECH SOLUTIONS (IR ALEM 1)");
  Serial.println("Aguardando mensagens da IA no formato: CMD|IRRIGAR:X|SOLO:YYY|ALERTA:ZZZ");
  Serial.println("==============================================================================");
}

void loop() {
  unsigned long agora = millis();

  // Leitura de Comandos Recebidos na Porta Serial
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    processarMensagemSerial(msg);
  }

  // Controle dos Atuadores e LEDs com base na IA
  if (acionarBomba == 1) {
    digitalWrite(PIN_LED_BOMBA, HIGH);
    digitalWrite(PIN_LED_VERDE, LOW);
  } else {
    digitalWrite(PIN_LED_BOMBA, LOW);
    digitalWrite(PIN_LED_VERDE, HIGH);
  }

  if (ultimoAlertaPraga != "NENHUM" && ultimoAlertaPraga != "") {
    digitalWrite(PIN_LED_ALERTA, HIGH);
  } else {
    digitalWrite(PIN_LED_ALERTA, LOW);
  }

  // Alternância do Display LCD a cada 3 segundos
  if (agora - ultimoAlternanciaLCD >= 3000) {
    ultimoAlternanciaLCD = agora;
    telaAtual = 1 - telaAtual;
    lcd.clear();

    int adcSolo = analogRead(PIN_POT_UMID);
    float umidadeSolo = (float)adcSolo * (100.0 / 4095.0);
    float tempAr = dht.readTemperature();
    if (isnan(tempAr)) tempAr = 26.5;

    if (telaAtual == 0) {
      // Tela 1: Leituras dos Sensores no Campo
      lcd.setCursor(0, 0);
      lcd.print("Umid: ");
      lcd.print((int)umidadeSolo);
      lcd.print("% Solo");

      lcd.setCursor(0, 1);
      lcd.print("Temp: ");
      lcd.print((int)tempAr);
      lcd.print("C  Ar:OK");
    } else {
      // Tela 2: Decisão da Inteligência Artificial
      lcd.setCursor(0, 0);
      lcd.print("IA:");
      lcd.print(recomendacaoIA);
      lcd.print(" [");
      lcd.print(condicaoSolo.substring(0, 4));
      lcd.print("]");

      lcd.setCursor(0, 1);
      lcd.print("Alt:");
      if (ultimoAlertaPraga.length() > 11) {
        lcd.print(ultimoAlertaPraga.substring(0, 11));
      } else {
        lcd.print(ultimoAlertaPraga);
      }
    }
  }

  // Envio periódico de telemetria serial
  if (agora - ultimoEnvio >= INTERVALO_LEITURA_MS) {
    ultimoEnvio = agora;
    int adc = analogRead(PIN_POT_UMID);
    float umid = (float)adc * (100.0 / 4095.0);
    Serial.print("TELEMETRIA,");
    Serial.print(agora);
    Serial.print(",");
    Serial.print(umid, 1);
    Serial.print(",");
    Serial.println(acionarBomba);
  }
}

