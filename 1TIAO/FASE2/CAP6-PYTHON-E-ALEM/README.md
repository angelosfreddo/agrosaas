# PerdaZero - Sistema de Gestao de Perdas na Colheita Mecanizada

> **FIAP - Fase 2: Gestao do Agronegocio em Python (Capitulos 3, 4, 5 e 6)**  
> **Turma:** 1TIAO  
> **Integrantes:**  
> - Angelo Sfreddo (RM: 566580)  

---

## 1. O Problema do Agronegocio Tratado

O Brasil e lider global na producao de cana-de-acucar (com safras superiores a 600 milhoes de toneladas), sendo pilar fundamental da matriz bioenergetica (etanol) e de acucar. Entretanto, a transicao da colheita manual para a colheita mecanizada gerou um gargalo critico:
* **Perdas Elevadas:** Enquanto a colheita manual apresentava perdas de aproximadamente 5%, na **colheita mecanizada as perdas de materia-prima deixada no solo chegam a 15%** (dados SOCICANA / UNICESUMAR).
* **Prejuizo Financeiro:** Em uma regiao tipica com produtividade de 100 t/ha, cada ponto percentual perdido representa milhoes de reais em biomassa e Acucar Total Recuperavel (ATR) deixados no campo.
* **Falta de Diagnostico em Tempo Real:** O gestor rural e o operador de colhedora frequentemente nao sabem **quanto perderam, onde perderam e qual o componente da maquina que causou a perda**.

O **PerdaZero** atua como uma solucao **AgroSaaS / Edge-Computing** para solucionar essa dor: permite que fiscais de qualidade e engenheiros agronomicos realizem amostragens de campo com molduras tecnicas, registrem os tipos de residuos (toco, tolete, cana inteira, ponteiro e estilhaco), calculem a perda em t/ha, percentual e prejuizo em R$ (modelo ATR), e recebam um **diagnostico de causa-raiz imediato** para regulagem da colhedora.

---

## 2. Conteudos da Disciplina Atendidos

| Conteudo | Aplicacao no Projeto |
| :--- | :--- |
| **Subalgoritmos (Cap. 3)** | Funcoes e procedimentos puros modulares com passagem de parametros em `calculos.py`, `validacao.py`, `interface.py`, `arquivos.py`, `repositorio.py` e `banco_oracle.py`. |
| **Estruturas de Dados (Cap. 4)** | **Tuplas** para constantes de dominio e retornos `(valido, valor)`; **Dicionarios** para base de conhecimento, parametros e registros; **Listas** para colecoes de talhoes e amostras; **Tabela de Memoria** em `ctx` com manipulacao de matrizes/tabelas no prompt. |
| **Manipulacao de Arquivos (Cap. 5)** | **JSON** para parametros (`config/parametros.json`), base offline (`data/base_local.json`), importacao de lotes (`data/coleta_campo_exemplo.json`) e exportacao; **Texto (.TXT)** para laudos tecnicos em `output/laudos/`, log de auditoria em `output/log_operacoes.txt` e descarte de dados rejeitados. |
| **Banco de Dados Oracle (Cap. 6)** | Integracao via `oracledb` com o banco FIAP (`oracle.fiap.com.br:1521/ORCL`), tabelas `PZ_TALHAO` e `PZ_AVALIACAO_PERDA` com *constraints* (`CHECK`, `FK`), indices e uso estrito de *bind variables* contra SQL Injection. |

---

## 3. Diferenciais e Inovacoes ("Ir Alem")

1. **Arquitetura Offline-First:** No campo, o sinal 4G/5G costuma ser inexistente ou instavel. O PerdaZero salva localmente em JSON (`base_local.json`) e, assim que conectado ao Oracle, realiza a sincronizacao em lote (*Upsert/Merge*).
2. **Diagnostico de Causa-Raiz da Colhedora:** O sistema correlaciona a composicao do residuo com a falha mecanica:
   * *Toco alto:* corte basal alto, facas desgastadas ou suspensao desregulada.
   * *Tolete/rebolo:* velocidade de translado excessiva ou descompasso do transbordo.
   * *Cana inteira:* divisores de linha desajustados ou colheita contra o acamamento.
   * *Ponteiro:* despontador muito baixo cortando colmo util.
   * *Estilhaco:* facas do picador cegas ou rotacao excessiva do extrator primario.
3. **Simulador Financeiro com Regras CONSECANA/ATR:** Projeta o ganho monetario direto ao reduzir o percentual de perdas para a meta agronômica estabelecida.
4. **Validacao Robusta de Entradas:** Dupla camada de consistencia que impede caracteres que quebram queries, tipos inconsistentes ou valores fora das faixas agronomicas.

---

## 4. Estrutura de Diretorios

```text
├── config/
│   └── parametros.json             # Parametros economicos (ATR, preco) e metas
├── data/
│   ├── base_local.json             # Base de dados local (Modo Offline)
│   └── coleta_campo_exemplo.json   # Arquivo JSON de exemplo para importacao em lote
├── output/                         # Criado automaticamente durante a execucao
│   ├── laudos/                     # Laudos tecnicos emitidos em arquivo .txt
│   ├── exportacoes/                # Dados consolidados exportados em JSON
│   └── log_operacoes.txt           # Trilha de auditoria das operacoes
├── scripts/
│   └── ddl_perdazero.sql           # Script SQL com criacao das tabelas no Oracle
├── src/
│   ├── main.py                     # Ponto de entrada e fluxo dos menus
│   ├── calculos.py                 # Funcoes agronomicas, financeiras e diagnostico
│   ├── validacao.py                # Consistencia de entradas do usuario e dados JSON
│   ├── interface.py                # Formatacao visual do terminal, cores e tabelas
│   ├── arquivos.py                 # Leitura e escrita de JSON e TXT
│   ├── repositorio.py              # Camada de uniao: memoria + JSON local + Oracle
│   └── banco_oracle.py             # Conexao e operacoes SQL no Oracle Database
├── tests/
│   └── test_calculos.py            # Testes unitarios das regras agronomicas
├── requirements.txt                # Dependencias do projeto
└── README.md                       # Documentacao do projeto
```

---

## 5. Como Executar

### Pre-requisitos
* Python 3.10 ou superior instalado.
* Criacao e ativacao de ambiente virtual (opcional, mas recomendado):
  ```bash
  python -m venv .venv
  source .venv/bin/activate    # Linux / Mac
  # .venv\Scripts\activate     # Windows
  ```
* Instalacao das dependencias:
  ```bash
  pip install -r requirements.txt
  ```

### Executando o Sistema
```bash
python src/main.py
```

### Executando os Testes Unitarios
```bash
python -m unittest discover tests
```

---

## 6. Navegacao Pelos Menus do Sistema

Ao iniciar o programa, voce acessara o painel principal:

* **`[1] Talhoes (cadastro)`**: Gerencia os talhoes cadastrados (Cadastrar, Listar, Alterar e Excluir com confirmacao).
* **`[2] Registrar avaliacao de perdas`**: Modulo central de campo. Informa as massas recolhidas por tipo de perda e recebe na hora a classificacao (*BAIXA, MODERADA, ALTA, CRITICA*), perda em t/ha, % de perda e recomendacoes corretivas.
* **`[3] Consultar avaliacoes`**: Lista historica das amostragens e busca detalhada por codigo.
* **`[4] Painel gerencial`**: Indicadores consolidados, ranking de perdas por operador/colhedora e distribuicao dos tipos de residuo.
* **`[5] Simulador de ganho`**: Calculadora de ROI simulando a economia financeira em R$ ao atingir as metas agronomicas de reducao de perdas.
* **`[6] Arquivos`**: Emite laudos tecnicos individuais em `.txt`, exporta base para JSON, importa coletas de campo em lote (como `data/coleta_campo_exemplo.json`) e exibe o log de auditoria.
* **`[7] Banco de dados Oracle`**: Painel de integracao com o banco FIAP. Permite conectar com usuario/senha, sincronizar registros offline pendentes e descarregar atualizacoes.
* **`[8] Parametros`**: Permite aos engenheiros agronomicos ajustar precos do ATR, produtividade padrao e tolerancias de perda.
* **`[0] Sair`**: Salva o estado atual na base local e encerra a aplicacao de forma segura.
