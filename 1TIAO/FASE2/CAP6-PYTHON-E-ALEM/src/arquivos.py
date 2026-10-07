"""
arquivos.py
-----------
Manipulacao de ARQUIVOS TEXTO e JSON (Capitulo 5).

Uso de cada arquivo na solucao:

  JSON  config/parametros.json      -> parametros economicos e metas (leitura e gravacao)
  JSON  data/base_local.json        -> base OFFLINE: copia local da tabela de memoria,
                                       usada no campo sem internet e sincronizada depois
  JSON  data/coleta_campo_*.json    -> lote vindo do app/planilha da equipe de campo (importacao)
  JSON  output/exportacoes/*.json   -> exportacao para cooperativa/consultoria/BI
  TXT   output/laudos/*.txt         -> laudo tecnico de perdas por avaliacao
  TXT   output/log_operacoes.txt    -> trilha de auditoria (modo 'a' = append)
  TXT   output/rejeitados_*.txt     -> registros recusados na importacao e o motivo
"""

import json
import os
from datetime import datetime

from calculos import (ROTULOS_PERDA, TIPOS_COLHEITA, TIPOS_PERDA, TURNOS,
                      composicao_perdas)
from validacao import (validar_codigo, validar_data, validar_float,
                       validar_inteiro, validar_opcao, validar_texto)

# ---------------------------------------------------------------------------
# Caminhos (relativos a raiz do projeto, independente de onde o script roda)
# ---------------------------------------------------------------------------
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQ_PARAMETROS = os.path.join(RAIZ, "config", "parametros.json")
ARQ_BASE_LOCAL = os.path.join(RAIZ, "data", "base_local.json")
ARQ_COLETA_EXEMPLO = os.path.join(RAIZ, "data", "coleta_campo_exemplo.json")
DIR_SAIDA = os.path.join(RAIZ, "output")
DIR_LAUDOS = os.path.join(DIR_SAIDA, "laudos")
DIR_EXPORTACOES = os.path.join(DIR_SAIDA, "exportacoes")
ARQ_LOG = os.path.join(DIR_SAIDA, "log_operacoes.txt")


def _garantir_pasta(caminho_arquivo: str) -> None:
    """Procedimento: cria a pasta do arquivo, se ainda nao existir."""
    pasta = os.path.dirname(caminho_arquivo)
    if pasta and not os.path.isdir(pasta):
        os.makedirs(pasta)


def _carimbo() -> str:
    """Funcao: data/hora atual para nome de arquivo, ex.: 20261007_153012."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ===========================================================================
# JSON GENERICO
# ===========================================================================
def ler_json(caminho: str, padrao=None):
    """
    Funcao: le um arquivo JSON e devolve o objeto Python (dict/list).
    Se o arquivo nao existir ou estiver corrompido, devolve 'padrao'.
    """
    if not os.path.exists(caminho):
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.loads(arquivo.read())
    except (json.JSONDecodeError, OSError):
        return padrao


def gravar_json(caminho: str, dados) -> None:
    """Procedimento: grava um objeto Python em JSON formatado (indent=4)."""
    _garantir_pasta(caminho)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(dados, indent=4, ensure_ascii=False))


# ===========================================================================
# PARAMETROS
# ===========================================================================
def carregar_parametros() -> dict:
    """Funcao: carrega config/parametros.json (obrigatorio)."""
    parametros = ler_json(ARQ_PARAMETROS)
    if parametros is None:
        raise FileNotFoundError(
            f"Arquivo de parametros ausente ou invalido: {ARQ_PARAMETROS}")
    return parametros


def salvar_parametros(parametros: dict) -> None:
    """Procedimento: grava os parametros alterados pelo usuario."""
    gravar_json(ARQ_PARAMETROS, parametros)


# ===========================================================================
# BASE LOCAL (MODO OFFLINE)
# ===========================================================================
def carregar_base_local() -> dict:
    """Funcao: carrega a base offline. Estrutura vazia se nao existir."""
    base = ler_json(ARQ_BASE_LOCAL, padrao=None)
    if not isinstance(base, dict):
        base = {}
    base.setdefault("talhoes", [])
    base.setdefault("avaliacoes", [])
    base.setdefault("exclusoes_pendentes", {"talhoes": [], "avaliacoes": []})
    return base


def salvar_base_local(base: dict) -> None:
    """Procedimento: persiste a base offline em JSON."""
    base["atualizado_em"] = datetime.now().isoformat(timespec="seconds")
    gravar_json(ARQ_BASE_LOCAL, base)


# ===========================================================================
# LOG DE OPERACOES (arquivo texto em modo append)
# ===========================================================================
def registrar_log(mensagem: str) -> None:
    """Procedimento: acrescenta uma linha no log de auditoria."""
    _garantir_pasta(ARQ_LOG)
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(ARQ_LOG, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{agora} | {mensagem}\n")


def ler_ultimas_linhas_log(quantidade: int = 15) -> list:
    """Funcao: devolve as ultimas linhas do log (lista de strings)."""
    if not os.path.exists(ARQ_LOG):
        return []
    with open(ARQ_LOG, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()
    return [linha.rstrip("\n") for linha in linhas[-quantidade:]]


# ===========================================================================
# LAUDO TECNICO EM TEXTO
# ===========================================================================
def _num(valor: float, casas: int = 2) -> str:
    """Funcao interna: numero no padrao brasileiro."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_laudo_txt(avaliacao: dict, talhao: dict, diagnostico: list,
                    simulacao: dict, meta_pct: float) -> str:
    """
    Funcao: gera o laudo tecnico de uma avaliacao em arquivo .txt e devolve
    o caminho do arquivo. Usa writelines() com uma lista de linhas.
    """
    largura = 72
    composicao = composicao_perdas(avaliacao["amostras"])
    data_br = datetime.strptime(avaliacao["data_avaliacao"], "%Y-%m-%d").strftime("%d/%m/%Y")
    velocidade = avaliacao.get("velocidade_kmh")

    linhas = [
        "=" * largura + "\n",
        "PERDAZERO - LAUDO TECNICO DE PERDAS NA COLHEITA DE CANA".center(largura) + "\n",
        "=" * largura + "\n",
        f"Avaliacao ........: {avaliacao['cod_avaliacao']}\n",
        f"Data .............: {data_br}\n",
        f"Emitido em .......: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n",
        "\n",
        "-- TALHAO " + "-" * (largura - 10) + "\n",
        f"Codigo / Fazenda .: {talhao['codigo']} / {talhao['fazenda']}\n",
        f"Area .............: {_num(talhao['area_ha'])} ha\n",
        f"Variedade ........: {talhao['variedade']} ({talhao['estagio_corte']}o corte)\n",
        f"Produtividade ....: {_num(talhao['produtividade_t_ha'], 1)} t/ha\n",
        "\n",
        "-- OPERACAO " + "-" * (largura - 12) + "\n",
        f"Tipo de colheita .: {avaliacao['tipo_colheita']}\n",
        f"Colhedora ........: {avaliacao.get('colhedora') or '-'}\n",
        f"Operador / Turno .: {avaliacao.get('operador') or '-'} / {avaliacao['turno']}\n",
        f"Velocidade .......: {_num(velocidade, 1) + ' km/h' if velocidade else '-'}\n",
        f"Amostragem .......: {avaliacao['pontos_amostrados']} ponto(s), "
        f"{_num(avaliacao['area_amostrada_m2'], 1)} m2\n",
        "\n",
        "-- RESULTADO " + "-" * (largura - 13) + "\n",
        f"Cana recolhida ...: {_num(avaliacao['kg_total'])} kg\n",
        f"Perda ............: {_num(avaliacao['perda_t_ha'], 3)} t/ha\n",
        f"Perda percentual .: {_num(avaliacao['perda_pct'])} %\n",
        f"Classificacao ....: {avaliacao['classificacao']}\n",
        f"Prejuizo estimado : R$ {_num(avaliacao['prejuizo_rs'])}\n",
        "\n",
        "-- COMPOSICAO DA PERDA " + "-" * (largura - 23) + "\n",
    ]

    for tipo in TIPOS_PERDA:
        participacao = composicao[tipo]
        barra = "#" * round(participacao / 100 * 30)
        linhas.append(f"{ROTULOS_PERDA[tipo]:<28} {participacao:5.1f}% {barra}\n")

    linhas.append("\n")
    linhas.append("-- DIAGNOSTICO E RECOMENDACOES " + "-" * (largura - 31) + "\n")
    for prioridade, titulo, causa, acao in diagnostico:
        linhas.append(f"{prioridade}. {titulo}\n")
        linhas.append(f"   Causa provavel: {causa}\n")
        linhas.append(f"   Acao..........: {acao}\n")

    linhas.append("\n")
    linhas.append("-- SIMULACAO DE GANHO " + "-" * (largura - 22) + "\n")
    if simulacao["ganho_rs"] > 0:
        linhas.append(f"Se a perda cair para a meta de {_num(meta_pct, 1)}%, o talhao recupera\n")
        linhas.append(f"{_num(simulacao['toneladas_recuperadas'])} t de cana = "
                      f"R$ {_num(simulacao['ganho_rs'])} por safra.\n")
    else:
        linhas.append(f"Talhao ja esta dentro da meta de {_num(meta_pct, 1)}%.\n")
    linhas.append("=" * largura + "\n")

    nome = f"laudo_{avaliacao['codigo_talhao']}_{avaliacao['cod_avaliacao']}.txt"
    caminho = os.path.join(DIR_LAUDOS, nome)
    _garantir_pasta(caminho)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.writelines(linhas)
    return caminho


# ===========================================================================
# EXPORTACAO JSON
# ===========================================================================
def exportar_json(talhoes: list, avaliacoes: list, resumo: dict) -> str:
    """Funcao: exporta talhoes, avaliacoes e resumo em JSON. Devolve o caminho."""
    pacote = {
        "sistema": "PerdaZero",
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "resumo": resumo,
        "talhoes": [_sem_controle(t) for t in talhoes],
        "avaliacoes": [_sem_controle(a) for a in avaliacoes],
    }
    caminho = os.path.join(DIR_EXPORTACOES, f"perdazero_{_carimbo()}.json")
    gravar_json(caminho, pacote)
    return caminho


def _sem_controle(registro: dict) -> dict:
    """Funcao interna: remove campos de controle interno antes de exportar."""
    copia = dict(registro)
    copia.pop("sincronizado", None)
    return copia


# ===========================================================================
# IMPORTACAO DE COLETA DE CAMPO (JSON) COM CONSISTENCIA REGISTRO A REGISTRO
# ===========================================================================
def validar_talhao_dict(dados: dict) -> tuple:
    """
    Funcao: valida um talhao vindo de arquivo.
    Devolve (True, talhao_limpo) ou (False, lista_de_erros).
    """
    erros = []
    talhao = {}
    regras = (
        ("codigo", validar_codigo, (10,)),
        ("fazenda", validar_texto, (2, 60)),
        ("area_ha", validar_float, (0.1, 100000)),
        ("variedade", validar_texto, (2, 30)),
        ("estagio_corte", validar_inteiro, (1, 15)),
        ("produtividade_t_ha", validar_float, (10, 250)),
    )
    for campo, validador, argumentos in regras:
        ok, resultado = validador(dados.get(campo), *argumentos)
        if ok:
            talhao[campo] = resultado
        else:
            erros.append(f"{campo}: {resultado}")
    if erros:
        return False, erros
    return True, talhao


def validar_avaliacao_dict(dados: dict, codigos_talhoes: set) -> tuple:
    """
    Funcao: valida uma avaliacao vinda de arquivo (mesmas regras do teclado).
    Devolve (True, avaliacao_limpa) ou (False, lista_de_erros).
    """
    erros = []
    avaliacao = {}

    ok, codigo = validar_codigo(dados.get("codigo_talhao"))
    if not ok:
        erros.append(f"codigo_talhao: {codigo}")
    elif codigo not in codigos_talhoes:
        erros.append(f"codigo_talhao: talhao {codigo} nao cadastrado")
    else:
        avaliacao["codigo_talhao"] = codigo

    regras = (
        ("data_avaliacao", validar_data, ()),
        ("tipo_colheita", validar_opcao, (TIPOS_COLHEITA,)),
        ("turno", validar_opcao, (TURNOS,)),
        ("pontos_amostrados", validar_inteiro, (1, 50)),
        ("area_amostrada_m2", validar_float, (1, 5000)),
    )
    for campo, validador, argumentos in regras:
        ok, resultado = validador(dados.get(campo), *argumentos)
        if ok:
            avaliacao[campo] = resultado
        else:
            erros.append(f"{campo}: {resultado}")

    if avaliacao.get("tipo_colheita") == "MECANIZADA":
        for campo, validador, argumentos in (
                ("colhedora", validar_codigo, (20,)),
                ("operador", validar_texto, (2, 60)),
                ("velocidade_kmh", validar_float, (0.5, 15))):
            ok, resultado = validador(dados.get(campo), *argumentos)
            if ok:
                avaliacao[campo] = resultado
            else:
                erros.append(f"{campo}: {resultado}")
    else:
        avaliacao["colhedora"] = None
        avaliacao["velocidade_kmh"] = None
        ok, resultado = validar_texto(dados.get("operador") or "Equipe manual", 2, 60)
        avaliacao["operador"] = resultado if ok else "Equipe manual"

    amostras_origem = dados.get("amostras")
    if not isinstance(amostras_origem, dict):
        erros.append("amostras: bloco ausente ou em formato invalido")
    else:
        amostras = {}
        for tipo in TIPOS_PERDA:
            ok, resultado = validar_float(amostras_origem.get(tipo, 0), 0, 5000)
            if ok:
                amostras[tipo] = resultado
            else:
                erros.append(f"amostras.{tipo}: {resultado}")
        avaliacao["amostras"] = amostras

    if erros:
        return False, erros
    return True, avaliacao


def ler_lote_campo(caminho: str) -> dict:
    """
    Funcao: le o arquivo de coleta de campo. Levanta ValueError se o
    arquivo nao existir ou nao for um JSON no formato esperado.
    """
    if not os.path.exists(caminho):
        raise ValueError(f"arquivo nao encontrado: {caminho}")
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            lote = json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise ValueError(f"JSON invalido (linha {erro.lineno}): {erro.msg}") from erro
    if not isinstance(lote, dict) or "avaliacoes" not in lote:
        raise ValueError("o arquivo precisa ter a chave 'avaliacoes'")
    lote.setdefault("talhoes", [])
    return lote


def gravar_rejeitados_txt(rejeitados: list) -> str:
    """
    Funcao: grava em TXT os registros recusados na importacao.
    rejeitados -> lista de tuplas (identificacao, lista_de_erros)
    """
    caminho = os.path.join(DIR_SAIDA, f"rejeitados_{_carimbo()}.txt")
    _garantir_pasta(caminho)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("REGISTROS RECUSADOS NA IMPORTACAO DE COLETA DE CAMPO\n")
        arquivo.write("=" * 60 + "\n")
        for identificacao, erros in rejeitados:
            arquivo.write(f"\n{identificacao}\n")
            for erro in erros:
                arquivo.write(f"  - {erro}\n")
    return caminho
