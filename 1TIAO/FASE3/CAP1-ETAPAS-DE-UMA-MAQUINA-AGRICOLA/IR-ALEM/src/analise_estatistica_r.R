# ============================================================================
# Projeto: FarmTech Solutions - Fase 3 (Ir Alem)
# Script: analise_estatistica_r.R
# Objetivo: Analise estatistica complementar em linguagem R sobre as leituras
#           tratadas dos sensores (media, desvio padrao, quantis, correlacao
#           de Pearson e regressao linear simples entre umidade e bomba).
# Execucao: Rscript IR-ALEM/src/analise_estatistica_r.R
# ============================================================================

caminho_csv <- "data/processed/leituras_tratadas.csv"
if (!file.exists(caminho_csv)) {
  caminho_csv <- "../../data/processed/leituras_tratadas.csv"
}

dados <- read.csv(caminho_csv, stringsAsFactors = FALSE)

cat("==============================================================================\n")
cat("ANALISE ESTATISTICA COMPLEMENTAR EM R - FARMTECH SOLUTIONS (FASE 3)\n")
cat("==============================================================================\n\n")

cat("1. ESTATISTICAS DESCRITIVAS - UMIDADE DO SOLO (%)\n")
cat(sprintf("   Media ..............: %.2f %%\n", mean(dados$umidade)))
cat(sprintf("   Desvio Padrao ......: %.2f %%\n", sd(dados$umidade)))
cat(sprintf("   Mediana ............: %.2f %%\n", median(dados$umidade)))
cat(sprintf("   Minimo / Maximo ....: %.2f %% / %.2f %%\n\n", min(dados$umidade), max(dados$umidade)))

cat("2. ESTATISTICAS DESCRITIVAS - NIVEL DE pH DO SOLO\n")
cat(sprintf("   Media ..............: %.2f\n", mean(dados$ph)))
cat(sprintf("   Desvio Padrao ......: %.3f\n", sd(dados$ph)))
cat(sprintf("   Mediana ............: %.2f\n", median(dados$ph)))
cat(sprintf("   Minimo / Maximo ....: %.2f / %.2f\n\n", min(dados$ph), max(dados$ph)))

cat("3. CORRELACAO DE PEARSON COM O ACIONAMENTO DA BOMBA\n")
vars <- c("umidade_suavizada", "ph_suavizado", "fosforo", "potassio", "nitrogenio", "chuva")
for (v in vars) {
  r <- cor(dados[[v]], dados$bomba, method = "pearson")
  cat(sprintf("   cor(%-18s, bomba) = %+0.4f\n", v, r))
}

cat("\n4. PROPORCAO DE HORAS COM BOMBA LIGADA POR FAIXA DE UMIDADE\n")
faixa <- ifelse(dados$umidade < 40, "1_Critica (<40%)",
         ifelse(dados$umidade < 60, "2_Histerese (40-59.9%)", "3_Adequada (>=60%)"))
tabela <- aggregate(bomba ~ faixa, data = data.frame(faixa = faixa, bomba = dados$bomba),
                    FUN = function(x) c(horas = length(x), ligada = sum(x), taxa = round(mean(x) * 100, 2)))
print(do.call(data.frame, tabela), row.names = FALSE)

