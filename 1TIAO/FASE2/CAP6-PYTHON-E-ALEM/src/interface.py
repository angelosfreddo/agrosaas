"""
interface.py
------------
Procedimentos e funcoes de apresentacao no terminal (prompt de comando).

Objetivo: deixar os dados "limpos e de claro entendimento", conforme pedido
na atividade, mesmo sem interface grafica. Aqui ficam:
  - limpeza de tela, cabecalhos e separadores;
  - tabelas alinhadas em colunas;
  - barras horizontais em texto (mini graficos ASCII);
  - formatacao numerica no padrao brasileiro (R$ 1.234,56).

Nao ha emojis em nenhuma saida: apenas caracteres ASCII, que funcionam em
qualquer terminal (cmd, PowerShell, Linux, macOS).
"""

import os

LARGURA = 78  # largura padrao das telas

# ---------------------------------------------------------------------------
# Cores ANSI (opcionais). Desativadas se a variavel NO_COLOR existir.
# ---------------------------------------------------------------------------
_USAR_COR = os.environ.get("NO_COLOR") is None
if os.name == "nt":
    os.system("")  # habilita sequencias ANSI no console do Windows

CORES = {
    "reset": "\033[0m",
    "negrito": "\033[1m",
    "verde": "\033[92m",
    "amarelo": "\033[93m",
    "vermelho": "\033[91m",
    "magenta": "\033[95m",
    "ciano": "\033[96m",
    "cinza": "\033[90m",
}

# Dicionario: cor associada a cada classe de perda
COR_CLASSE = {
    "BAIXA": "verde",
    "MODERADA": "amarelo",
    "ALTA": "vermelho",
    "CRITICA": "magenta",
}


def cor(texto: str, nome_cor: str) -> str:
    """Funcao: devolve o texto envolvido pela cor ANSI (se habilitada)."""
    if not _USAR_COR or nome_cor not in CORES:
        return texto
    return f"{CORES[nome_cor]}{texto}{CORES['reset']}"


def cor_classe(classe: str) -> str:
    """Funcao: devolve a classificacao de perda ja colorida."""
    return cor(classe, COR_CLASSE.get(classe, "reset"))


# ---------------------------------------------------------------------------
# Formatacao numerica (padrao brasileiro)
# ---------------------------------------------------------------------------
def formatar_numero(valor: float, casas: int = 2) -> str:
    """Funcao: 1234.5 -> '1.234,50'."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_moeda(valor: float) -> str:
    """Funcao: 1234.5 -> 'R$ 1.234,50'."""
    return f"R$ {formatar_numero(valor, 2)}"


def formatar_data_br(data_iso: str) -> str:
    """Funcao: '2026-10-07' -> '07/10/2026'."""
    partes = data_iso.split("-")
    if len(partes) != 3:
        return data_iso
    return f"{partes[2]}/{partes[1]}/{partes[0]}"


# ---------------------------------------------------------------------------
# Estrutura de telas
# ---------------------------------------------------------------------------
def limpar_tela() -> None:
    """Procedimento: limpa o terminal (cls no Windows, clear nos demais)."""
    os.system("cls" if os.name == "nt" else "clear")


def linha(caractere: str = "-") -> None:
    """Procedimento: imprime uma linha separadora."""
    print(caractere * LARGURA)


def cabecalho(titulo: str, subtitulo: str = "") -> None:
    """Procedimento: imprime o cabecalho padrao de cada tela."""
    linha("=")
    print(cor(titulo.upper().center(LARGURA), "negrito"))
    if subtitulo:
        print(cor(subtitulo.center(LARGURA), "cinza"))
    linha("=")


def secao(titulo: str) -> None:
    """Procedimento: imprime o titulo de uma secao interna da tela."""
    print()
    print(cor(f"[ {titulo.upper()} ]", "ciano"))
    linha("-")


def mensagem_ok(texto: str) -> None:
    """Procedimento: mensagem de sucesso."""
    print(cor(f"  [OK] {texto}", "verde"))


def mensagem_aviso(texto: str) -> None:
    """Procedimento: mensagem de alerta."""
    print(cor(f"  [ATENCAO] {texto}", "amarelo"))


def mensagem_erro(texto: str) -> None:
    """Procedimento: mensagem de erro."""
    print(cor(f"  [ERRO] {texto}", "vermelho"))


def pausar() -> None:
    """Procedimento: aguarda o ENTER do usuario."""
    input(cor("\n  Pressione ENTER para continuar...", "cinza"))


def campo(rotulo: str, valor: str, largura_rotulo: int = 28) -> None:
    """Procedimento: imprime 'Rotulo.......: valor' alinhado."""
    print(f"  {rotulo.ljust(largura_rotulo, '.')}: {valor}")


# ---------------------------------------------------------------------------
# Tabelas e graficos em texto
# ---------------------------------------------------------------------------
def _ajustar(texto: str, largura: int, alinhamento: str) -> str:
    """Funcao interna: corta/alinha um texto para caber na coluna."""
    texto = str(texto)
    if len(texto) > largura:
        texto = texto[: largura - 1] + "~"
    if alinhamento == ">":
        return texto.rjust(largura)
    if alinhamento == "^":
        return texto.center(largura)
    return texto.ljust(largura)


def imprimir_tabela(colunas: tuple, linhas: list) -> None:
    """
    Procedimento: imprime uma tabela alinhada.

    colunas -> tupla de tuplas (titulo, largura, alinhamento '<' '>' '^')
    linhas  -> lista de tuplas/listas com os valores de cada linha.
               Uma celula pode ser uma tupla (valor, nome_cor) para ser
               exibida colorida sem perder o alinhamento.
    """
    titulo = " ".join(_ajustar(c[0], c[1], c[2]) for c in colunas)
    print("  " + cor(titulo, "negrito"))
    print("  " + " ".join("-" * c[1] for c in colunas))
    for registro in linhas:
        celulas = []
        for indice, coluna in enumerate(colunas):
            valor = registro[indice]
            if isinstance(valor, tuple):
                texto = _ajustar(valor[0], coluna[1], coluna[2])
                celulas.append(cor(texto, valor[1]))
            else:
                celulas.append(_ajustar(valor, coluna[1], coluna[2]))
        print("  " + " ".join(celulas))
    if not linhas:
        print(cor("  (nenhum registro)", "cinza"))


def barra(valor: float, maximo: float, largura: int = 30) -> str:
    """Funcao: devolve uma barra horizontal proporcional, ex.: '#######.....'."""
    if maximo <= 0:
        return "." * largura
    preenchido = round((valor / maximo) * largura)
    preenchido = max(0, min(largura, preenchido))
    return "#" * preenchido + "." * (largura - preenchido)
