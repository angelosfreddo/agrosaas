# Script R para Analise Estatistica e Tomada de Decisao
# FarmTech Solutions - Fase 2
# Objetivo: Analisar dados historicos para recomendar a irrigacao

print("==========================================")
print("   Sistema Analitico FarmTech (R Script)  ")
print("==========================================")
print("Iniciando analise de dados historicos do solo...")

# Gerando dados simulados dos ultimos 10 dias de uma plantacao
dias <- 1:10
umidade_solo <- c(65.2, 60.1, 55.4, 48.9, 45.0, 41.2, 38.5, 35.1, 33.0, 31.5)
temperatura <- c(22.1, 23.5, 24.0, 25.5, 26.1, 27.0, 28.5, 29.0, 30.2, 31.0)

dados <- data.frame(Dia = dias, Umidade = umidade_solo, Temperatura = temperatura)

# Estatistica Descritiva Basica (Exigencia do Curso)
media_umidade <- mean(dados$Umidade)
sd_umidade <- sd(dados$Umidade)
min_umidade <- min(dados$Umidade)
max_umidade <- max(dados$Umidade)

print("--- Resumo Estatistico da Umidade (Ultimos 10 dias) ---")
cat("Media de Umidade:", round(media_umidade, 2), "%\n")
cat("Desvio Padrao:", round(sd_umidade, 2), "%\n")
cat("Umidade Minima:", min_umidade, "%\n")
cat("Umidade Maxima:", max_umidade, "%\n")

# Logica de Decisao (Data Science) baseada em media movel dos ultimos 3 dias
ultimos_3_dias <- tail(dados$Umidade, 3)
media_recente <- mean(ultimos_3_dias)

cat("\n--- Analise de Tendencia (Data Science) ---\n")
cat("Media de umidade dos ultimos 3 dias:", round(media_recente, 2), "%\n")

# Tomada de decisao integrada a regra de negocio (40%)
if (media_recente < 40) {
  print(">>> [DECISAO IA/R]: Recomendacao para LIGAR a bomba (Rele Azul). <<<")
  print("Motivo: A umidade media recente indica solo secando abaixo do nivel critico (40%).")
} else {
  print(">>> [DECISAO IA/R]: Recomendacao para MANTER DESLIGADA a bomba. <<<")
  print("Motivo: O solo ainda possui reserva de agua suficiente.")
}
print("==========================================")
