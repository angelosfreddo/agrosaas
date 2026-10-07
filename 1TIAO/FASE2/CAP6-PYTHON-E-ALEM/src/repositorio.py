"""
repositorio.py
--------------
Camada que une TABELA DE MEMORIA + ARQUIVO JSON + BANCO ORACLE.

Arquitetura "offline-first" (pensada para a realidade do campo, onde muitas
vezes nao ha sinal de internet no talhao):

    +-------------------+      grava sempre      +----------------------+
    | Tabela de memoria | ---------------------> | data/base_local.json |
    | (lista de dicts)  |                        +----------------------+
    +-------------------+
             |  se conectado, grava na hora (write-through)
             v
    +-------------------+
    |   ORACLE (FIAP)   |  <-- registros feitos offline ficam marcados como
    +-------------------+      "sincronizado": False e sobem na opcao
                               "Sincronizar pendencias".

O "contexto" (ctx) e um DICIONARIO passado por parametro para todas as
rotinas, contendo conexao, parametros e as tabelas de memoria.
"""

import random
from datetime import datetime

import arquivos
import banco_oracle


# ===========================================================================
# CONTEXTO
# ===========================================================================
def iniciar_contexto(parametros: dict) -> dict:
    """Funcao: cria o contexto da aplicacao a partir da base local."""
    base = arquivos.carregar_base_local()
    return {
        "parametros": parametros,
        "conn": None,
        "usuario_oracle": "",
        "talhoes": base["talhoes"],              # TABELA DE MEMORIA 1
        "avaliacoes": base["avaliacoes"],        # TABELA DE MEMORIA 2
        "exclusoes_pendentes": base["exclusoes_pendentes"],
    }


def online(ctx: dict) -> bool:
    """Funcao: indica se ha conexao ativa com o Oracle."""
    return ctx["conn"] is not None


def descricao_modo(ctx: dict) -> str:
    """Funcao: texto do modo atual para o cabecalho."""
    if online(ctx):
        return f"ONLINE - Oracle ({ctx['usuario_oracle']})"
    return "OFFLINE - base local JSON"


def persistir_local(ctx: dict) -> None:
    """Procedimento: grava as tabelas de memoria no JSON local."""
    arquivos.salvar_base_local({
        "talhoes": ctx["talhoes"],
        "avaliacoes": ctx["avaliacoes"],
        "exclusoes_pendentes": ctx["exclusoes_pendentes"],
    })


def gerar_cod_avaliacao() -> str:
    """Funcao: codigo unico gerado no dispositivo (funciona offline)."""
    agora = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"AV{agora}{random.randint(100, 999)}"


# ===========================================================================
# CONEXAO E SINCRONIZACAO
# ===========================================================================
def conectar_oracle(ctx: dict, usuario: str, senha: str, dsn: str) -> dict:
    """
    Funcao: conecta, cria tabelas se preciso, envia pendencias locais e
    recarrega a tabela de memoria com o conteudo oficial do banco.
    Devolve um resumo (dict). Levanta RuntimeError se nao conectar.
    """
    conn = banco_oracle.conectar(usuario, senha, dsn)
    ctx["conn"] = conn
    ctx["usuario_oracle"] = usuario.upper()
    criadas = banco_oracle.criar_estrutura(conn)
    enviados, falhas = sincronizar(ctx)
    recarregar_do_oracle(ctx)
    arquivos.registrar_log(f"CONEXAO ORACLE usuario={usuario.upper()} dsn={dsn} "
                           f"tabelas_criadas={criadas} sincronizados={enviados}")
    return {"tabelas_criadas": criadas, "enviados": enviados, "falhas": falhas}


def desconectar_oracle(ctx: dict) -> None:
    """Procedimento: encerra a conexao e passa para o modo offline."""
    banco_oracle.desconectar(ctx["conn"])
    ctx["conn"] = None
    ctx["usuario_oracle"] = ""


def recarregar_do_oracle(ctx: dict) -> None:
    """
    Procedimento: substitui a tabela de memoria pelos dados do Oracle,
    preservando os registros locais que ainda nao subiram.
    """
    talhoes_bd = banco_oracle.listar_talhoes(ctx["conn"])
    avaliacoes_bd = banco_oracle.listar_avaliacoes(ctx["conn"])
    for registro in talhoes_bd + avaliacoes_bd:
        registro["sincronizado"] = True

    codigos_bd = {t["codigo"] for t in talhoes_bd}
    cods_av_bd = {a["cod_avaliacao"] for a in avaliacoes_bd}
    pend_talhoes = [t for t in ctx["talhoes"]
                    if not t.get("sincronizado") and t["codigo"] not in codigos_bd]
    pend_avaliacoes = [a for a in ctx["avaliacoes"]
                       if not a.get("sincronizado") and a["cod_avaliacao"] not in cods_av_bd]

    ctx["talhoes"] = sorted(talhoes_bd + pend_talhoes, key=lambda t: t["codigo"])
    ctx["avaliacoes"] = avaliacoes_bd + pend_avaliacoes
    persistir_local(ctx)


def contar_pendencias(ctx: dict) -> dict:
    """Funcao: quantidade de operacoes aguardando envio ao Oracle."""
    return {
        "talhoes": sum(1 for t in ctx["talhoes"] if not t.get("sincronizado")),
        "avaliacoes": sum(1 for a in ctx["avaliacoes"] if not a.get("sincronizado")),
        "exclusoes": (len(ctx["exclusoes_pendentes"]["talhoes"])
                      + len(ctx["exclusoes_pendentes"]["avaliacoes"])),
    }


def sincronizar(ctx: dict) -> tuple:
    """
    Funcao: envia ao Oracle tudo o que foi feito offline.
    Ordem respeita a chave estrangeira: exclui avaliacoes -> grava talhoes
    -> grava avaliacoes -> exclui talhoes.
    Devolve TUPLA (quantidade_enviada, lista_de_falhas).
    """
    if not online(ctx):
        return 0, ["sem conexao com o Oracle"]
    conn = ctx["conn"]
    enviados = 0
    falhas = []
    exclusoes = ctx["exclusoes_pendentes"]

    for cod in list(exclusoes["avaliacoes"]):
        try:
            banco_oracle.excluir_avaliacao(conn, cod)
            exclusoes["avaliacoes"].remove(cod)
            enviados += 1
        except Exception as erro:
            falhas.append(f"exclusao avaliacao {cod}: {erro}")

    for talhao in ctx["talhoes"]:
        if not talhao.get("sincronizado"):
            try:
                banco_oracle.salvar_talhao(conn, talhao)
                talhao["sincronizado"] = True
                enviados += 1
            except Exception as erro:
                falhas.append(f"talhao {talhao['codigo']}: {erro}")

    for avaliacao in ctx["avaliacoes"]:
        if not avaliacao.get("sincronizado"):
            try:
                if not banco_oracle.existe_avaliacao(conn, avaliacao["cod_avaliacao"]):
                    banco_oracle.inserir_avaliacao(conn, avaliacao)
                avaliacao["sincronizado"] = True
                enviados += 1
            except Exception as erro:
                falhas.append(f"avaliacao {avaliacao['cod_avaliacao']}: {erro}")

    for codigo in list(exclusoes["talhoes"]):
        try:
            banco_oracle.excluir_talhao(conn, codigo)
            exclusoes["talhoes"].remove(codigo)
            enviados += 1
        except Exception as erro:
            falhas.append(f"exclusao talhao {codigo}: {erro}")

    persistir_local(ctx)
    if enviados:
        arquivos.registrar_log(f"SINCRONIZACAO enviados={enviados} falhas={len(falhas)}")
    return enviados, falhas


# ===========================================================================
# OPERACOES DE TALHAO
# ===========================================================================
def buscar_talhao(ctx: dict, codigo: str):
    """Funcao: devolve o dicionario do talhao ou None."""
    for talhao in ctx["talhoes"]:
        if talhao["codigo"] == codigo:
            return talhao
    return None


def avaliacoes_do_talhao(ctx: dict, codigo: str) -> list:
    """Funcao: filtra a tabela de memoria de avaliacoes por talhao."""
    return [a for a in ctx["avaliacoes"] if a["codigo_talhao"] == codigo]


def salvar_talhao(ctx: dict, talhao: dict) -> str:
    """
    Funcao: inclui ou altera um talhao na memoria, no JSON e no Oracle.
    Devolve 'ORACLE' se gravou no banco ou 'PENDENTE' se ficou offline.
    """
    talhao["sincronizado"] = False
    existente = buscar_talhao(ctx, talhao["codigo"])
    if existente is None:
        ctx["talhoes"].append(talhao)
        ctx["talhoes"].sort(key=lambda t: t["codigo"])
        operacao = "INCLUSAO"
    else:
        existente.update(talhao)
        talhao = existente
        operacao = "ALTERACAO"
    if talhao["codigo"] in ctx["exclusoes_pendentes"]["talhoes"]:
        ctx["exclusoes_pendentes"]["talhoes"].remove(talhao["codigo"])

    status = "PENDENTE"
    if online(ctx):
        try:
            banco_oracle.salvar_talhao(ctx["conn"], talhao)
            talhao["sincronizado"] = True
            status = "ORACLE"
        except Exception as erro:
            arquivos.registrar_log(f"ERRO ORACLE talhao {talhao['codigo']}: {erro}")
    persistir_local(ctx)
    arquivos.registrar_log(f"TALHAO {operacao} {talhao['codigo']} destino={status}")
    return status


def excluir_talhao(ctx: dict, codigo: str) -> tuple:
    """
    Funcao: exclui o talhao se NAO houver avaliacoes ligadas a ele
    (mesma regra da chave estrangeira do banco). Devolve (ok, mensagem).
    """
    talhao = buscar_talhao(ctx, codigo)
    if talhao is None:
        return False, f"talhao {codigo} nao encontrado"
    vinculadas = avaliacoes_do_talhao(ctx, codigo)
    if vinculadas:
        return False, (f"talhao {codigo} possui {len(vinculadas)} avaliacao(oes). "
                       "Exclua as avaliacoes antes.")

    ctx["talhoes"].remove(talhao)
    destino = "LOCAL"
    if talhao.get("sincronizado"):
        destino = "PENDENTE"
        if online(ctx):
            try:
                banco_oracle.excluir_talhao(ctx["conn"], codigo)
                destino = "ORACLE"
            except Exception as erro:
                arquivos.registrar_log(f"ERRO ORACLE exclusao talhao {codigo}: {erro}")
        if destino == "PENDENTE":
            ctx["exclusoes_pendentes"]["talhoes"].append(codigo)
    persistir_local(ctx)
    arquivos.registrar_log(f"TALHAO EXCLUSAO {codigo} destino={destino}")
    return True, f"talhao {codigo} excluido ({destino})"


# ===========================================================================
# OPERACOES DE AVALIACAO
# ===========================================================================
def buscar_avaliacao(ctx: dict, cod_avaliacao: str):
    """Funcao: devolve o dicionario da avaliacao ou None."""
    for avaliacao in ctx["avaliacoes"]:
        if avaliacao["cod_avaliacao"] == cod_avaliacao:
            return avaliacao
    return None


def adicionar_avaliacao(ctx: dict, avaliacao: dict) -> str:
    """Funcao: grava uma avaliacao processada. Devolve 'ORACLE' ou 'PENDENTE'."""
    avaliacao["sincronizado"] = False
    ctx["avaliacoes"].append(avaliacao)
    status = "PENDENTE"
    if online(ctx):
        try:
            banco_oracle.inserir_avaliacao(ctx["conn"], avaliacao)
            avaliacao["sincronizado"] = True
            status = "ORACLE"
        except Exception as erro:
            arquivos.registrar_log(
                f"ERRO ORACLE avaliacao {avaliacao['cod_avaliacao']}: {erro}")
    persistir_local(ctx)
    arquivos.registrar_log(
        f"AVALIACAO INCLUSAO {avaliacao['cod_avaliacao']} talhao={avaliacao['codigo_talhao']} "
        f"perda={avaliacao['perda_pct']}% destino={status}")
    return status


def excluir_avaliacao(ctx: dict, cod_avaliacao: str) -> tuple:
    """Funcao: exclui uma avaliacao. Devolve (ok, mensagem)."""
    avaliacao = buscar_avaliacao(ctx, cod_avaliacao)
    if avaliacao is None:
        return False, f"avaliacao {cod_avaliacao} nao encontrada"
    ctx["avaliacoes"].remove(avaliacao)
    destino = "LOCAL"
    if avaliacao.get("sincronizado"):
        destino = "PENDENTE"
        if online(ctx):
            try:
                banco_oracle.excluir_avaliacao(ctx["conn"], cod_avaliacao)
                destino = "ORACLE"
            except Exception as erro:
                arquivos.registrar_log(f"ERRO ORACLE exclusao {cod_avaliacao}: {erro}")
        if destino == "PENDENTE":
            ctx["exclusoes_pendentes"]["avaliacoes"].append(cod_avaliacao)
    persistir_local(ctx)
    arquivos.registrar_log(f"AVALIACAO EXCLUSAO {cod_avaliacao} destino={destino}")
    return True, f"avaliacao {cod_avaliacao} excluida ({destino})"
