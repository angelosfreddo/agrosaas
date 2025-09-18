# clima.R
library(httr)
library(jsonlite)

# ---- API pública Open-Meteo ----
# Exemplo: São Paulo (-23.55, -46.63)
url <- "https://api.open-meteo.com/v1/forecast?latitude=-23.55&longitude=-46.63&current_weather=true"

resposta <- GET(url)

if (status_code(resposta) == 200) {
  clima <- fromJSON(content(resposta, "text"))
  cat("🌦 Dados meteorológicos:\n")
  print(clima$current_weather)
} else {
  cat("❌ Erro ao acessar API meteorológica\n")
}
