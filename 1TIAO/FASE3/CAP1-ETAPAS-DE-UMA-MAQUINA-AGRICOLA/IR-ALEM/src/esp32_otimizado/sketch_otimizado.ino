// ============================================================================
// Projeto: FarmTech Solutions - Sistema de Irrigacao Inteligente (Fase 3)
// Desafio Opcional: IR ALEM 1 - ESP32 Eficiente (Otimizacao de Tipos e Memoria)
// Cultura Agricola: Milho (Zea mays) - Referencia: Embrapa Milho e Sorgo
//
// RESUMO DAS OTIMIZACOES APLICADAS EM RELACAO AO FIRMWARE DA FASE 2:
//
// 1. Pinos e Constantes de Hardware:
//    - Antes : #define sem tipo ou constantes inteiras implicitas (int = 32 bits).
//    - Depois: constexpr uint8_t (1 byte em tempo de compilacao, zero RAM alocada,
//      com verificacao de tipo pelo compilador C++).
//
// 2. Leitura do ADC no pino LDR (0 a 4095 - resolucao de 12 bits do ESP32):
//    - Antes : int valorLDR = analogRead(LDR_PIN);  -> 4 bytes (32 bits com sinal).
//    - Depois: uint16_t valorLDR = analogRead(LDR_PIN); -> 2 bytes sem sinal
//      (intervalo 0..65535 comporta com folga o ADC de 12 bits 0..4095, economizando
//      50% na variavel e evitando sinal desnecessario).
//
// 3. Calculo de Ponto Flutuante na FPU do ESP32 (Xtensa LX6 single-precision):
//    - Antes : float pH = (valorLDR / 4095.0) * 14.0;
//              Literais sem sufixo 'f' sao double (64 bits / 8 bytes). O ESP32 nao
//              possui FPU de 64 bits em hardware; operacoes double invocam rotinas
//              de emulacao em software (__divdf3, __muldf3), consumindo mais Flash
//              e mais stack.
//    - Depois: Uso de decimo de ponto fixo (uint8_t phDecimos = 0..140, representando
//              pH 0.0 a 14.0 com 1 casa decimal, que e exatamente a precisao impressa
//              no Serial.println(pH, 1) da Fase 2) e sufixo 'f' (float 32 bits) apenas
//              na leitura do sensor DHT22. Elimina completamente emulacao double (64-bit).
//
// 4. Empacotamento de Estados Booleanos em Bitmask (uint8_t):
//    - Antes : 7 variaveis bool separadas (previsaoChuva, nivelN_ok, nivelP_ok,
//              nivelK_ok, precisaIrrigar, umidadeSuficiente, precisaNutrientes) = 7 bytes.
//    - Depois: 1 unico registrador de flags uint8_t (1 byte) com mascaras de bits
//              para N, P, K, chuva e bomba, reduzindo 7 bytes para 1 byte (economia de 85,7%).
//
// 5. Strings Constantes em Flash (PROGMEM / F()) e Eliminacao de Duplicacoes:
//    - Antes : Strings repetidas ("[OK]", "[BAIXO]", linhas tracejadas) espalhadas
//              em multiplas chamadas Serial.println().
//    - Depois: Constantes centralizadas em Flash (constexpr const char*) e funcao
//              auxiliar unica para impressao do status de cada nutriente, reduzindo
//              o segmento .rodata e o tamanho do binario na Flash.
// ============================================================================

#include <Arduino.h>
#include <DHT.h>

// --- 1. PINOS E CONSTANTES TIPADAS (constexpr uint8_t: 1 byte, zero RAM) ---
constexpr uint8_t PINO_DHT        = 15U;
constexpr uint8_t TIPO_DHT        = DHT22;
constexpr uint8_t PINO_BOTAO_N    = 12U;
constexpr uint8_t PINO_BOTAO_P    = 14U;
constexpr uint8_t PINO_BOTAO_K    = 27U;
constexpr uint8_t PINO_LDR        = 34U;
constexpr uint8_t PINO_RELE_BOMBA = 2U;

// Limites agronomicos em ponto fixo (decimos: 400 = 40.0%, 600 = 60.0%, 60 = pH 6.0)
constexpr uint16_t UMIDADE_CRITICA_DEC = 400U;  // 40.0%
constexpr uint16_t UMIDADE_IDEAL_DEC   = 600U;  // 60.0%
constexpr uint8_t  PH_MIN_IDEAL_DEC    = 60U;   // pH 6.0
constexpr uint8_t  PH_MAX_IDEAL_DEC    = 70U;   // pH 7.0
constexpr uint16_t TEMPO_CICLO_MS      = 3000U; // 3000 ms cabe em uint16_t (0..65535)

// --- 2. MASCARAS DE BITS PARA EMPACOTAR ESTADOS EM 1 UNICO uint8_t ---
constexpr uint8_t FLAG_N_OK   = (1U << 0); // bit 0: Nitrogenio adequado
constexpr uint8_t FLAG_P_OK   = (1U << 1); // bit 1: Fosforo adequado
constexpr uint8_t FLAG_K_OK   = (1U << 2); // bit 2: Potassio adequado
constexpr uint8_t FLAG_TODOS_NPK = (FLAG_N_OK | FLAG_P_OK | FLAG_K_OK);
constexpr uint8_t FLAG_CHUVA  = (1U << 3); // bit 3: Previsao de chuva ativa

// Strings reutilizadas armazenadas uma unica vez em Flash (.rodata)
static constexpr const char STR_SEPARADOR[] PROGMEM = "------------------------------------------------";
static constexpr const char STR_OK[]        PROGMEM = "[OK]";
static constexpr const char STR_BAIXO[]     PROGMEM = "[BAIXO]";

// Instancia do sensor DHT
DHT dht(PINO_DHT, TIPO_DHT);

// Estado global compactado em 1 byte (substitui bool previsaoChuva global)
static uint8_t estadoGlobal = 0U;

// Imprime um valor em decimos (ex.: 63 -> "6.3") sem usar printf nem float
static void imprimirDecimos(uint16_t valorDecimos) {
  Serial.print(valorDecimos / 10U);
  Serial.write('.');
  Serial.print(valorDecimos % 10U);
}

void setup() {
  Serial.begin(115200UL);
  dht.begin();

  pinMode(PINO_BOTAO_N, INPUT_PULLUP);
  pinMode(PINO_BOTAO_P, INPUT_PULLUP);
  pinMode(PINO_BOTAO_K, INPUT_PULLUP);
  pinMode(PINO_LDR, INPUT);

  pinMode(PINO_RELE_BOMBA, OUTPUT);
  digitalWrite(PINO_RELE_BOMBA, LOW);

  Serial.println(F("Sistema FarmTech Iniciado..."));
  delay(2000U);
}

void loop() {
  // --- INTEGRACAO COM PYTHON VIA SERIAL ---
  if (Serial.available() > 0) {
    const uint8_t comando = static_cast<uint8_t>(Serial.read());
    if (comando == '1') {
      estadoGlobal |= FLAG_CHUVA;
      Serial.println(F("\n*** COMANDO RECEBIDO: Previsao de Chuva! Irrigacao Suspensa. ***\n"));
    } else if (comando == '0') {
      estadoGlobal &= static_cast<uint8_t>(~FLAG_CHUVA);
      Serial.println(F("\n*** COMANDO RECEBIDO: Clima Estavel. Sistema Liberado. ***\n"));
    }
  }

  // 1. Leitura de Umidade (float 32-bit exigido pela biblioteca DHT, convertido para decimos uint16_t)
  const float umidadeFloat = dht.readHumidity();
  if (isnan(umidadeFloat)) {
    Serial.println(F("Falha ao ler o sensor DHT22!"));
    delay(2000U);
    return;
  }
  const uint16_t umidadeDec = static_cast<uint16_t>(umidadeFloat * 10.0f + 0.5f);

  // 2. Leitura do LDR (0..4095 em uint16_t) e conversao inteira para pH em decimos (0..140)
  //    Evita completamente operacoes double de 64 bits: (valorLDR * 140 + 2047) / 4095
  const uint16_t valorLDR = static_cast<uint16_t>(analogRead(PINO_LDR));
  const uint8_t phDec = static_cast<uint8_t>((static_cast<uint32_t>(valorLDR) * 140UL + 2047UL) / 4095UL);

  // 3. Leitura dos botoes NPK empacotada nos bits 0, 1 e 2 de estadoGlobal
  estadoGlobal &= FLAG_CHUVA; // preserva apenas o bit de chuva e atualiza NPK
  if (!digitalRead(PINO_BOTAO_N)) estadoGlobal |= FLAG_N_OK;
  if (!digitalRead(PINO_BOTAO_P)) estadoGlobal |= FLAG_P_OK;
  if (!digitalRead(PINO_BOTAO_K)) estadoGlobal |= FLAG_K_OK;

  const bool precisaNutrientes = ((estadoGlobal & FLAG_TODOS_NPK) != FLAG_TODOS_NPK);

  // --- IMPRESSAO DE STATUS NO MONITOR SERIAL (mesmo layout da Fase 2) ---
  Serial.write('\n');
  Serial.println(STR_SEPARADOR);
  Serial.print(F("Umidade do Solo: "));
  imprimirDecimos(umidadeDec);
  Serial.println('%');

  Serial.print(F("Nivel de pH (LDR): "));
  imprimirDecimos(phDec);
  Serial.write('\n');

  Serial.print(F("Status NPK -> N: "));
  Serial.print((estadoGlobal & FLAG_N_OK) ? STR_OK : STR_BAIXO);
  Serial.print(F(" | P: "));
  Serial.print((estadoGlobal & FLAG_P_OK) ? STR_OK : STR_BAIXO);
  Serial.print(F(" | K: "));
  Serial.println((estadoGlobal & FLAG_K_OK) ? STR_OK : STR_BAIXO);

  Serial.print(F("Previsao de Chuva (Python): "));
  Serial.println((estadoGlobal & FLAG_CHUVA) ? F("SIM") : F("NAO"));

  // --- APLICACAO DAS REGRAS AGRONOMICAS (logica 100% preservada) ---
  if (phDec < PH_MIN_IDEAL_DEC || phDec > PH_MAX_IDEAL_DEC) {
    Serial.println(F("ALERTA: pH desbalanceado. Realize a correcao do solo."));
  }

  if (estadoGlobal & FLAG_CHUVA) {
    digitalWrite(PINO_RELE_BOMBA, LOW);
    Serial.println(F("ACAO: Bomba Bloqueada devido a previsao de chuva na API."));
  }
  else if (umidadeDec < UMIDADE_CRITICA_DEC) {
    digitalWrite(PINO_RELE_BOMBA, HIGH);
    if (precisaNutrientes) {
      Serial.println(F("ACAO: INICIANDO FERTIRRIGACAO (Injetando Agua + Nutrientes)."));
    } else {
      Serial.println(F("ACAO: INICIANDO IRRIGACAO COMUM (Apenas Agua)."));
    }
  }
  else if (umidadeDec >= UMIDADE_IDEAL_DEC) {
    digitalWrite(PINO_RELE_BOMBA, LOW);
    Serial.println(F("ACAO: Bomba Desligada. O solo possui umidade adequada."));
    if (precisaNutrientes) {
      Serial.println(F("AVISO: Nutrientes baixos. Aguarde o solo secar para fertirrigar."));
    }
  }
  else {
    if (digitalRead(PINO_RELE_BOMBA) == HIGH) {
      Serial.println(F("ACAO: Irrigacao em andamento."));
    } else {
      Serial.println(F("ACAO: Solo estavel. Bomba em repouso."));
    }
  }

  Serial.println(STR_SEPARADOR);
  delay(TEMPO_CICLO_MS);
}

