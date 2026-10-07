"""
validacao.py
------------
Consistencia dos dados de entrada.

A atividade exige que o usuario NAO consiga digitar um tipo indesejado que
atrapalhe o entendimento ou a gravacao no banco. Por isso a validacao foi
dividida em duas camadas:

1) Funcoes "validar_*" (puras): recebem um TEXTO e devolvem uma TUPLA
   (valido: bool, resultado). Se valido, resultado e o valor ja convertido;
   se invalido, resultado e a mensagem de erro. Por serem puras, sao usadas
   tanto no teclado quanto na IMPORTACAO DE ARQUIVOS JSON (a mesma regra vale
   para o dado digitado e para o dado que chega do campo).

2) Funcoes "ler_*" (interativas): repetem a pergunta ate o usuario digitar
   um valor valido, usando as funcoes da camada 1.
"""

from datetime import date, datetime

from interface import mensagem_erro

DATA_MINIMA = date(2000, 1, 1)


# ===========================================================================
# CAMADA 1 - VALIDADORES PUROS (texto -> (bool, valor | mensagem))
# ===========================================================================
def validar_float(texto, minimo: float, maximo: float) -> tuple:
    """Funcao: valida numero real dentro de um intervalo. Aceita virgula."""
    if texto is None:
        return False, "campo ausente"
    if isinstance(texto, bool):
        return False, "valor logico nao e um numero"
    if isinstance(texto, (int, float)):
        numero = float(texto)
    else:
        texto = str(texto).strip().replace(",", ".")
        if texto == "":
            return False, "o campo nao pode ficar vazio"
        try:
            numero = float(texto)
        except ValueError:
            return False, f"'{texto}' nao e um numero valido"
    if numero != numero:  # NaN
        return False, "numero invalido"
    if numero < minimo or numero > maximo:
        return False, f"informe um valor entre {minimo:g} e {maximo:g}"
    return True, round(numero, 3)


def validar_inteiro(texto, minimo: int, maximo: int) -> tuple:
    """Funcao: valida numero inteiro dentro de um intervalo."""
    if texto is None:
        return False, "campo ausente"
    if isinstance(texto, bool):
        return False, "valor logico nao e um numero"
    if isinstance(texto, int):
        numero = texto
    else:
        texto = str(texto).strip()
        if texto == "":
            return False, "o campo nao pode ficar vazio"
        if not texto.lstrip("-").isdigit():
            return False, f"'{texto}' nao e um numero inteiro"
        numero = int(texto)
    if numero < minimo or numero > maximo:
        return False, f"informe um inteiro entre {minimo} e {maximo}"
    return True, numero


def validar_texto(texto, tamanho_min: int, tamanho_max: int) -> tuple:
    """
    Funcao: valida texto livre (nomes, fazendas, variedades).
    Remove espacos duplicados e bloqueia caracteres que quebram SQL/arquivos.
    """
    if texto is None:
        return False, "o campo nao pode ficar vazio"
    texto = " ".join(str(texto).split())
    if len(texto) < tamanho_min:
        return False, f"digite pelo menos {tamanho_min} caractere(s)"
    if len(texto) > tamanho_max:
        return False, f"digite no maximo {tamanho_max} caracteres"
    proibidos = (";", "'", '"', "\\", "|", "<", ">")
    for caractere in proibidos:
        if caractere in texto:
            return False, f"caractere nao permitido: {caractere}"
    return True, texto


def validar_codigo(texto, tamanho_max: int = 10) -> tuple:
    """
    Funcao: valida codigos (talhao, colhedora). Apenas letras, numeros e '-'.
    Converte para maiusculas, ex.: 't-01' -> 'T-01'.
    """
    if texto is None:
        return False, "o codigo nao pode ficar vazio"
    texto = str(texto).strip().upper()
    if len(texto) < 2 or len(texto) > tamanho_max:
        return False, f"o codigo deve ter de 2 a {tamanho_max} caracteres"
    for caractere in texto:
        if not (caractere.isalnum() or caractere == "-"):
            return False, "use apenas letras, numeros e hifen (ex.: T-01)"
    return True, texto


def validar_opcao(texto, opcoes: tuple) -> tuple:
    """Funcao: valida se o texto esta dentro de uma tupla de opcoes."""
    if texto is None:
        return False, "opcao vazia"
    texto = str(texto).strip().upper()
    if texto not in opcoes:
        return False, f"opcoes validas: {', '.join(opcoes)}"
    return True, texto


def validar_data(texto) -> tuple:
    """
    Funcao: valida data em dd/mm/aaaa (teclado) ou aaaa-mm-dd (JSON).
    Nao aceita datas futuras nem anteriores a 2000.
    Devolve a data no formato ISO (aaaa-mm-dd) para gravacao.
    """
    if texto is None:
        return False, "data vazia"
    texto = str(texto).strip()
    formatos = ("%d/%m/%Y", "%Y-%m-%d")
    data_convertida = None
    for formato in formatos:
        try:
            data_convertida = datetime.strptime(texto, formato).date()
            break
        except ValueError:
            continue
    if data_convertida is None:
        return False, f"'{texto}' nao e uma data valida (use dd/mm/aaaa)"
    if data_convertida > date.today():
        return False, "a data da avaliacao nao pode estar no futuro"
    if data_convertida < DATA_MINIMA:
        return False, "data muito antiga (minimo 01/01/2000)"
    return True, data_convertida.isoformat()


# ===========================================================================
# CAMADA 2 - LEITURAS INTERATIVAS (repetem ate o dado ficar consistente)
# ===========================================================================
def _ler(prompt: str, validador, *args, padrao=None):
    """
    Funcao generica: pergunta, valida e repete ate ficar correto.
    Se 'padrao' for informado, ENTER vazio assume o valor padrao.
    """
    sufixo = f" [{padrao}]" if padrao is not None else ""
    while True:
        resposta = input(f"  {prompt}{sufixo}: ")
        if resposta.strip() == "" and padrao is not None:
            resposta = str(padrao)
        valido, resultado = validador(resposta, *args)
        if valido:
            return resultado
        mensagem_erro(resultado)


def ler_float(prompt: str, minimo: float, maximo: float, padrao=None) -> float:
    """Funcao: le numero real valido."""
    return _ler(prompt, validar_float, minimo, maximo, padrao=padrao)


def ler_inteiro(prompt: str, minimo: int, maximo: int, padrao=None) -> int:
    """Funcao: le numero inteiro valido."""
    return _ler(prompt, validar_inteiro, minimo, maximo, padrao=padrao)


def ler_texto(prompt: str, tamanho_min: int, tamanho_max: int, padrao=None) -> str:
    """Funcao: le texto valido."""
    return _ler(prompt, validar_texto, tamanho_min, tamanho_max, padrao=padrao)


def ler_codigo(prompt: str, tamanho_max: int = 10, padrao=None) -> str:
    """Funcao: le codigo valido (letras, numeros e hifen)."""
    return _ler(prompt, validar_codigo, tamanho_max, padrao=padrao)


def ler_opcao(prompt: str, opcoes: tuple, padrao=None) -> str:
    """Funcao: le uma opcao pertencente a tupla 'opcoes'."""
    texto_prompt = f"{prompt} ({'/'.join(opcoes)})"
    return _ler(texto_prompt, validar_opcao, opcoes, padrao=padrao)


def ler_data(prompt: str) -> str:
    """Funcao: le data (ENTER = hoje). Devolve ISO aaaa-mm-dd."""
    hoje = date.today().strftime("%d/%m/%Y")
    return _ler(prompt + " (dd/mm/aaaa)", validar_data, padrao=hoje)


def confirmar(prompt: str) -> bool:
    """Funcao: pergunta S/N e devolve True/False (so aceita S ou N)."""
    resposta = ler_opcao(prompt, ("S", "N"))
    return resposta == "S"
