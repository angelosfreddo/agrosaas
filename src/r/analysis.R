# ==============================================================================
# FarmTech Solutions - Análise Estatística Agrícola em R
# Projeto FIAP - Fase 1
# ==============================================================================

cat("==============================================================\n")
cat("      FARMTECH SOLUTIONS - ANÁLISE ESTATÍSTICA (R)\n")
cat("==============================================================\n\n")

# Caminho para o arquivo CSV exportado pela aplicação Python
caminho_csv <- file.path("data", "dados_fazenda.csv")

if (!file.exists(caminho_csv)) {
  stop("❌ Arquivo 'data/dados_fazenda.csv' não encontrado. Execute o script Python primeiro!")
}

# Leitura do dataset
dados <- read.csv(caminho_csv, stringsAsFactors = FALSE)

cat("📊 Dataset Carregado com Sucesso! (Total de Registros:", nrow(dados), ")\n")
print(dados)
cat("\n--------------------------------------------------------------\n")

# ==============================================================================
# ESTATÍSTICA DESCRITIVA GERAL
# ==============================================================================
cat("\n📈 1. ESTATÍSTICAS GERAIS DA ÁREA DE PLANTIO (em Hectares - ha)\n")
cat("--------------------------------------------------------------\n")
media_area <- mean(dados$area_ha)
desvio_area <- sd(dados$area_ha)
min_area <- min(dados$area_ha)
max_area <- max(dados$area_ha)
mediana_area <- median(dados$area_ha)

cat(sprintf("• Média de Área:        %.4f ha\n", media_area))
cat(sprintf("• Desvio Padrão:        %.4f ha\n", desvio_area))
cat(sprintf("• Mediana:              %.4f ha\n", mediana_area))
cat(sprintf("• Área Mínima:          %.4f ha\n", min_area))
cat(sprintf("• Área Máxima:          %.4f ha\n", max_area))

# ==============================================================================
# ESTATÍSTICA AGRUPADA POR CULTURA (CAFÉ VS MILHO)
# ==============================================================================
cat("\n🌱 2. ANÁLISE COMPARATIVA POR CULTURA\n")
cat("--------------------------------------------------------------\n")

culturas <- unique(dados$cultura)

for (c in culturas) {
  sub_dados <- dados[dados$cultura == c, ]
  
  cat(sprintf("\n🔸 Cultura: %s (Total de Terrenos: %d)\n", c, nrow(sub_dados)))
  cat(sprintf("   - Área Média:         %.4f ha\n", mean(sub_dados$area_ha)))
  cat(sprintf("   - Desvio Padrão Área: %.4f ha\n", ifelse(nrow(sub_dados) > 1, sd(sub_dados$area_ha), 0)))
  cat(sprintf("   - Total de Insumo:    %.2f %s\n", sum(sub_dados$qtd_insumo), sub_dados$unidade[1]))
  cat(sprintf("   - Média de Insumo:    %.2f %s/propriedade\n", mean(sub_dados$qtd_insumo), sub_dados$unidade[1]))
}

cat("\n==============================================================\n")
cat("  ANÁLISE CONCLUÍDA COM SUCESSO!\n")
cat("==============================================================\n")
