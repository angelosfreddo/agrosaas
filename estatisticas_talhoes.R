

# ler CSV (ajuste o caminho se necessário)
df <- read.csv("talhoes.csv", stringsAsFactors = FALSE)

# garante que campos numéricos estejam numéricos
num_cols <- c("comprimento","largura","base_maior","base_menor","altura","taxa_ml_por_m","numero_linhas")
for (nc in num_cols) {
  if (nc %in% names(df)) {
    df[[nc]] <- as.numeric(df[[nc]])
  }
}

# calcular área linha a linha
area <- numeric(nrow(df))
for (i in seq_len(nrow(df))) {
  tipo <- tolower(df$tipo_area[i])
  if (tipo == "retangulo") {
    area[i] <- df$comprimento[i] * df$largura[i]
  } else if (tipo == "trapezio") {
    area[i] <- (df$base_maior[i] + df$base_menor[i]) * df$altura[i] / 2
  } else {
    area[i] <- NA
  }
}

# estatísticas básicas da área
media_area <- mean(area, na.rm = TRUE)
sd_area <- sd(area, na.rm = TRUE)
cat("N talhões:", nrow(df), "\n")
cat("Média da área (m2):", round(media_area,2), "\n")
cat("Desvio padrão da área (m2):", round(sd_area,2), "\n")

# calcular insumo ml por talhão e total
insumo_ml <- numeric(nrow(df))
for (i in seq_len(nrow(df))) {
  taxa <- df$taxa_ml_por_m[i]
  nlinhas <- df$numero_linhas[i]
  comp <- df$comprimento[i]
  insumo_ml[i] <- taxa * nlinhas * comp
}
cat("Média de insumo (mL):", round(mean(insumo_ml, na.rm=TRUE),2), "\n")
cat("Total de insumo (L):", round(sum(insumo_ml, na.rm=TRUE)/1000,2), "\n")
