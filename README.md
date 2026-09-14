# FarmTech Solutions - Agrosaas (FIAP - Fase 1)

Projeto desenvolvido para a FarmTech Solutions como parte do ecossistema de Agricultura Digital (FIAP - Fase 1).

---

## Estrutura do Projeto

```
agrosaas/
├── .agents/
│   └── AGENTS.md                  # Memoria do projeto e diretrizes
├── docs/
│   ├── CAP8.pdf                   # Artigo Embrapa original
│   ├── resumo_artigo_embrapa.pdf  # Resumo em PDF (A4, Arial 11, margem 2cm)
│   ├── resumo_artigo_embrapa.odt  # Resumo em ODT (A4, Arial 11)
│   ├── resumo_artigo_embrapa.html # Resumo em HTML formatado
│   ├── resumo_artigo_embrapa.md   # Resumo em Markdown
│   └── script_video.md            # Roteiro passo a passo para o video no YouTube
├── src/
│   ├── python/
│   │   └── main.py                # Aplicacao CRUD em Python (Cafe e Milho)
│   └── r/
│       ├── analysis.R             # Analise estatistica (Media, SD, Mediana)
│       └── weather.R              # Integracao API Meteorologica publica (Ir Alem)
├── data/
│   └── dados_fazenda.csv          # Dataset compartilhado entre Python e R
├── link_video.txt                 # Arquivo TXT com o link do video (YouTube)
├── gerar_zip_entrega.py           # Script para gerar o pacote ZIP de entrega
└── README.md                      # Documentacao do repositorio
```

---

## Como Executar as Aplicacoes

### 1. Aplicacao Python (Menu Interativo CRUD)
```bash
python3 src/python/main.py
```
- Funcionalidades:
  - Suporte a 2 culturas: Cafe (Area Retangular + Manejo de Pulverizacao) e Milho (Area Trapezoidal + Adubacao Fosfatada).
  - Organizacao de dados em vetores paralelos.
  - Operacoes CRUD no menu terminal (Entrada, Saida, Atualizacao por posicao, Delecao por posicao e Saida).

### 2. Aplicacao R (Analise Estatistica Basica)
```bash
Rscript src/r/analysis.R
```
- Funcionalidades:
  - Leitura do dataset `data/dados_fazenda.csv`.
  - Calculo de media, desvio padrao, mediana, minimo e maximo das areas plantadas (ha) e insumos por cultura.

### 3. Aplicacao R (API Meteorologica em Tempo Real - Ir Alem)
```bash
Rscript src/r/weather.R
```
- Funcionalidades:
  - Conexao com a API meteorologica publica Open-Meteo.
  - Coleta de temperatura, vento e condicoes climaticas da regiao agricola.
  - Emissao de recomendacao agronomica para pulverizacao no terminal.

---

## Gerando o Pacote de Entrega (.ZIP)
Para compactar automaticamente todos os arquivos exigidos para entrega na plataforma FIAP, execute:
```bash
python3 gerar_zip_entrega.py
```
O arquivo `entregavel_farmtech_fase1.zip` sera gerado no diretorio raiz pronto para submissao.
