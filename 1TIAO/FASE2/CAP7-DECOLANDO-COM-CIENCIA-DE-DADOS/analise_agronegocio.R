# AngeloGuilhermeSfreddo_RM566580_fase2_cap7

# ==============================================================================
# FIAP - FASE 2: DECOLANDO COM CIÊNCIA DE DADOS
# ATIVIDADE AVALIATIVA: ANÁLISE ESTATÍSTICA DE DADOS DO AGRO
# ------------------------------------------------------------------------------
# Contexto: Análise exploratória descritiva com dados do agronegócio brasileiro,
# baseados em levantamentos públicos de órgãos como CONAB, IBGE e MAPA.
# ==============================================================================


# ------------------------------------------------------------------------------
# 1. CARREGAMENTO DOS DADOS E PREPARAÇÃO DO AMBIENTE
# ------------------------------------------------------------------------------

# Para ler o arquivo Excel (.xlsx), utilizamos o pacote 'readxl'
# Caso o pacote ainda não esteja instalado no seu R/RStudio, instale-o executando:
# install.packages("readxl")

if (requireNamespace("readxl", quietly = TRUE)) {
  library(readxl)
  dados <- read_excel("base_dados_agronegocio.xlsx")
  cat(">> Dados carregados com sucesso a partir de 'base_dados_agronegocio.xlsx'\n")
} else {
  # Fallback: Caso 'readxl' não esteja instalado, carregamos via CSV
  dados <- read.csv("base_dados_agronegocio.csv", stringsAsFactors = FALSE, encoding = "UTF-8")
  cat(">> Pacote 'readxl' não encontrado. Dados carregados a partir de 'base_dados_agronegocio.csv'\n")
}

# Visualização da estrutura da base de dados
cat("\n======================================================\n")
cat("ESTRUTURA GERAL DA BASE DE DADOS\n")
cat("======================================================\n")
str(dados)

cat("\nPrimeiras 6 observações:\n")
print(head(dados))

cat(sprintf("\nTotal de Linhas: %d | Total de Colunas: %d\n", nrow(dados), ncol(dados)))

# ------------------------------------------------------------------------------
# CLASSIFICAÇÃO DAS VARIÁVEIS NA BASE (Atendimento ao Requisito 2):
# 1. Quantitativa Discreta:  numero_maquinas (contagem inteira de maquinários)
# 2. Quantitativa Contínua:  produtividade_sc_ha (sacas de 60 kg por hectare)
# 3. Qualitativa Nominal:    regiao (Centro-Oeste, Sul, Sudeste, Nordeste, Norte)
# 4. Qualitativa Ordinal:    porte_propriedade (Pequeno < Médio < Grande)
# ------------------------------------------------------------------------------


# ==============================================================================
# 2. ITEM 3: ANÁLISE EXPLORATÓRIA DE UMA VARIÁVEL QUANTITATIVA
# Variável escolhida: produtividade_sc_ha (Produtividade em sacas/ha)
# ==============================================================================

var_quant <- dados$produtividade_sc_ha

cat("\n======================================================\n")
cat("ITEM 3: ANÁLISE EXPLORATÓRIA - PRODUTIVIDADE AGRÍCOLA (sc/ha)\n")
cat("======================================================\n")

# --- A) MEDIDAS DE TENDÊNCIA CENTRAL ---
media_prod    <- mean(var_quant)
mediana_prod  <- median(var_quant)

# Função personalizada para cálculo da Moda Estatística (amostral)
calcular_moda <- function(v) {
  uniqv <- unique(v)
  uniqv[which.max(tabulate(match(v, uniqv)))]
}
moda_prod <- calcular_moda(var_quant)

cat("\n[1] MEDIDAS DE TENDÊNCIA CENTRAL:\n")
cat(sprintf("  • Média Aritmética : %.2f sc/ha\n", media_prod))
cat(sprintf("  • Mediana          : %.2f sc/ha\n", mediana_prod))
cat(sprintf("  • Moda             : %.2f sc/ha\n", moda_prod))

# --- B) MEDIDAS DE DISPERSÃO ---
variancia_prod     <- var(var_quant)
desvio_padrao_prod <- sd(var_quant)
amplitude_prod     <- max(var_quant) - min(var_quant)
cv_prod            <- (desvio_padrao_prod / media_prod) * 100

cat("\n[2] MEDIDAS DE DISPERSÃO:\n")
cat(sprintf("  • Variância Amostral      : %.2f (sc/ha)²\n", variancia_prod))
cat(sprintf("  • Desvio Padrão (s)       : %.2f sc/ha\n", desvio_padrao_prod))
cat(sprintf("  • Amplitude Total (A)     : %.2f sc/ha (Min: %.2f, Max: %.2f)\n", 
            amplitude_prod, min(var_quant), max(var_quant)))
cat(sprintf("  • Coeficiente de Variação : %.2f%%\n", cv_prod))

# Avaliação do Coeficiente de Variação (Critério estatístico de Garcia, 1989):
if (cv_prod < 15) {
  cat("  -> Interpretação do CV: Baixa dispersão (conjunto homogêneo, dados bem concentrados em torno da média).\n")
} else if (cv_prod <= 30) {
  cat("  -> Interpretação do CV: Média dispersão (moderada variabilidade em torno da média).\n")
} else {
  cat("  -> Interpretação do CV: Alta dispersão (conjunto heterogêneo).\n")
}

# --- C) MEDIDAS SEPARATRIZES ---
minimo_prod <- min(var_quant)
q1_prod     <- as.numeric(quantile(var_quant, probs = 0.25))
q2_prod     <- as.numeric(quantile(var_quant, probs = 0.50)) # Mediana
q3_prod     <- as.numeric(quantile(var_quant, probs = 0.75))
maximo_prod <- max(var_quant)
iqr_prod    <- IQR(var_quant) # Intervalo Interquartil: Q3 - Q1
p10_prod    <- as.numeric(quantile(var_quant, probs = 0.10))
p90_prod    <- as.numeric(quantile(var_quant, probs = 0.90))

cat("\n[3] MEDIDAS SEPARATRIZES:\n")
cat(sprintf("  • Mínimo                     : %.2f sc/ha\n", minimo_prod))
cat(sprintf("  • 1º Quartil (Q1 - 25%%)      : %.2f sc/ha\n", q1_prod))
cat(sprintf("  • 2º Quartil (Q2/Mediana 50%%): %.2f sc/ha\n", q2_prod))
cat(sprintf("  • 3º Quartil (Q3 - 75%%)      : %.2f sc/ha\n", q3_prod))
cat(sprintf("  • Máximo                     : %.2f sc/ha\n", maximo_prod))
cat(sprintf("  • Intervalo Interquartil(IQR): %.2f sc/ha\n", iqr_prod))
cat(sprintf("  • 10º Percentil (P10)        : %.2f sc/ha\n", p10_prod))
cat(sprintf("  • 90º Percentil (P90)        : %.2f sc/ha\n", p90_prod))

# --- D) ANÁLISE GRÁFICA DA VARIÁVEL QUANTITATIVA ---

# Configuração e salvamento da imagem comparativa (Histograma + Boxplot)
png("grafico_1_quantitativa_produtividade.png", width = 1300, height = 650, res = 130)
par(mfrow = c(1, 2), mar = c(5, 5, 4, 3))

# 1. Histograma com linhas de Média e Mediana
hist(var_quant,
     breaks = 7,
     col = "#85C1E9",
     border = "#1B4F72",
     main = "Distribuição da Produtividade Agrícola",
     xlab = "Produtividade (sacas de 60kg / ha)",
     ylab = "Frequência Absoluta (Polos Produtores)",
     ylim = c(0, 13),
     las = 1)
abline(v = media_prod, col = "#C0392B", lwd = 2.5, lty = 2)
abline(v = mediana_prod, col = "#1E8449", lwd = 2.5, lty = 3)
legend("topleft", 
       legend = c(sprintf("Média: %.2f", media_prod), sprintf("Mediana: %.2f", mediana_prod)),
       col = c("#C0392B", "#1E8449"), 
       lty = c(2, 3), 
       lwd = 2.5, 
       bty = "o",
       bg = "white",
       cex = 0.9)

# 2. Boxplot (Diagrama de Caixa) com anotações claras
bx <- boxplot(var_quant,
              col = "#A9DFBF",
              border = "#1E8449",
              main = "Boxplot: Produtividade Agrícola",
              ylab = "Produtividade (sacas / ha)",
              las = 1,
              ylim = c(40, 75))
# Ponto da Média (losango vermelho)
points(x = 1, y = media_prod, col = "#C0392B", pch = 18, cex = 2)

# Rótulos posicionados sem sobreposição
text(x = 0.65, y = media_prod, labels = sprintf("Média: %.1f", media_prod), col = "#C0392B", font = 2, cex = 0.85)
text(x = 1.35, y = q3_prod, labels = sprintf("Q3: %.1f", q3_prod), col = "#1E8449", font = 2, cex = 0.85)
text(x = 1.35, y = q2_prod, labels = sprintf("Mediana: %.1f", q2_prod), col = "#1E8449", font = 2, cex = 0.85)
text(x = 1.35, y = q1_prod, labels = sprintf("Q1: %.1f", q1_prod), col = "#1E8449", font = 2, cex = 0.85)
text(x = 1.35, y = maximo_prod, labels = sprintf("Máx: %.1f", maximo_prod), col = "#5D6D7E", cex = 0.8)
text(x = 1.35, y = minimo_prod, labels = sprintf("Mín: %.1f", minimo_prod), col = "#5D6D7E", cex = 0.8)

dev.off()
cat("\n>> Gráfico salvo com sucesso: 'grafico_1_quantitativa_produtividade.png'\n")


# ==============================================================================
# 3. ITEM 4: ANÁLISE GRÁFICA DE UMA VARIÁVEL QUALITATIVA
# Variável escolhida: regiao (Qualitativa Nominal)
# ==============================================================================

cat("\n======================================================\n")
cat("ITEM 4: ANÁLISE DE VARIÁVEL QUALITATIVA - REGIÃO\n")
cat("======================================================\n")

# Tabela de frequências
freq_abs_regiao <- table(dados$regiao)
freq_rel_regiao <- prop.table(freq_abs_regiao) * 100

tabela_regiao <- data.frame(
  Regiao = names(freq_abs_regiao),
  Freq_Absoluta = as.numeric(freq_abs_regiao),
  Freq_Relativa_Pct = round(as.numeric(freq_rel_regiao), 2)
)

cat("\n[1] TABELA DE DISTRIBUIÇÃO DE FREQUÊNCIAS:\n")
print(tabela_regiao)

# Geração dos gráficos da variável qualitativa
png("grafico_2_qualitativa_regiao.png", width = 1300, height = 650, res = 130)
par(mfrow = c(1, 2), mar = c(5, 5, 4, 3))

# Paleta de cores harmoniosa
paleta_regioes <- c("#F9E79F", "#EDBB99", "#D7BDE2", "#AED6F1", "#A3E4D7")

# 1. Gráfico de Barras com todos os nomes visíveis e porcentagens
bp_regiao <- barplot(freq_rel_regiao,
                     col = paleta_regioes,
                     border = "#34495E",
                     main = "Participação por Região Geográfica (%)",
                     xlab = "Região",
                     ylab = "Frequência Relativa (%)",
                     ylim = c(0, max(freq_rel_regiao) * 1.3),
                     names.arg = c("Centro-Oeste", "Nordeste", "Norte", "Sudeste", "Sul"),
                     cex.names = 0.75,
                     las = 1)
# Rótulos no topo das barras
text(x = bp_regiao, y = freq_rel_regiao + 1.2, 
     labels = paste0(round(freq_rel_regiao, 1), "%\n(n=", freq_abs_regiao, ")"), 
     cex = 0.82, font = 2)

# 2. Gráfico de Pizza / Setores
rotulos_pizza <- paste0(names(freq_abs_regiao), "\n", round(freq_rel_regiao, 1), "%")
pie(freq_abs_regiao,
    labels = rotulos_pizza,
    col = paleta_regioes,
    border = "white",
    main = "Composição Amostral por Região",
    cex = 0.9)

dev.off()
cat(">> Gráfico salvo com sucesso: 'grafico_2_qualitativa_regiao.png'\n")


# ==============================================================================
# 4. ANÁLISE COMPLEMENTAR: VARIÁVEL QUALITATIVA ORDINAL (PORTE DA PROPRIEDADE)
# ==============================================================================

cat("\n======================================================\n")
cat("ANÁLISE COMPLEMENTAR: VARIÁVEL QUALITATIVA ORDINAL (PORTE)\n")
cat("======================================================\n")

# Ordenação lógica dos fatores (Pequeno < Médio < Grande)
dados$porte_propriedade <- factor(dados$porte_propriedade, 
                                  levels = c("Pequeno", "Médio", "Grande"), 
                                  ordered = TRUE)

freq_abs_porte <- table(dados$porte_propriedade)
freq_rel_porte <- prop.table(freq_abs_porte) * 100

tabela_porte <- data.frame(
  Porte = names(freq_abs_porte),
  Freq_Absoluta = as.numeric(freq_abs_porte),
  Freq_Relativa_Pct = round(as.numeric(freq_rel_porte), 2)
)
print(tabela_porte)

png("grafico_3_qualitativa_ordinal_porte.png", width = 800, height = 550, res = 130)
par(mar = c(5, 5, 4, 2))
cores_porte <- c("#FAD7A0", "#F8C471", "#E59866")
bp_porte <- barplot(freq_rel_porte,
                    col = cores_porte,
                    border = "#6E2C00",
                    main = "Distribuição por Porte da Propriedade (Ordinal)",
                    xlab = "Porte Agrícola (Pequeno < Médio < Grande)",
                    ylab = "Frequência Relativa (%)",
                    ylim = c(0, max(freq_rel_porte) * 1.25),
                    las = 1)
text(x = bp_porte, y = freq_rel_porte + 2.5, 
     labels = paste0(round(freq_rel_porte, 1), "% (n=", freq_abs_porte, ")"), 
     cex = 0.95, font = 2)
dev.off()
cat(">> Gráfico complementar salvo com sucesso: 'grafico_3_qualitativa_ordinal_porte.png'\n")

cat("\n======================================================\n")
cat(">>> TODOS OS ENTREGÁVEIS FORAM GERADOS COM SUCESSO! <<<\n")
cat("======================================================\n")
