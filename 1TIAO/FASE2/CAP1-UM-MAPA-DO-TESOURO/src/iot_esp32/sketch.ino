#include <DHT.h>

// Definicao dos pinos
#define DHTPIN 15
#define DHTTYPE DHT22

#define BOTAO_N 12
#define BOTAO_P 14
#define BOTAO_K 27
#define LDR_PIN 34
#define RELE_BOMBA 2

// Instancia do sensor DHT
DHT dht(DHTPIN, DHTTYPE);

// Variavel global para armazenar a previsao de chuva recebida via Serial
bool previsaoChuva = false;

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
  
  Serial.println("Sistema FarmTech Iniciado...");
  delay(2000);
}

void loop() {
  // --- INTEGRAÇÃO COM PYTHON VIA SERIAL ---
  // Verifica se o usuario digitou algo no Monitor Serial
  if (Serial.available() > 0) {
    char comando = Serial.read();
    if (comando == '1') {
      previsaoChuva = true;
      Serial.println("\n*** COMANDO RECEBIDO: Previsao de Chuva! Irrigacao Suspensa. ***\n");
    } else if (comando == '0') {
      previsaoChuva = false;
      Serial.println("\n*** COMANDO RECEBIDO: Clima Estavel. Sistema Liberado. ***\n");
    }
  }

  // 1. Leitura de Umidade
  float umidade = dht.readHumidity();
  
  // Tratamento de falha na leitura do DHT
  if (isnan(umidade)) {
    Serial.println("Falha ao ler o sensor DHT22!");
    delay(2000);
    return;
  }
  
  // 2. Leitura do LDR simulando pH (mapeamento de 0-4095 para 0-14)
  int valorLDR = analogRead(LDR_PIN);
  float pH = (valorLDR / 4095.0) * 14.0;
  
  // 3. Leitura dos Botoes NPK
  bool nivelN_ok = !digitalRead(BOTAO_N);
  bool nivelP_ok = !digitalRead(BOTAO_P);
  bool nivelK_ok = !digitalRead(BOTAO_K);
  
  // 4. Variaveis de tomada de decisao
  bool precisaIrrigar = (umidade < 40.0);
  bool umidadeSuficiente = (umidade >= 60.0);
  bool precisaNutrientes = (!nivelN_ok || !nivelP_ok || !nivelK_ok);
  
  // --- IMPRESSAO DE STATUS NO MONITOR SERIAL ---
  Serial.println("\n------------------------------------------------");
  Serial.print("Umidade do Solo: "); 
  Serial.print(umidade); 
  Serial.println("%");
  
  Serial.print("Nivel de pH (LDR): "); 
  Serial.println(pH, 1);
  
  Serial.print("Status NPK -> N: "); 
  Serial.print(nivelN_ok ? "[OK]" : "[BAIXO]");
  Serial.print(" | P: "); 
  Serial.print(nivelP_ok ? "[OK]" : "[BAIXO]");
  Serial.print(" | K: "); 
  Serial.println(nivelK_ok ? "[OK]" : "[BAIXO]");
  
  Serial.print("Previsao de Chuva (Python): ");
  Serial.println(previsaoChuva ? "SIM" : "NAO");
  
  // --- APLICACAO DAS REGRAS AGRONOMICAS ---
  
  // Regra de pH: Alertar se fora do ideal (6.0 a 7.0)
  if (pH < 6.0 || pH > 7.0) {
    Serial.println("ALERTA: pH desbalanceado. Realize a correcao do solo.");
  }
  
  // Regra da Irrigacao e Integracao com Python
  if (previsaoChuva) {
    digitalWrite(RELE_BOMBA, LOW); // Bloqueia a bomba
    Serial.println("ACAO: Bomba Bloqueada devido a previsao de chuva na API.");
  }
  else if (precisaIrrigar) {
    digitalWrite(RELE_BOMBA, HIGH); // Liga a bomba
    
    if (precisaNutrientes) {
      Serial.println("ACAO: INICIANDO FERTIRRIGACAO (Injetando Agua + Nutrientes).");
    } else {
      Serial.println("ACAO: INICIANDO IRRIGACAO COMUM (Apenas Agua).");
    }
  } 
  else if (umidadeSuficiente) {
    digitalWrite(RELE_BOMBA, LOW); // Desliga a bomba
    Serial.println("ACAO: Bomba Desligada. O solo possui umidade adequada.");
    
    if (precisaNutrientes) {
      Serial.println("AVISO: Nutrientes baixos. Aguarde o solo secar para fertirrigar.");
    }
  } 
  else {
    bool estadoBomba = digitalRead(RELE_BOMBA);
    if (estadoBomba == HIGH) {
      Serial.println("ACAO: Irrigacao em andamento.");
    } else {
      Serial.println("ACAO: Solo estavel. Bomba em repouso.");
    }
  }
  
  Serial.println("------------------------------------------------");
  
  // Aguarda 3 segundos antes da proxima leitura
  delay(3000);
}
