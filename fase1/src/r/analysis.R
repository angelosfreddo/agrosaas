#!/usr/bin/env Rscript
# ==============================================================================
# FarmTech Solutions - Analise Estatistica Agricola em R
# Projeto FIAP - Fase 1
# ==============================================================================

cat("==============================================================\n")
cat("      FARMTECH SOLUTIONS - ANALISE ESTATISTICA (R)\n")
cat("==============================================================\n\n")

# Caminho para o arquivo CSV exportado pela aplicacao Python
caminho_csv <- file.path("data", "dados_fazenda.csv")

if (!file.exists(caminho_csv)) {
  stop("[ERRO] Arquivo 'data/dados_fazenda.csv' nao encontrado. Execute o script Python primeiro!")
}

# Leitura do dataset
dados <- read.csv(caminho_csv, stringsAsFactors = FALSE)

cat("[INFO] Dataset Carregado com Sucesso! (Total de Registros:", nrow(dados), ")\n")
print(dados)
cat("\n--------------------------------------------------------------\n")

# ==============================================================================
# ESTATISTICA DESCRITIVA GERAL
# ==============================================================================
cat("\n1. ESTATISTICAS GERAIS DA AREA DE PLANTIO (em Hectares - ha)\n")
cat("--------------------------------------------------------------\n")
media_area <- mean(dados$area_ha)
desvio_area <- sd(dados$area_ha)
min_area <- min(dados$area_ha)
max_area <- max(dados$area_ha)
mediana_area <- median(dados$area_ha)

cat(sprintf("- Media de Area:        %.4f ha\n", media_area))
cat(sprintf("- Desvio Padrao:        %.4f ha\n", desvio_area))
cat(sprintf("- Mediana:              %.4f ha\n", mediana_area))
cat(sprintf("- Area Minima:          %.4f ha\n", min_area))
cat(sprintf("- Area Maxima:          %.4f ha\n", max_area))

# ==============================================================================
# ESTATISTICA AGRUPADA POR CULTURA (CAFE VS MILHO)
# ==============================================================================
cat("\n2. ANALISE COMPARATIVA POR CULTURA\n")
cat("--------------------------------------------------------------\n")

culturas <- unique(dados$cultura)

for (c in culturas) {
  sub_dados <- dados[dados$cultura == c, ]
  
  cat(sprintf("\nCultura: %s (Total de Terrenos: %d)\n", c, nrow(sub_dados)))
  cat(sprintf("   - Area Media:         %.4f ha\n", mean(sub_dados$area_ha)))
  cat(sprintf("   - Desvio Padrao Area: %.4f ha\n", ifelse(nrow(sub_dados) > 1, sd(sub_dados$area_ha), 0)))
  cat(sprintf("   - Total de Insumo:    %.2f %s\n", sum(sub_dados$qtd_insumo), sub_dados$unidade[1]))
  cat(sprintf("   - Media de Insumo:    %.2f %s/propriedade\n", mean(sub_dados$qtd_insumo), sub_dados$unidade[1]))
}

cat("\n==============================================================\n")
cat("  ANALISE CONCLUIDA COM SUCESSO!\n")
cat("==============================================================\n")
