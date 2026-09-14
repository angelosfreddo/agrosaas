# ==============================================================================
# FarmTech Solutions - Integracao com API Meteorologica (R - Ir Alem)
# Projeto FIAP - Fase 1
# ==============================================================================

cat("==============================================================\n")
cat("    FARMTECH SOLUTIONS - MONITORAMENTO METEOROLOGICO (R)\n")
cat("==============================================================\n\n")

# Coordenadas da Regiao de Sao Carlos / SP (Polo Tecnologico da Embrapa Instrumentacao)
latitude  <- -22.0174
longitude <- -47.8860
cidade    <- "Sao Carlos - SP (Regiao da Fazenda FarmTech)"

cat(sprintf("[CONEXAO] Conectando a API Meteorologica Publica (Open-Meteo)...\n"))
cat(sprintf("Localizacao: %s\n", cidade))
cat(sprintf("Coordenadas: Lat %.4f, Lon %.4f\n\n", latitude, longitude))

api_url <- sprintf(
  "https://api.open-meteo.com/v1/forecast?latitude=%.4f&longitude=%.4f&current_weather=true",
  latitude, longitude
)

# Funcao para traduzir o codigo de tempo WMO da API
mapear_condicao_tempo <- function(code) {
  switch(as.character(code),
         "0" = "Ceu Limpo",
         "1" = "Predominantemente Limpo",
         "2" = "Parcialmente Nublado",
         "3" = "Nublado",
         "45" = "Nevoa / Encoberto",
         "48" = "Nevoa Deposicional",
         "51" = "Garoa Leve",
         "53" = "Garoa Moderada",
         "55" = "Garoa Densa",
         "61" = "Chuva Leve",
         "63" = "Chuva Moderada",
         "65" = "Chuva Forte",
         "80" = "Pancadas de Chuva Leves",
         "81" = "Pancadas de Chuva Moderadas",
         "82" = "Pancadas de Chuva Violentas",
         "95" = "Tempestade",
         "Condicao Meteorologica Normal"
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
    cat("           RELATORIO CLIMATICO EM TEMPO REAL                 \n")
    cat("==============================================================\n")
    cat(sprintf("Data / Horario UTC:    %s\n", horario))
    cat(sprintf("Temperatura Atual:     %.1f °C\n", temp))
    cat(sprintf("Condicao do Tempo:     %s (Codigo WMO: %d)\n", condicao_txt, weather_code))
    cat(sprintf("Velocidade do Vento:   %.1f km/h\n", vento_vel))
    cat(sprintf("Direcao do Vento:      %d°\n", vento_dir))
    cat("==============================================================\n")
    
    # Recomendacao Agricola com base na temperatura e vento
    cat("\nRECOMENDACAO AGRONOMICA PARA PULVERIZACAO:\n")
    if (vento_vel > 10.0) {
      cat("[AVISO] ATENCAO: Vento acima de 10 km/h. Risco de deriva na pulverizacao defensiva!\n")
    } else {
      cat("[INFO] Condicao favoravel para pulverizacao e manejo no campo.\n")
    }
    
  } else {
    con <- url(api_url)
    raw_text <- readLines(con, warn = FALSE)
    close(con)
    cat("Resposta Bruta da API Meteorologica:\n")
    cat(raw_text, "\n")
  }
}, error = function(e) {
  cat("[ERRO] Erro ao conectar ou processar os dados da API Meteorologica:\n")
  cat(e$message, "\n")
})
