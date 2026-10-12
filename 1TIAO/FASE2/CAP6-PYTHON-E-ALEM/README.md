# PerdaZero - Sistema de Gestao de Perdas na Colheita

Bem-vindo ao **PerdaZero**, a solucao em software (AgroSaaS) para monitoramento e gestao inteligente de perdas na colheita mecanizada de cana-de-acucar. Este sistema foi desenvolvido como entrega da Fase 2 do curso da FIAP (Gestao do Agronegocio em Python).

## O Que Este Sistema Faz?
Na colheita mecanizada, as perdas de materia-prima (cana deixada no chao) podem chegar a 15%. O produtor raramente sabe **quanto perdeu, onde perdeu e qual foi a causa**. 

O PerdaZero resolve isso! Ele roda direto no campo (ate mesmo sem internet), registra os residuos da colheita, faz o calculo agronomico transformando Quilos (Kg) em Toneladas por Hectare (t/ha), calcula o prejuizo financeiro e diagnostica onde a colhedora falhou. 

Quando a internet volta, ele manda tudo pro banco de dados Oracle da matriz.

---

## Como Executar o Programa

### Pre-requisitos
1. Ter o Python 3 instalado.
2. Ativar sua Virtual Environment (`.venv`).
3. Instalar as dependencias (`pip install pandas oracledb`).

### Executando
Basta abrir o terminal, navegar ate a pasta do projeto e rodar:
```bash
python src/main.py
```

---

## Estrutura e Pastas do Projeto
- `src/` -> Codigo-fonte (A logica principal esta em `main.py`).
- `config/` -> Arquivo `parametros.json` onde os engenheiros agronomicos ajustam os precos da cana, do ATR e as tolerancias de perda.
- `data/` -> Onde o arquivo `base_local.json` e criado para fazer o modo Offline funcionar.
- `laudos/` -> Onde o sistema salva os Laudos impressos (.txt) que sao gerados no menu 6.
- `scratch/` -> Rascunhos.

---

## Navegando Pelos Menus
Ao rodar o programa, voce vera 9 opcoes:

1. **`[1] Cadastrar Talhao`**: O "Talhao" e o pedaco de terra. Voce informa a area, fazenda, variedade da cana e qual a produtividade esperada.
2. **`[2] Listar Talhoes`**: Mostra na tela uma tabela com todas as rocas cadastradas.
3. **`[3] Excluir Talhao`**: Deleta o registro do sistema (Cuidado: deleta em cascata as avaliacoes tambem).
4. **`[4] Registrar Avaliacao de Perdas`**: O coracao do sistema. O fiscal preenche os quilos de cana que achou no chao (toco, cana inteira, rebolo) e o sistema te devolve instantaneamente se a colheita foi Otima, Aceitavel ou Critica.
5. **`[5] Importar Dados de Coleta (JSON)`**: Em vez de digitar na mao, se voce tiver um pendrive com varias coletas do campo, o sistema importa tudo de uma vez.
6. **`[6] Ranking de Eficiencia de Colheita`**: Monta um podio mostrando quais colhedoras ou quais operadores deram mais prejuizo para a Usina.
7. **`[7] Gerar Laudos de Perda (TXT)`**: Cria um "recibo" tecnico (.txt) que o fiscal pode mandar por WhatsApp para o operador da maquina consertar a colheita na hora.
8. **`[8] Banco de dados Oracle`**: Abre o menu de Conexao (onde a magica Offline acontece).
9. **`[0] Sair`**: Fecha o sistema com seguranca.

---

## Integracao com Oracle e o Modo "Offline-First"
O PerdaZero nao trava se voce ficar sem internet!

* **Modo Offline:** Por padrao, ou se a internet cair, ele funciona 100% usando o `base_local.json`.
* **Conectando no Banco:** Va no Menu `[8]` -> Digite `[1]`. Insira seu **RM da FIAP** e sua **Senha** (data de nascimento com 6 numeros). O sistema se conecta ao banco `oracle.fiap.com.br`.
* **Sincronizacao:** Assim que conecta, ele cria as tabelas automaticamente se for seu primeiro acesso e **faz upload** de todas as coletas que voce salvou no modo offline para a nuvem da Oracle.

## Entendendo os Resultados (Diagnostico)
Ao registrar uma perda, observe a classificacao:
* **[OTIMO / BOM]**: Tudo certo! Operador mandando bem.
* **[ACEITAVEL / ALERTA]**: Atencao, precisa regular as facas da maquina.
* **[CRITICO]**: Pare a maquina! Muito dinheiro sendo deixado no chao.

> **Dica de Mestre:** Para testar a importacao automatica, escolha a opcao de menu `[5]` e digite `data/coleta_campo_exemplo.json`. Ele importara coletas de teste prontas em 1 segundo.
