# PerdaZero 🌾 - Sistema de Gestão de Perdas na Colheita

Bem-vindo ao **PerdaZero**, a solução em software (AgroSaaS) para monitoramento e gestão inteligente de perdas na colheita mecanizada de cana-de-açúcar. Este sistema foi desenvolvido como entrega da Fase 2 do curso da FIAP (Gestão do Agronegócio em Python).

## 🎯 O Que Este Sistema Faz?
Na colheita mecanizada, as perdas de matéria-prima (cana deixada no chão) podem chegar a 15%. O produtor raramente sabe **quanto perdeu, onde perdeu e qual foi a causa**. 

O PerdaZero resolve isso! Ele roda direto no campo (até mesmo sem internet), registra os resíduos da colheita, faz o cálculo agronômico transformando Quilos (Kg) em Toneladas por Hectare (t/ha), calcula o prejuízo financeiro e diagnostica onde a colhedora falhou. 

Quando a internet volta, ele manda tudo pro banco de dados Oracle da matriz.

---

## 🚀 Como Executar o Programa

### Pré-requisitos
1. Ter o Python 3 instalado.
2. Ativar sua Virtual Environment (`.venv`).
3. Instalar as dependências (`pip install pandas oracledb`).

### Executando
Basta abrir o terminal, navegar até a pasta do projeto e rodar:
```bash
python src/main.py
```

---

## 🗂 Estrutura e Pastas do Projeto
- `src/` → Código-fonte (A lógica principal está em `main.py`).
- `config/` → Arquivo `parametros.json` onde os engenheiros agronômicos ajustam os preços da cana, do ATR e as tolerâncias de perda.
- `data/` → Onde o arquivo `base_local.json` é criado para fazer o modo Offline funcionar.
- `laudos/` → Onde o sistema salva os Laudos impressos (.txt) que são gerados no menu 6.
- `scratch/` → Rascunhos.

---

## 🛠️ Navegando Pelos Menus
Ao rodar o programa, você verá 9 opções:

1. **`[1] Cadastrar Talhão`**: O "Talhão" é o pedaço de terra. Você informa a área, fazenda, variedade da cana e qual a produtividade esperada.
2. **`[2] Listar Talhões`**: Mostra na tela uma tabela com todas as roças cadastradas.
3. **`[3] Excluir Talhão`**: Deleta o registro do sistema (Cuidado: deleta em cascata as avaliações também).
4. **`[4] Registrar Avaliação de Perdas`**: O coração do sistema. O fiscal preenche os quilos de cana que achou no chão (toco, cana inteira, rebolo) e o sistema te devolve instantaneamente se a colheita foi Ótima, Aceitável ou Crítica.
5. **`[5] Importar Dados de Coleta (JSON)`**: Em vez de digitar na mão, se você tiver um pendrive com várias coletas do campo, o sistema importa tudo de uma vez.
6. **`[6] Ranking de Eficiência de Colheita`**: Monta um pódio mostrando quais colhedoras ou quais operadores deram mais prejuízo para a Usina.
7. **`[7] Gerar Laudos de Perda (TXT)`**: Cria um "recibo" técnico (.txt) que o fiscal pode mandar por WhatsApp para o operador da máquina consertar a colheita na hora.
8. **`[8] Banco de dados Oracle`**: Abre o menu de Conexão (onde a mágica Offline acontece).
9. **`[0] Sair`**: Fecha o sistema com segurança.

---

## 🌐 A Mágica do Oracle e o Modo "Offline-First"
O PerdaZero não trava se você ficar sem internet!

* **Modo Offline:** Por padrão, ou se a internet cair, ele funciona 100% usando o `base_local.json`.
* **Conectando no Banco:** Vá no Menu `[8]` -> Digite `[1]`. Insira seu **RM da FIAP** e sua **Senha** (data de nascimento com 6 números). O sistema se conecta ao banco `oracle.fiap.com.br`.
* **Sincronização:** Assim que conecta, ele cria as tabelas automaticamente se for seu primeiro acesso e **faz upload** de todas as coletas que você salvou no modo offline para a nuvem da Oracle.

## 📊 Entendendo os Resultados (Diagnóstico)
Ao registrar uma perda, observe a classificação:
* 🟢 **OTIMO / BOM**: Tudo certo! Operador mandando bem.
* 🟡 **ACEITAVEL / ALERTA**: Atenção, precisa regular as facas da máquina.
* 🔴 **CRITICO**: Pare a máquina! Muito dinheiro sendo deixado no chão.

> **💡 Dica de Mestre:** Para testar a importação automática, escolha a opção de menu `[5]` e digite `data/coleta_campo_exemplo.json`. Ele importará coletas de teste prontas em 1 segundo.
