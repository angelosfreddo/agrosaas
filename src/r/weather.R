# ==============================================================================
# FarmTech Solutions - Integração com API Meteorológica (R - Ir Além)
# Projeto FIAP - Fase 1
# ==============================================================================

cat("==============================================================\n")
cat("    FARMTECH SOLUTIONS - MONITORAMENTO METEOROLÓGICO (R)\n")
cat("==============================================================\n\n")

# Coordenadas da Região de São Carlos / SP (Polo Tecnológico da Embrapa Instrumentação)
latitude  <- -22.0174
longitude <- -47.8860
cidade    <- "São Carlos - SP (Região da Fazenda FarmTech)"

cat(sprintf("📡 Conectando à API Meteorológica Pública (Open-Meteo)...\n"))
cat(sprintf("📍 Localização: %s\n", cidade))
cat(sprintf("   Coordenadas: Lat %.4f, Lon %.4f\n\n", latitude, longitude))

api_url <- sprintf(
  "https://api.open-meteo.com/v1/forecast?latitude=%.4f&longitude=%.4f&current_weather=true",
  latitude, longitude
)

# Função para traduzir o código de tempo WMO da API
mapear_condicao_tempo <- function(code) {
  switch(as.character(code),
         "0" = "Céu Limpo ☀️",
         "1" = "Predominantemente Limpo 🌤️",
         "2" = "Parcialmente Nublado ⛅",
         "3" = "Nublado ☁️",
         "45" = "Névoa / Encoberto 🌫️",
         "48" = "Névoa Deposicional 🌫️",
         "51" = "Garoa Leve 🌦️",
         "53" = "Garoa Moderada 🌦️",
         "55" = "Garoa Densa 🌧️",
         "61" = "Chuva Leve 🌧️",
         "63" = "Chuva Moderada 🌧️",
         "65" = "Chuva Forte 🌧️",
         "80" = "Pancadas de Chuva Leves 🌦️",
         "81" = "Pancadas de Chuva Moderadas 🌧️",
         "82" = "Pancadas de Chuva Violentas ⛈️",
         "95" = "Tempestade ⚡",
         "Condição Meteorológica Normal 🍃"
  )
}

tryCatch({
  if (require("jsonlite", quietly = TRUE)) {
    dados_clima <- jsonlite::fromJSON(api_url)
    cw <- dados_clima$current_weather
    
    temp <- cw$temperature
    vento_vel <- cw$windspeed
    vento_dir <- cw$winddirection
    weather_code <- cw$weathercode
    horario <- cw$time
    
    condicao_txt <- mapear_condicao_tempo(weather_code)
    
    cat("==============================================================\n")
    cat("           RELATÓRIO CLIMÁTICO EM TEMPO REAL                 \n")
    cat("==============================================================\n")
    cat(sprintf("⏰ Data / Horário UTC:    %s\n", horario))
    cat(sprintf("🌡️ Temperatura Atual:     %.1f °C\n", temp))
    cat(sprintf("🌤️ Condição do Tempo:     %s (Código WMO: %d)\n", condicao_txt, weather_code))
    cat(sprintf("💨 Velocidade do Vento:   %.1f km/h\n", vento_vel))
    cat(sprintf("🧭 Direção do Vento:      %d°\n", vento_dir))
    cat("==============================================================\n")
    
    # Recomendação Agrícola com base na temperatura e vento
    cat("\n🚜 RECOMENDAÇÃO AGRONÔMICA PARA PULVERIZAÇÃO:\n")
    if (vento_vel > 10.0) {
      cat("⚠️ ATENÇÃO: Vento acima de 10 km/h. Risco de deriva na pulverização defensiva!\n")
    } else {
      cat("✅ Condição favorável para pulverização e manejo no campo.\n")
    }
    
  } else {
    # Fallback usando leitor de URL nativo caso jsonlite não estivesse disponível
    con <- url(api_url)
    raw_text <- readLines(con, warn = FALSE)
    close(con)
    cat("📄 Resposta Bruta da API Meteorológica:\n")
    cat(raw_text, "\n")
  }
}, error = function(e) {
  cat("❌ Erro ao conectar ou processar os dados da API Meteorológica:\n")
  cat(e$message, "\n")
})
