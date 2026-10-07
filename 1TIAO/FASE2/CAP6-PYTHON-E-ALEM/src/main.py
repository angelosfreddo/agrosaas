"""
PerdaZero - Gestao de perdas na colheita da cana-de-acucar
==========================================================
FIAP - Fase 2 - Gestao do agronegocio em Python (Capitulos 3 a 6)

Problema tratado: na colheita mecanizada da cana as perdas podem chegar a
15% da producao (SOCICANA), contra cerca de 5% na colheita manual. O
produtor raramente sabe QUANTO perde, ONDE perde e POR QUE perde.

Solucao: um sistema de terminal que registra as amostragens de perda feitas
apos a colhedora, calcula perda em t/ha, % e R$ (modelo ATR), classifica,
DIAGNOSTICA a causa provavel pela composicao da perda, simula o ganho de
atingir a meta e consolida tudo em um painel gerencial. Os dados ficam em
tabelas de memoria, sao espelhados em JSON (funciona offline no campo) e
gravados no Oracle quando ha conexao.

Execucao:  python src/main.py
"""

import getpass
import os
import sys

import arquivos
import banco_oracle
import calculos
import repositorio as repo
from interface import (barra, cabecalho, campo, cor, cor_classe, formatar_data_br,
                       formatar_moeda, formatar_numero, imprimir_tabela,
                       limpar_tela, linha, mensagem_aviso, mensagem_erro,
                       mensagem_ok, pausar, secao, COR_CLASSE)
from validacao import (confirmar, ler_codigo, ler_data, ler_float, ler_inteiro,
                       ler_opcao, ler_texto)

NOME_SISTEMA = "PerdaZero"
SUBTITULO = "Gestao de perdas na colheita da cana-de-acucar"


# ===========================================================================
# FUNCOES AUXILIARES DE TELA
# ===========================================================================
def tela(ctx: dict, titulo: str) -> None:
    """Procedimento: limpa a tela e mostra cabecalho com o modo atual."""
    limpar_tela()
    pend = repo.contar_pendencias(ctx)
    total_pend = pend["talhoes"] + pend["avaliacoes"] + pend["exclusoes"]
    modo = repo.descricao_modo(ctx)
    status = f"{modo} | Pendencias de sincronizacao: {total_pend}"
    cabecalho(f"{NOME_SISTEMA} - {titulo}", status)


def ler_menu(opcoes_validas: tuple) -> str:
    """Funcao: le a opcao do menu, aceitando apenas as opcoes listadas."""
    while True:
        escolha = input("\n  Escolha -> ").strip()
        if escolha in opcoes_validas:
            return escolha
        mensagem_erro(f"opcao invalida. Digite uma destas: {', '.join(opcoes_validas)}")


def celula_classe(classe: str) -> tuple:
    """Funcao: celula colorida (valor, cor) para a tabela."""
    return (classe, COR_CLASSE.get(classe, "reset"))


def selo_sync(registro: dict) -> str:
    """Funcao: indicador visual de sincronizacao com o Oracle."""
    return "BD" if registro.get("sincronizado") else "LOC"


# ===========================================================================
# 1. TALHOES
# ===========================================================================
def listar_talhoes(ctx: dict) -> None:
    """Procedimento: exibe a tabela de talhoes."""
    colunas = (("Codigo", 8, "<"), ("Fazenda", 22, "<"), ("Area ha", 9, ">"),
               ("Variedade", 12, "<"), ("Corte", 5, ">"), ("t/ha", 7, ">"),
               ("Aval.", 5, ">"), ("Sync", 4, "^"))
    linhas = []
    for t in ctx["talhoes"]:
        linhas.append((t["codigo"], t["fazenda"], formatar_numero(t["area_ha"]),
                       t["variedade"], f"{t['estagio_corte']}o",
                       formatar_numero(t["produtividade_t_ha"], 1),
                       len(repo.avaliacoes_do_talhao(ctx, t["codigo"])),
                       selo_sync(t)))
    imprimir_tabela(colunas, linhas)


def formulario_talhao(parametros: dict, atual=None) -> dict:
    """
    Funcao: le os dados de um talhao com consistencia.
    Se 'atual' for informado (alteracao), ENTER mantem o valor atual.
    """
    padrao_prod = parametros["agronomia"]["produtividade_padrao_t_ha"]
    atual = atual or {}
    return {
        "fazenda": ler_texto("Fazenda", 2, 60, padrao=atual.get("fazenda")),
        "area_ha": ler_float("Area do talhao (ha)", 0.1, 100000,
                             padrao=atual.get("area_ha")),
        "variedade": ler_texto("Variedade (ex.: RB867515)", 2, 30,
                               padrao=atual.get("variedade")),
        "estagio_corte": ler_inteiro("Estagio de corte (1 = cana planta)", 1, 15,
                                     padrao=atual.get("estagio_corte")),
        "produtividade_t_ha": ler_float("Produtividade estimada (t/ha)", 10, 250,
                                        padrao=atual.get("produtividade_t_ha", padrao_prod)),
    }


def cadastrar_talhao(ctx: dict) -> None:
    """Procedimento: inclusao de talhao."""
    tela(ctx, "Cadastrar talhao")
    codigo = ler_codigo("Codigo do talhao (ex.: T-01)")
    if repo.buscar_talhao(ctx, codigo):
        mensagem_erro(f"o talhao {codigo} ja existe. Use a opcao Alterar.")
        return
    talhao = formulario_talhao(ctx["parametros"])
    talhao["codigo"] = codigo
    destino = repo.salvar_talhao(ctx, talhao)
    mensagem_ok(f"talhao {codigo} gravado ({'Oracle' if destino == 'ORACLE' else 'base local - pendente de sincronizacao'}).")


def alterar_talhao(ctx: dict) -> None:
    """Procedimento: alteracao de talhao (ENTER mantem o valor atual)."""
    tela(ctx, "Alterar talhao")
    listar_talhoes(ctx)
    if not ctx["talhoes"]:
        return
    codigo = ler_codigo("\n  Codigo do talhao a alterar")
    talhao = repo.buscar_talhao(ctx, codigo)
    if talhao is None:
        mensagem_erro(f"talhao {codigo} nao encontrado.")
        return
    print(cor("  (pressione ENTER para manter o valor entre colchetes)", "cinza"))
    novos = formulario_talhao(ctx["parametros"], talhao)
    novos["codigo"] = codigo
    destino = repo.salvar_talhao(ctx, novos)
    mensagem_ok(f"talhao {codigo} atualizado ({destino}).")
    mensagem_aviso("avaliacoes ja registradas mantem os valores calculados na data do laudo.")


def excluir_talhao(ctx: dict) -> None:
    """Procedimento: exclusao de talhao com confirmacao."""
    tela(ctx, "Excluir talhao")
    listar_talhoes(ctx)
    if not ctx["talhoes"]:
        return
    codigo = ler_codigo("\n  Codigo do talhao a excluir")
    if repo.buscar_talhao(ctx, codigo) is None:
        mensagem_erro(f"talhao {codigo} nao encontrado.")
        return
    if confirmar(f"Confirma a exclusao do talhao {codigo}?"):
        ok, mensagem = repo.excluir_talhao(ctx, codigo)
        if ok:
            mensagem_ok(mensagem)
        else:
            mensagem_erro(mensagem)
    else:
        mensagem_aviso("operacao cancelada.")


def menu_talhoes(ctx: dict) -> None:
    """Procedimento: submenu de talhoes."""
    while True:
        tela(ctx, "Talhoes")
        print("""
  [1] Cadastrar talhao
  [2] Listar talhoes
  [3] Alterar talhao
  [4] Excluir talhao
  [0] Voltar""")
        match ler_menu(("1", "2", "3", "4", "0")):
            case "1":
                cadastrar_talhao(ctx)
            case "2":
                tela(ctx, "Talhoes cadastrados")
                listar_talhoes(ctx)
            case "3":
                alterar_talhao(ctx)
            case "4":
                excluir_talhao(ctx)
            case "0":
                return
        pausar()


# ===========================================================================
# 2. REGISTRO DE AVALIACAO
# ===========================================================================
def exibir_resultado(ctx: dict, avaliacao: dict, talhao: dict) -> None:
    """Procedimento: mostra indicadores, composicao, diagnostico e simulacao."""
    parametros = ctx["parametros"]
    meta = parametros["metas"]["meta_perda_pct"]

    secao("Resultado da avaliacao")
    campo("Talhao", f"{talhao['codigo']} - {talhao['fazenda']} ({formatar_numero(talhao['area_ha'])} ha)")
    campo("Data", formatar_data_br(avaliacao["data_avaliacao"]))
    operacao = avaliacao["tipo_colheita"]
    if avaliacao.get("colhedora"):
        operacao += f" | {avaliacao['colhedora']} | {formatar_numero(avaliacao['velocidade_kmh'], 1)} km/h"
    campo("Operacao", f"{operacao} | turno {avaliacao['turno']}")
    campo("Cana recolhida", f"{formatar_numero(avaliacao['kg_total'])} kg em "
                            f"{formatar_numero(avaliacao['area_amostrada_m2'], 1)} m2")
    campo("Perda", f"{formatar_numero(avaliacao['perda_t_ha'], 3)} t/ha")
    campo("Perda percentual", f"{formatar_numero(avaliacao['perda_pct'])} %  (meta: {formatar_numero(meta, 1)} %)")
    campo("Classificacao", cor_classe(avaliacao["classificacao"]))
    campo("Prejuizo estimado no talhao", cor(formatar_moeda(avaliacao["prejuizo_rs"]), "negrito"))

    secao("Composicao da perda (onde a cana ficou)")
    composicao = calculos.composicao_perdas(avaliacao["amostras"])
    for tipo in calculos.TIPOS_PERDA:
        participacao = composicao[tipo]
        print(f"  {calculos.ROTULOS_PERDA[tipo]:<28} {participacao:5.1f}% "
              f"{cor(barra(participacao, 100, 30), 'ciano')}")

    secao("Diagnostico e recomendacoes")
    for prioridade, titulo, causa, acao in calculos.diagnosticar(avaliacao, parametros):
        print(cor(f"  {prioridade}. {titulo}", "negrito"))
        print(f"     Causa provavel: {causa}")
        print(cor(f"     Acao..........: {acao}", "verde"))

    simulacao = calculos.simular_meta(avaliacao, talhao, meta, parametros)
    secao("Quanto volta para o bolso se atingir a meta")
    if simulacao["ganho_rs"] > 0:
        print(f"  Reduzindo a perda de {formatar_numero(simulacao['perda_atual_t_ha'], 2)} para "
              f"{formatar_numero(simulacao['perda_meta_t_ha'], 2)} t/ha, o talhao recupera "
              f"{formatar_numero(simulacao['toneladas_recuperadas'])} t de cana:")
        print(cor(f"  {formatar_moeda(simulacao['ganho_rs'])} a mais por safra.", "verde"))
    else:
        print(cor("  Talhao ja esta dentro da meta. Mantenha a regulagem.", "verde"))


def registrar_avaliacao(ctx: dict) -> None:
    """Procedimento: fluxo completo de coleta, calculo, diagnostico e gravacao."""
    parametros = ctx["parametros"]
    tela(ctx, "Registrar avaliacao de perdas")
    if not ctx["talhoes"]:
        mensagem_aviso("cadastre um talhao antes (menu 1) ou importe a coleta de exemplo (menu 6).")
        return

    listar_talhoes(ctx)
    print()
    while True:
        codigo = ler_codigo("Codigo do talhao avaliado")
        talhao = repo.buscar_talhao(ctx, codigo)
        if talhao:
            break
        mensagem_erro(f"talhao {codigo} nao cadastrado.")

    secao("Operacao de colheita")
    avaliacao = {
        "cod_avaliacao": repo.gerar_cod_avaliacao(),
        "codigo_talhao": codigo,
        "data_avaliacao": ler_data("Data da avaliacao"),
        "tipo_colheita": ler_opcao("Tipo de colheita", calculos.TIPOS_COLHEITA, padrao="MECANIZADA"),
    }
    if avaliacao["tipo_colheita"] == "MECANIZADA":
        avaliacao["colhedora"] = ler_codigo("Identificacao da colhedora (ex.: CH-03)", 20)
        avaliacao["operador"] = ler_texto("Nome do operador", 2, 60)
        avaliacao["velocidade_kmh"] = ler_float("Velocidade media de colheita (km/h)", 0.5, 15)
    else:
        avaliacao["colhedora"] = None
        avaliacao["velocidade_kmh"] = None
        avaliacao["operador"] = ler_texto("Equipe/encarregado", 2, 60, padrao="Equipe manual")
    avaliacao["turno"] = ler_opcao("Turno", calculos.TURNOS, padrao="DIURNO")

    secao("Amostragem no campo")
    area_ponto = parametros["agronomia"]["area_padrao_ponto_m2"]
    pontos = ler_inteiro("Quantidade de pontos amostrados", 1, 50, padrao=5)
    area_ponto = ler_float("Area de cada ponto/moldura (m2)", 1, 100, padrao=area_ponto)
    avaliacao["pontos_amostrados"] = pontos
    avaliacao["area_amostrada_m2"] = round(pontos * area_ponto, 2)

    print(cor("  Informe o TOTAL em kg recolhido em todos os pontos, por tipo de perda:", "cinza"))
    amostras = {}
    for tipo in calculos.TIPOS_PERDA:
        amostras[tipo] = ler_float(f"  {calculos.ROTULOS_PERDA[tipo]:<28} kg", 0, 5000, padrao=0)
    avaliacao["amostras"] = amostras

    if calculos.calcular_kg_total(amostras) == 0:
        mensagem_aviso("nenhuma perda informada: a avaliacao sera registrada com perda zero.")

    avaliacao = calculos.processar_avaliacao(avaliacao, talhao, parametros)
    tela(ctx, "Resultado da avaliacao")
    exibir_resultado(ctx, avaliacao, talhao)

    print()
    linha()
    if confirmar("Gravar esta avaliacao?"):
        destino = repo.adicionar_avaliacao(ctx, avaliacao)
        mensagem_ok(f"avaliacao {avaliacao['cod_avaliacao']} gravada "
                    f"({'Oracle' if destino == 'ORACLE' else 'base local - pendente de sincronizacao'}).")
        if confirmar("Gerar laudo tecnico em TXT?"):
            caminho = gerar_laudo(ctx, avaliacao, talhao)
            mensagem_ok(f"laudo gerado em: {caminho}")
    else:
        mensagem_aviso("avaliacao descartada.")


# ===========================================================================
# 3. CONSULTA DE AVALIACOES
# ===========================================================================
def listar_avaliacoes(lista: list) -> None:
    """Procedimento: tabela numerada de avaliacoes."""
    colunas = (("No", 3, ">"), ("Data", 10, "<"), ("Talhao", 6, "<"),
               ("Colhedora", 9, "<"), ("Turno", 7, "<"), ("Perda %", 7, ">"),
               ("Classe", 8, "<"), ("Prejuizo", 14, ">"), ("Sync", 4, "^"))
    linhas = []
    for numero, a in enumerate(lista, start=1):
        linhas.append((numero, formatar_data_br(a["data_avaliacao"]), a["codigo_talhao"],
                       a.get("colhedora") or "MANUAL", a["turno"],
                       formatar_numero(a["perda_pct"]), celula_classe(a["classificacao"]),
                       formatar_moeda(a["prejuizo_rs"]), selo_sync(a)))
    imprimir_tabela(colunas, linhas)


def escolher_avaliacao(lista: list):
    """Funcao: usuario escolhe uma avaliacao pelo numero da lista."""
    if not lista:
        return None
    numero = ler_inteiro("Numero da avaliacao (0 = cancelar)", 0, len(lista))
    if numero == 0:
        return None
    return lista[numero - 1]


def menu_consultas(ctx: dict) -> None:
    """Procedimento: submenu de consulta, filtro, detalhe e exclusao."""
    filtro_texto = "todas"
    lista = list(ctx["avaliacoes"])
    while True:
        tela(ctx, "Consultar avaliacoes")
        print(f"  Filtro atual: {cor(filtro_texto, 'ciano')} ({len(lista)} registro(s))\n")
        listar_avaliacoes(lista)
        print("""
  [1] Detalhar avaliacao (com diagnostico)
  [2] Filtrar por talhao
  [3] Filtrar por classificacao
  [4] Filtrar acima da meta
  [5] Limpar filtro
  [6] Excluir avaliacao
  [0] Voltar""")
        match ler_menu(("1", "2", "3", "4", "5", "6", "0")):
            case "1":
                avaliacao = escolher_avaliacao(lista)
                if avaliacao:
                    talhao = repo.buscar_talhao(ctx, avaliacao["codigo_talhao"])
                    tela(ctx, f"Avaliacao {avaliacao['cod_avaliacao']}")
                    exibir_resultado(ctx, avaliacao, talhao)
                    pausar()
            case "2":
                codigo = ler_codigo("Codigo do talhao")
                lista = repo.avaliacoes_do_talhao(ctx, codigo)
                filtro_texto = f"talhao {codigo}"
            case "3":
                classe = ler_opcao("Classificacao", calculos.CLASSES_PERDA)
                lista = [a for a in ctx["avaliacoes"] if a["classificacao"] == classe]
                filtro_texto = f"classificacao {classe}"
            case "4":
                meta = ctx["parametros"]["metas"]["meta_perda_pct"]
                lista = [a for a in ctx["avaliacoes"] if a["perda_pct"] > meta]
                filtro_texto = f"perda acima da meta de {formatar_numero(meta, 1)}%"
            case "5":
                lista = list(ctx["avaliacoes"])
                filtro_texto = "todas"
            case "6":
                avaliacao = escolher_avaliacao(lista)
                if avaliacao and confirmar(f"Excluir a avaliacao {avaliacao['cod_avaliacao']}?"):
                    ok, mensagem = repo.excluir_avaliacao(ctx, avaliacao["cod_avaliacao"])
                    (mensagem_ok if ok else mensagem_erro)(mensagem)
                    lista = [a for a in lista if a is not avaliacao]
                    pausar()
            case "0":
                return


# ===========================================================================
# 4. PAINEL GERENCIAL
# ===========================================================================
def gerar_resumo(ctx: dict) -> dict:
    """Funcao: indicadores consolidados (usado no painel e na exportacao)."""
    avaliacoes = ctx["avaliacoes"]
    meta = ctx["parametros"]["metas"]["meta_perda_pct"]
    estat = calculos.estatisticas([a["perda_pct"] for a in avaliacoes])
    acima = sum(1 for a in avaliacoes if a["perda_pct"] > meta)
    return {
        "avaliacoes": estat["qtd"],
        "perda_media_pct": estat["media"],
        "perda_min_pct": estat["minimo"],
        "perda_max_pct": estat["maximo"],
        "perda_media_t_ha": calculos.estatisticas([a["perda_t_ha"] for a in avaliacoes])["media"],
        "prejuizo_total_rs": round(sum(a["prejuizo_rs"] for a in avaliacoes), 2),
        "acima_da_meta": acima,
        "meta_pct": meta,
    }


def imprimir_ranking(titulo: str, ranking: list, maior_media: float) -> None:
    """Procedimento: imprime um ranking (lista de tuplas) com barras."""
    secao(titulo)
    colunas = (("Grupo", 12, "<"), ("Aval.", 5, ">"), ("Perda %", 7, ">"),
               ("Prejuizo", 15, ">"), ("", 24, "<"))
    linhas = []
    for grupo, media, qtd, prejuizo in ranking:
        linhas.append((grupo, qtd, formatar_numero(media), formatar_moeda(prejuizo),
                       (barra(media, maior_media, 24), "ciano")))
    imprimir_tabela(colunas, linhas)


def gerar_insights(ctx: dict, resumo: dict) -> list:
    """Funcao: frases automaticas de apoio a decisao (lista de strings)."""
    avaliacoes = ctx["avaliacoes"]
    insights = []

    composicao = calculos.composicao_geral(avaliacoes)
    total_kg = sum(composicao.values())
    if total_kg > 0:
        tipo_vilao = max(composicao, key=composicao.get)
        participacao = composicao[tipo_vilao] / total_kg * 100
        causa, acao = calculos.BASE_CONHECIMENTO[tipo_vilao]
        insights.append(f"Principal tipo de perda da fazenda: {calculos.ROTULOS_PERDA[tipo_vilao]} "
                        f"({participacao:.1f}%). Foco: {acao}")

    turnos = {g: m for g, m, q, p in calculos.agrupar_media(avaliacoes, "turno")}
    if "DIURNO" in turnos and "NOTURNO" in turnos:
        diferenca = turnos["NOTURNO"] - turnos["DIURNO"]
        if abs(diferenca) >= 0.5:
            pior = "NOTURNO" if diferenca > 0 else "DIURNO"
            insights.append(f"O turno {pior} perde {abs(diferenca):.2f} p.p. a mais. "
                            "Avaliar iluminacao, fadiga e supervisao nesse turno.")

    mecanizadas = [a for a in avaliacoes if a["tipo_colheita"] == "MECANIZADA"]
    colhedoras = calculos.agrupar_media(mecanizadas, "colhedora")
    if colhedoras and resumo["prejuizo_total_rs"] > 0:
        pior = colhedoras[0]
        fatia = pior[3] / resumo["prejuizo_total_rs"] * 100
        insights.append(f"A colhedora {pior[0]} tem a maior perda media ({pior[1]:.2f}%) e "
                        f"responde por {fatia:.1f}% do prejuizo. Priorizar manutencao/regulagem.")

    vel_max = ctx["parametros"]["agronomia"]["velocidade_ideal_max_kmh"]
    rapidas = [a for a in mecanizadas if (a.get("velocidade_kmh") or 0) > vel_max]
    normais = [a for a in mecanizadas if 0 < (a.get("velocidade_kmh") or 0) <= vel_max]
    if rapidas and normais:
        media_rapidas = sum(a["perda_pct"] for a in rapidas) / len(rapidas)
        media_normais = sum(a["perda_pct"] for a in normais) / len(normais)
        insights.append(f"Acima de {vel_max:.1f} km/h a perda media foi {media_rapidas:.2f}% "
                        f"contra {media_normais:.2f}% na faixa ideal.")

    if resumo["acima_da_meta"] == 0 and avaliacoes:
        insights.append("Todas as avaliacoes estao dentro da meta. Parabens a equipe!")
    return insights


def painel_gerencial(ctx: dict) -> None:
    """Procedimento: dashboard consolidado em texto."""
    tela(ctx, "Painel gerencial")
    avaliacoes = ctx["avaliacoes"]
    if not avaliacoes:
        mensagem_aviso("nenhuma avaliacao registrada ainda.")
        return
    resumo = gerar_resumo(ctx)

    secao("Indicadores gerais")
    campo("Avaliacoes registradas", str(resumo["avaliacoes"]))
    campo("Perda media", f"{formatar_numero(resumo['perda_media_pct'])} %  "
                         f"(min {formatar_numero(resumo['perda_min_pct'])} | "
                         f"max {formatar_numero(resumo['perda_max_pct'])})")
    campo("Perda media por hectare", f"{formatar_numero(resumo['perda_media_t_ha'], 2)} t/ha")
    campo("Acima da meta", f"{resumo['acima_da_meta']} de {resumo['avaliacoes']} "
                           f"(meta {formatar_numero(resumo['meta_pct'], 1)} %)")
    campo("Prejuizo acumulado", cor(formatar_moeda(resumo["prejuizo_total_rs"]), "negrito"))

    secao("Distribuicao por classificacao")
    for classe in calculos.CLASSES_PERDA:
        qtd = sum(1 for a in avaliacoes if a["classificacao"] == classe)
        print(f"  {cor_classe(classe.ljust(9))} {str(qtd).rjust(3)} "
              f"{cor(barra(qtd, len(avaliacoes), 40), COR_CLASSE[classe])}")

    secao("Composicao geral da perda (kg recolhidos)")
    composicao = calculos.composicao_geral(avaliacoes)
    maior = max(composicao.values()) or 1
    for tipo in calculos.TIPOS_PERDA:
        print(f"  {calculos.ROTULOS_PERDA[tipo]:<28} {formatar_numero(composicao[tipo], 1):>9} kg "
              f"{cor(barra(composicao[tipo], maior, 25), 'ciano')}")

    por_talhao = calculos.agrupar_media(avaliacoes, "codigo_talhao")
    por_colhedora = calculos.agrupar_media(
        [a for a in avaliacoes if a["tipo_colheita"] == "MECANIZADA"], "colhedora")
    por_turno = calculos.agrupar_media(avaliacoes, "turno")
    maior_media = max([r[1] for r in por_talhao + por_colhedora + por_turno] or [1])

    imprimir_ranking("Ranking de talhoes (pior para melhor)", por_talhao[:5], maior_media)
    imprimir_ranking("Ranking de colhedoras", por_colhedora, maior_media)
    imprimir_ranking("Comparativo de turnos", por_turno, maior_media)

    secao("Insights automaticos")
    for numero, texto in enumerate(gerar_insights(ctx, resumo), start=1):
        print(f"  {numero}. {texto}")


# ===========================================================================
# 5. SIMULADOR
# ===========================================================================
def ultima_avaliacao_por_talhao(ctx: dict) -> dict:
    """Funcao: dicionario {codigo_talhao: avaliacao mais recente}."""
    ultimas = {}
    for avaliacao in ctx["avaliacoes"]:
        codigo = avaliacao["codigo_talhao"]
        if codigo not in ultimas or avaliacao["data_avaliacao"] >= ultimas[codigo]["data_avaliacao"]:
            ultimas[codigo] = avaliacao
    return ultimas


def simulador(ctx: dict) -> None:
    """Procedimento: 'e se' - ganho financeiro ao atingir uma meta de perda."""
    tela(ctx, "Simulador de ganho")
    ultimas = ultima_avaliacao_por_talhao(ctx)
    if not ultimas:
        mensagem_aviso("nenhuma avaliacao registrada ainda.")
        return
    print("  Considera a avaliacao MAIS RECENTE de cada talhao e calcula quanto")
    print("  dinheiro volta para o produtor se a perda cair para a meta informada.\n")
    meta_padrao = ctx["parametros"]["metas"]["meta_perda_pct"]
    meta = ler_float("Meta de perda a simular (%)", 0.5, 30, padrao=meta_padrao)

    colunas = (("Talhao", 7, "<"), ("Area ha", 9, ">"), ("Perda %", 8, ">"),
               ("Meta %", 7, ">"), ("t recuperadas", 13, ">"), ("Ganho/safra", 16, ">"))
    linhas = []
    total_t = 0.0
    total_rs = 0.0
    for codigo in sorted(ultimas):
        avaliacao = ultimas[codigo]
        talhao = repo.buscar_talhao(ctx, codigo)
        if talhao is None:
            continue
        sim = calculos.simular_meta(avaliacao, talhao, meta, ctx["parametros"])
        total_t += sim["toneladas_recuperadas"]
        total_rs += sim["ganho_rs"]
        ganho = (formatar_moeda(sim["ganho_rs"]), "verde") if sim["ganho_rs"] > 0 else ("dentro da meta", "cinza")
        linhas.append((codigo, formatar_numero(talhao["area_ha"]),
                       formatar_numero(avaliacao["perda_pct"]), formatar_numero(meta, 1),
                       formatar_numero(sim["toneladas_recuperadas"]), ganho))
    print()
    imprimir_tabela(colunas, linhas)
    linha()
    print(f"  Atingindo {formatar_numero(meta, 1)}% em todos os talhoes, a fazenda recupera "
          f"{cor(formatar_numero(total_t) + ' t', 'negrito')} de cana")
    print(f"  o equivalente a {cor(formatar_moeda(total_rs), 'verde')} por safra.")
    caminhoes = total_t / 60  # caminhao canavieiro (rodotrem) ~ 60 t
    if caminhoes >= 1:
        print(cor(f"  Isso equivale a aproximadamente {caminhoes:.0f} carga(s) de rodotrem que hoje ficam no chao.", "cinza"))


# ===========================================================================
# 6. ARQUIVOS
# ===========================================================================
def gerar_laudo(ctx: dict, avaliacao: dict, talhao: dict) -> str:
    """Funcao: monta diagnostico/simulacao e grava o laudo TXT."""
    parametros = ctx["parametros"]
    meta = parametros["metas"]["meta_perda_pct"]
    diagnostico = calculos.diagnosticar(avaliacao, parametros)
    simulacao = calculos.simular_meta(avaliacao, talhao, meta, parametros)
    caminho = arquivos.gerar_laudo_txt(avaliacao, talhao, diagnostico, simulacao, meta)
    arquivos.registrar_log(f"LAUDO TXT {avaliacao['cod_avaliacao']} -> {os.path.basename(caminho)}")
    return caminho


def importar_coleta(ctx: dict) -> None:
    """Procedimento: importa lote JSON do campo, validando registro a registro."""
    tela(ctx, "Importar coleta de campo (JSON)")
    print("  Simula o arquivo gerado pelo app/planilha da equipe de qualidade no campo.")
    print("  Cada registro passa pelas MESMAS regras de consistencia do teclado.\n")
    caminho = input(f"  Caminho do arquivo [{os.path.relpath(arquivos.ARQ_COLETA_EXEMPLO)}]: ").strip()
    caminho = caminho.strip('"') or arquivos.ARQ_COLETA_EXEMPLO
    try:
        lote = arquivos.ler_lote_campo(caminho)
    except ValueError as erro:
        mensagem_erro(str(erro))
        return

    rejeitados = []
    novos_talhoes = 0
    for indice, dados in enumerate(lote["talhoes"], start=1):
        ok, resultado = arquivos.validar_talhao_dict(dados)
        if not ok:
            rejeitados.append((f"talhao #{indice} ({dados.get('codigo')})", resultado))
        elif repo.buscar_talhao(ctx, resultado["codigo"]) is None:
            repo.salvar_talhao(ctx, resultado)
            novos_talhoes += 1

    codigos = {t["codigo"] for t in ctx["talhoes"]}
    novas = 0
    duplicadas = 0
    for indice, dados in enumerate(lote["avaliacoes"], start=1):
        cod_origem = dados.get("cod_avaliacao")
        if cod_origem and repo.buscar_avaliacao(ctx, cod_origem):
            duplicadas += 1
            continue
        ok, resultado = arquivos.validar_avaliacao_dict(dados, codigos)
        if not ok:
            rejeitados.append((f"avaliacao #{indice} (talhao {dados.get('codigo_talhao')})", resultado))
            continue
        resultado["cod_avaliacao"] = cod_origem or repo.gerar_cod_avaliacao()
        talhao = repo.buscar_talhao(ctx, resultado["codigo_talhao"])
        processada = calculos.processar_avaliacao(resultado, talhao, ctx["parametros"])
        repo.adicionar_avaliacao(ctx, processada)
        novas += 1

    secao("Resumo da importacao")
    campo("Origem", str(lote.get("origem", "nao informada")))
    campo("Talhoes novos", str(novos_talhoes))
    campo("Avaliacoes importadas", str(novas))
    campo("Ja existentes (ignoradas)", str(duplicadas))
    campo("Registros rejeitados", cor(str(len(rejeitados)), "vermelho" if rejeitados else "verde"))
    for identificacao, erros in rejeitados:
        print(cor(f"    - {identificacao}: {'; '.join(erros)}", "amarelo"))
    if rejeitados:
        caminho_rej = arquivos.gravar_rejeitados_txt(rejeitados)
        mensagem_aviso(f"detalhes dos rejeitados gravados em: {caminho_rej}")
    arquivos.registrar_log(f"IMPORTACAO {os.path.basename(caminho)} talhoes={novos_talhoes} "
                           f"avaliacoes={novas} rejeitados={len(rejeitados)}")


def menu_arquivos(ctx: dict) -> None:
    """Procedimento: submenu de arquivos texto e JSON."""
    while True:
        tela(ctx, "Arquivos (TXT e JSON)")
        print("""
  [1] Gerar laudo tecnico de uma avaliacao (TXT)
  [2] Exportar base completa com resumo (JSON)
  [3] Importar coleta de campo (JSON)
  [4] Ver ultimas linhas do log de operacoes (TXT)
  [0] Voltar""")
        match ler_menu(("1", "2", "3", "4", "0")):
            case "1":
                tela(ctx, "Gerar laudo TXT")
                listar_avaliacoes(ctx["avaliacoes"])
                avaliacao = escolher_avaliacao(ctx["avaliacoes"])
                if avaliacao:
                    talhao = repo.buscar_talhao(ctx, avaliacao["codigo_talhao"])
                    mensagem_ok(f"laudo gerado em: {gerar_laudo(ctx, avaliacao, talhao)}")
            case "2":
                caminho = arquivos.exportar_json(ctx["talhoes"], ctx["avaliacoes"], gerar_resumo(ctx))
                arquivos.registrar_log(f"EXPORTACAO JSON -> {os.path.basename(caminho)}")
                mensagem_ok(f"arquivo exportado em: {caminho}")
            case "3":
                importar_coleta(ctx)
            case "4":
                tela(ctx, "Log de operacoes")
                linhas_log = arquivos.ler_ultimas_linhas_log(20)
                for texto in linhas_log:
                    print(f"  {texto}")
                if not linhas_log:
                    print(cor("  (log vazio)", "cinza"))
            case "0":
                return
        pausar()


# ===========================================================================
# 7. ORACLE
# ===========================================================================
def conectar_interativo(ctx: dict) -> None:
    """Procedimento: solicita credenciais e conecta ao Oracle."""
    if not banco_oracle.DRIVER_OK:
        mensagem_erro("driver 'oracledb' indisponivel neste computador.")
        print(cor(f"  Detalhe: {banco_oracle.DRIVER_ERRO}", "cinza"))
        print("  Instale com: pip install oracledb   (o sistema segue em modo OFFLINE)")
        return
    dsn_padrao = os.environ.get("ORACLE_DSN") or ctx["parametros"]["oracle"]["dsn_padrao"]
    usuario = os.environ.get("ORACLE_USER") or ler_texto("Usuario Oracle (ex.: RM123456)", 2, 30)
    senha = os.environ.get("ORACLE_PASSWORD") or getpass.getpass("  Senha (nao aparece ao digitar): ")
    dsn = input(f"  DSN [{dsn_padrao}]: ").strip() or dsn_padrao
    print(cor("  Conectando...", "cinza"))
    try:
        resultado = repo.conectar_oracle(ctx, usuario, senha, dsn)
    except Exception as erro:
        repo.desconectar_oracle(ctx)
        mensagem_erro(str(erro))
        mensagem_aviso("seguindo em modo OFFLINE. Os dados continuam salvos no JSON local.")
        return
    mensagem_ok(f"conectado ao Oracle como {usuario.upper()}.")
    if resultado["tabelas_criadas"]:
        mensagem_ok(f"tabelas criadas: {', '.join(resultado['tabelas_criadas'])}")
    if resultado["enviados"]:
        mensagem_ok(f"{resultado['enviados']} pendencia(s) local(is) sincronizada(s).")
    for falha in resultado["falhas"]:
        mensagem_erro(falha)


def ranking_sql(ctx: dict) -> None:
    """Procedimento: ranking calculado pelo proprio Oracle (GROUP BY)."""
    tela(ctx, "Consulta analitica no Oracle")
    print(cor("  SELECT colhedora, COUNT(*), AVG(perda_pct), SUM(prejuizo_rs)", "cinza"))
    print(cor("    FROM PZ_AVALIACAO_PERDA GROUP BY colhedora ORDER BY 3 DESC\n", "cinza"))
    try:
        resultado = banco_oracle.consultar_ranking_sql(ctx["conn"])
    except Exception as erro:
        mensagem_erro(f"falha na consulta: {erro}")
        return
    colunas = (("Colhedora", 12, "<"), ("Aval.", 6, ">"), ("Perda media %", 13, ">"),
               ("Prejuizo total", 18, ">"))
    imprimir_tabela(colunas, [(c, q, formatar_numero(m), formatar_moeda(p)) for c, q, m, p in resultado])


def menu_oracle(ctx: dict) -> None:
    """Procedimento: submenu do banco de dados Oracle."""
    while True:
        tela(ctx, "Banco de dados Oracle")
        pend = repo.contar_pendencias(ctx)
        campo("Driver oracledb", "disponivel" if banco_oracle.DRIVER_OK else cor("indisponivel", "vermelho"))
        campo("Conexao", repo.descricao_modo(ctx))
        campo("Pendencias", f"{pend['talhoes']} talhao(oes), {pend['avaliacoes']} avaliacao(oes), "
                            f"{pend['exclusoes']} exclusao(oes)")
        print("""
  [1] Conectar ao Oracle
  [2] Sincronizar pendencias locais
  [3] Recarregar dados a partir do Oracle
  [4] Ranking de colhedoras calculado no Oracle (SQL GROUP BY)
  [5] Desconectar (trabalhar offline)
  [0] Voltar""")
        escolha = ler_menu(("1", "2", "3", "4", "5", "0"))
        if escolha in ("2", "3", "4", "5") and not repo.online(ctx):
            mensagem_erro("nao ha conexao ativa. Use a opcao 1 primeiro.")
            pausar()
            continue
        match escolha:
            case "1":
                conectar_interativo(ctx)
            case "2":
                enviados, falhas = repo.sincronizar(ctx)
                mensagem_ok(f"{enviados} operacao(oes) enviada(s) ao Oracle.")
                for falha in falhas:
                    mensagem_erro(falha)
            case "3":
                try:
                    repo.recarregar_do_oracle(ctx)
                    mensagem_ok(f"{len(ctx['talhoes'])} talhoes e {len(ctx['avaliacoes'])} avaliacoes carregados.")
                except Exception as erro:
                    mensagem_erro(f"falha ao recarregar: {erro}")
            case "4":
                ranking_sql(ctx)
            case "5":
                repo.desconectar_oracle(ctx)
                mensagem_ok("desconectado. Novos registros ficarao pendentes no JSON local.")
            case "0":
                return
        pausar()


# ===========================================================================
# 8. PARAMETROS
# ===========================================================================
def menu_parametros(ctx: dict) -> None:
    """Procedimento: consulta e altera config/parametros.json."""
    parametros = ctx["parametros"]
    while True:
        tela(ctx, "Parametros (config/parametros.json)")
        economia = parametros["economia"]
        agronomia = parametros["agronomia"]
        metas = parametros["metas"]
        campo("[1] Preco do kg de ATR", formatar_moeda(economia["preco_kg_atr_rs"]))
        campo("[2] ATR medio da cana", f"{formatar_numero(economia['atr_medio_kg_t'], 1)} kg/t")
        campo("[3] Meta de perda", f"{formatar_numero(metas['meta_perda_pct'], 1)} %")
        campo("[4] Produtividade padrao", f"{formatar_numero(agronomia['produtividade_padrao_t_ha'], 1)} t/ha")
        campo("[5] Velocidade ideal", f"{formatar_numero(agronomia['velocidade_ideal_min_kmh'], 1)} a "
                                      f"{formatar_numero(agronomia['velocidade_ideal_max_kmh'], 1)} km/h")
        faixas = metas["faixas_classificacao_pct"]
        campo("    Faixas de classificacao", f"BAIXA <= {faixas[0]} | MODERADA <= {faixas[1]} | "
                                             f"ALTA <= {faixas[2]} | CRITICA acima")
        valor_tonelada = economia["preco_kg_atr_rs"] * economia["atr_medio_kg_t"]
        campo("    Valor da tonelada de cana", formatar_moeda(valor_tonelada) + " (ATR x preco)")
        print("\n  [0] Voltar")
        escolha = ler_menu(("1", "2", "3", "4", "5", "0"))
        match escolha:
            case "1":
                economia["preco_kg_atr_rs"] = ler_float("Novo preco do kg de ATR (R$)", 0.1, 10)
            case "2":
                economia["atr_medio_kg_t"] = ler_float("Novo ATR medio (kg/t)", 50, 250)
            case "3":
                metas["meta_perda_pct"] = ler_float("Nova meta de perda (%)", 0.5, 30)
            case "4":
                agronomia["produtividade_padrao_t_ha"] = ler_float("Nova produtividade padrao (t/ha)", 10, 250)
            case "5":
                minimo = ler_float("Velocidade minima ideal (km/h)", 0.5, 14)
                agronomia["velocidade_ideal_min_kmh"] = minimo
                agronomia["velocidade_ideal_max_kmh"] = ler_float("Velocidade maxima ideal (km/h)", minimo, 15)
            case "0":
                return
        arquivos.salvar_parametros(parametros)
        arquivos.registrar_log(f"PARAMETROS alterados (opcao {escolha})")
        mensagem_ok("parametro salvo. Vale para as proximas avaliacoes.")
        pausar()


# ===========================================================================
# PROGRAMA PRINCIPAL
# ===========================================================================
def inicializar(ctx: dict) -> None:
    """Procedimento: conexao opcional e carga de exemplo na primeira execucao."""
    tela(ctx, "Inicializacao")
    print(f"\n  {SUBTITULO}\n")
    if banco_oracle.DRIVER_OK:
        if os.environ.get("ORACLE_USER") and os.environ.get("ORACLE_PASSWORD"):
            print("  Credenciais encontradas nas variaveis de ambiente ORACLE_USER/ORACLE_PASSWORD.")
            conectar_interativo(ctx)
        elif confirmar("Deseja conectar ao banco Oracle agora?"):
            conectar_interativo(ctx)
        else:
            mensagem_aviso("modo OFFLINE: os dados serao salvos em data/base_local.json.")
    else:
        mensagem_aviso("driver oracledb indisponivel. Iniciando em modo OFFLINE (JSON local).")

    if not ctx["talhoes"] and os.path.exists(arquivos.ARQ_COLETA_EXEMPLO):
        print()
        if confirmar("Base vazia. Importar a coleta de campo de exemplo?"):
            importar_coleta(ctx)
    pausar()


def menu_principal(ctx: dict) -> None:
    """Procedimento: laco principal da aplicacao."""
    while True:
        tela(ctx, "Menu principal")
        resumo = gerar_resumo(ctx)
        print(f"  {SUBTITULO}")
        print(cor(f"  Talhoes: {len(ctx['talhoes'])} | Avaliacoes: {resumo['avaliacoes']} | "
                  f"Perda media: {formatar_numero(resumo['perda_media_pct'])}% | "
                  f"Prejuizo: {formatar_moeda(resumo['prejuizo_total_rs'])}", "cinza"))
        print("""
  [1] Talhoes (cadastro)
  [2] Registrar avaliacao de perdas
  [3] Consultar avaliacoes
  [4] Painel gerencial
  [5] Simulador de ganho
  [6] Arquivos (laudo TXT, exportar/importar JSON, log)
  [7] Banco de dados Oracle
  [8] Parametros
  [0] Sair""")
        match ler_menu(("1", "2", "3", "4", "5", "6", "7", "8", "0")):
            case "1":
                menu_talhoes(ctx)
            case "2":
                registrar_avaliacao(ctx)
                pausar()
            case "3":
                menu_consultas(ctx)
            case "4":
                painel_gerencial(ctx)
                pausar()
            case "5":
                simulador(ctx)
                pausar()
            case "6":
                menu_arquivos(ctx)
            case "7":
                menu_oracle(ctx)
            case "8":
                menu_parametros(ctx)
            case "0":
                return


def main() -> None:
    """Procedimento: ponto de entrada."""
    try:
        parametros = arquivos.carregar_parametros()
    except FileNotFoundError as erro:
        mensagem_erro(str(erro))
        sys.exit(1)
    ctx = repo.iniciar_contexto(parametros)
    try:
        inicializar(ctx)
        menu_principal(ctx)
    except (KeyboardInterrupt, EOFError):
        print()
        mensagem_aviso("execucao interrompida pelo usuario.")
    finally:
        repo.persistir_local(ctx)
        pend = repo.contar_pendencias(ctx)
        repo.desconectar_oracle(ctx)
        print()
        mensagem_ok("dados salvos em data/base_local.json.")
        total = pend["talhoes"] + pend["avaliacoes"] + pend["exclusoes"]
        if total:
            mensagem_aviso(f"{total} operacao(oes) aguardando sincronizacao com o Oracle.")
        print(f"\n  Obrigado por usar o {NOME_SISTEMA}. Menos cana no chao, mais renda no campo.\n")


if __name__ == "__main__":
    main()
