# FarmTech Solutions - Agrosaas (FIAP - Fase 1)

Projeto desenvolvido para a **FarmTech Solutions** como parte do ecossistema de Agricultura Digital (FIAP - Fase 1).

---

## 🌾 Estrutura do Projeto

```
agrosaas/
├── .agents/
│   └── AGENTS.md                  # Memória do projeto e diretrizes
├── docs/
│   ├── CAP8.pdf                   # Artigo Embrapa original
│   ├── resumo_artigo_embrapa.pdf  # Resumo em PDF (A4, Arial 11, margem 2cm)
│   ├── resumo_artigo_embrapa.odt  # Resumo em ODT (A4, Arial 11)
│   ├── resumo_artigo_embrapa.html # Resumo em HTML formatado
│   ├── resumo_artigo_embrapa.md   # Resumo em Markdown
│   └── script_video.md            # Roteiro passo a passo para o vídeo no YouTube
├── src/
│   ├── python/
│   │   └── main.py                # Aplicação CRUD em Python (Café e Milho)
│   └── r/
│       ├── analysis.R             # Análise estatística (Média, SD, Mediana)
│       └── weather.R              # Integração API Meteorológica pública (Ir Além)
├── data/
│   └── dados_fazenda.csv          # Dataset compartilhado entre Python e R
├── link_video.txt                 # Arquivo TXT com o link do vídeo (YouTube)
├── gerar_zip_entrega.py           # Script para gerar o pacote ZIP de entrega
└── README.md                      # Documentação do repositório
```

---

## 🚀 Como Executar as Aplicações

### 1. Aplicação Python (Menu Interativo CRUD)
```bash
python3 src/python/main.py
```
- **Funcionalidades:**
  - Suporte a 2 culturas: **Café** (Área Retangular + Manejo de Pulverização) e **Milho** (Área Trapezoidal + Adubação Fosfatada).
  - Organização de dados em **vetores paralelos**.
  - Operações CRUD no menu terminal (Entrada, Saída, Atualização por posição, Deleção por posição e Saída).

### 2. Aplicação R (Análise Estatística Básica)
```bash
Rscript src/r/analysis.R
```
- **Funcionalidades:**
  - Leitura do dataset `data/dados_fazenda.csv`.
  - Cálculo de média, desvio padrão, mediana, mínimo e máximo das áreas plantadas (ha) e insumos por cultura.

### 3. Aplicação R (API Meteorológica em Tempo Real - Ir Além)
```bash
Rscript src/r/weather.R
```
- **Funcionalidades:**
  - Conexão com a API meteorológica pública **Open-Meteo**.
  - Coleta de temperatura, vento e condições climáticas da região agrícola.
  - Emissão de recomendação agronômica para pulverização no terminal.

---

## 📦 Gerando o Pacote de Entrega (.ZIP)
Para compactar automaticamente todos os arquivos exigidos para entrega na plataforma FIAP, execute:
```bash
python3 gerar_zip_entrega.py
```
O arquivo `entregavel_farmtech_fase1.zip` será gerado no diretório raiz pronto para submissão.
