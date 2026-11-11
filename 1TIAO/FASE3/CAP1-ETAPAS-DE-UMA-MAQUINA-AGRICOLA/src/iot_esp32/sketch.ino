// ============================================================================
// Projeto: FarmTech Solutions - Sistema de Irrigacao Inteligente (Fase 3)
// Cultura Agricola: Milho (Zea mays) - Referencia: Embrapa Milho e Sorgo
//
// Evolucao do firmware da Fase 2 para EXPORTACAO DE HISTORICO:
// - A logica de irrigacao e IDENTICA a da Fase 2 (umidade < 40% liga a bomba,
//   umidade >= 60% desliga, entre 40% e 60% mantem o estado atual; previsao de
//   chuva recebida pela Serial bloqueia a bomba; nutriente baixo durante a
//   irrigacao caracteriza FERTIRRIGACAO; pH fora de 6.0 a 7.0 gera alerta).
// - NOVO: relogio simulado em que CADA CICLO DO LOOP VALE 1 HORA. Assim, alguns
//   minutos de simulacao no Wokwi geram meses de historico.
// - NOVO: cada ciclo imprime UMA linha CSV no Monitor Serial, pronta para ser
//   copiada para um arquivo e tratada em Python (Pandas/NumPy).
// - Linhas que NAO sao dados (mensagens e alertas) comecam com '#', para que o
//   script de exportacao consiga ignora-las.
//
// Formato da linha CSV:
// data_hora,umidade,ph,fosforo,potassio,nitrogenio,bomba,chuva,acao
//   fosforo/potassio/nitrogenio: 1 = nivel adequado (botao pressionado), 0 = baixo
//   bomba: 1 = ligada, 0 = desligada | chuva: 1 = previsao de chuva ativa
// ============================================================================

#include <DHT.h>

// Definicao dos pinos (mesma pinagem da Fase 2)
#define DHTPIN 15
#define DHTTYPE DHT22

#define BOTAO_N 12
#define BOTAO_P 14
#define BOTAO_K 27
#define LDR_PIN 34
#define RELE_BOMBA 2

// Intervalo real entre ciclos. Cada ciclo representa 1 hora simulada.
// 200 ms -> 5 horas simuladas por segundo -> ~3 meses em ~7,5 minutos.
#define INTERVALO_CICLO_MS 200

// Instancia do sensor DHT
DHT dht(DHTPIN, DHTTYPE);

// Variavel global para armazenar a previsao de chuva recebida via Serial
bool previsaoChuva = false;

// --- RELOGIO SIMULADO (inicio em 01/01/2026 00:00) ---
int anoSim = 2026;
int mesSim = 1;
int diaSim = 1;
int horaSim = 0;

// Retorna a quantidade de dias do mes (considera ano bissexto)
int diasNoMes(int mes, int ano) {
  if (mes == 2) {
    bool bissexto = (ano % 4 == 0 && ano % 100 != 0) || (ano % 400 == 0);
    return bissexto ? 29 : 28;
  }
  if (mes == 4 || mes == 6 || mes == 9 || mes == 11) {
    return 30;
  }
  return 31;
}

// Avanca o relogio simulado em 1 hora
void avancarRelogio() {
  horaSim++;
  if (horaSim > 23) {
    horaSim = 0;
    diaSim++;
    if (diaSim > diasNoMes(mesSim, anoSim)) {
      diaSim = 1;
      mesSim++;
      if (mesSim > 12) {
        mesSim = 1;
        anoSim++;
      }
    }
  }
}

// Imprime a data/hora simulada no formato AAAA-MM-DD HH:MM
void imprimirDataHora() {
  char buffer[17];
  snprintf(buffer, sizeof(buffer), "%04d-%02d-%02d %02d:00", anoSim, mesSim, diaSim, horaSim);
  Serial.print(buffer);
}

void setup() {
  Serial.begin(115200);

  // Inicializacao do sensor de umidade
  dht.begin();

  // Configuracao dos botoes NPK
  pinMode(BOTAO_N, INPUT_PULLUP);
  pinMode(BOTAO_P, INPUT_PULLUP);
  pinMode(BOTAO_K, INPUT_PULLUP);

  // Configuracao do LDR (pH)
  pinMode(LDR_PIN, INPUT);

  // Configuracao do Rele (Bomba)
  pinMode(RELE_BOMBA, OUTPUT);
  digitalWrite(RELE_BOMBA, LOW); // Comeca com a bomba desligada

  Serial.println("# Sistema FarmTech Iniciado (Fase 3 - exportacao CSV, 1 ciclo = 1 hora)");
  delay(2000);

  // Cabecalho do CSV (impresso uma unica vez)
  Serial.println("data_hora,umidade,ph,fosforo,potassio,nitrogenio,bomba,chuva,acao");
}

void loop() {
  // --- INTEGRACAO COM PYTHON VIA SERIAL (igual a Fase 2) ---
  if (Serial.available() > 0) {
    char comando = Serial.read();
    if (comando == '1') {
      previsaoChuva = true;
      Serial.println("# COMANDO RECEBIDO: Previsao de Chuva! Irrigacao Suspensa.");
    } else if (comando == '0') {
      previsaoChuva = false;
      Serial.println("# COMANDO RECEBIDO: Clima Estavel. Sistema Liberado.");
    }
  }

  // 1. Leitura de Umidade
  float umidade = dht.readHumidity();

  // 2. Leitura do LDR simulando pH (mapeamento de 0-4095 para 0-14)
  int valorLDR = analogRead(LDR_PIN);
  float pH = (valorLDR / 4095.0) * 14.0;

  // 3. Leitura dos Botoes NPK (pressionado = nivel adequado)
  bool nivelN_ok = !digitalRead(BOTAO_N);
  bool nivelP_ok = !digitalRead(BOTAO_P);
  bool nivelK_ok = !digitalRead(BOTAO_K);

  const char* acao;

  // Tratamento de falha na leitura do DHT: na Fase 2 o ciclo era abortado sem
  // mexer na bomba. Aqui a bomba tambem nao e alterada, mas a hora e registrada
  // com umidade "nan" para que o tratamento em Python identifique o valor ausente.
  if (isnan(umidade)) {
    acao = "FALHA_SENSOR";
  } else {
    // 4. Variaveis de tomada de decisao
    bool precisaIrrigar = (umidade < 40.0);
    bool umidadeSuficiente = (umidade >= 60.0);
    bool precisaNutrientes = (!nivelN_ok || !nivelP_ok || !nivelK_ok);

    // --- APLICACAO DAS REGRAS AGRONOMICAS (identicas a Fase 2) ---
    if (pH < 6.0 || pH > 7.0) {
      Serial.println("# ALERTA: pH desbalanceado. Realize a correcao do solo.");
    }

    if (previsaoChuva) {
      digitalWrite(RELE_BOMBA, LOW); // Bloqueia a bomba
      acao = "BLOQUEIO_CHUVA";
    }
    else if (precisaIrrigar) {
      digitalWrite(RELE_BOMBA, HIGH); // Liga a bomba
      acao = precisaNutrientes ? "FERTIRRIGACAO" : "IRRIGACAO";
    }
    else if (umidadeSuficiente) {
      digitalWrite(RELE_BOMBA, LOW); // Desliga a bomba
      acao = precisaNutrientes ? "DESLIGADA_NUTRIENTE_BAIXO" : "DESLIGADA";
    }
    else {
      bool estadoBomba = digitalRead(RELE_BOMBA);
      acao = (estadoBomba == HIGH) ? "IRRIGACAO_EM_ANDAMENTO" : "REPOUSO";
    }
  }

  // --- LINHA CSV DO CICLO ---
  imprimirDataHora();
  Serial.print(",");
  if (isnan(umidade)) {
    Serial.print("nan");
  } else {
    Serial.print(umidade, 1);
  }
  Serial.print(",");
  Serial.print(pH, 2);
  Serial.print(",");
  Serial.print(nivelP_ok ? 1 : 0);
  Serial.print(",");
  Serial.print(nivelK_ok ? 1 : 0);
  Serial.print(",");
  Serial.print(nivelN_ok ? 1 : 0);
  Serial.print(",");
  Serial.print(digitalRead(RELE_BOMBA) == HIGH ? 1 : 0);
  Serial.print(",");
  Serial.print(previsaoChuva ? 1 : 0);
  Serial.print(",");
  Serial.println(acao);

  // Avanca 1 hora no relogio simulado e aguarda o proximo ciclo
  avancarRelogio();
  delay(INTERVALO_CICLO_MS);
}

