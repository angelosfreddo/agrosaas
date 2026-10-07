"""
calculos.py
-----------
Regras de negocio do PerdaZero (nucleo agronomico e financeiro).

Todas as rotinas aqui sao FUNCOES com passagem de parametros e sem efeitos
colaterais (nao leem teclado, nao gravam arquivo, nao acessam banco).
Isso facilita testar (ver tests/test_calculos.py) e reaproveitar.

METODOLOGIA DE AMOSTRAGEM (adaptada da pratica de campo das usinas)
-------------------------------------------------------------------
Apos a passagem da colhedora, a equipe de qualidade lanca molduras de area
conhecida (ex.: 10 m2) em pontos do talhao, recolhe TODA a cana que ficou
no chao e separa por TIPO DE PERDA. Cada tipo aponta para uma causa
diferente na operacao - e isso que permite o DIAGNOSTICO automatico.

    perda (t/ha) = kg recolhidos / area amostrada (m2) * 10
                   (kg/m2 * 10.000 m2/ha / 1.000 kg/t)

    perda (%)    = perda / (produtividade colhida + perda) * 100

    prejuizo R$  = perda (t/ha) * area (ha) * ATR (kg/t) * preco kg ATR
"""

# ---------------------------------------------------------------------------
# TUPLAS: estruturas imutaveis com o "vocabulario" do dominio
# ---------------------------------------------------------------------------
TIPOS_PERDA = ("toco", "tolete", "cana_inteira", "ponteiro", "estilhaco")
CLASSES_PERDA = ("BAIXA", "MODERADA", "ALTA", "CRITICA")
TIPOS_COLHEITA = ("MECANIZADA", "MANUAL")
TURNOS = ("DIURNO", "NOTURNO")

# ---------------------------------------------------------------------------
# DICIONARIOS: rotulos e base de conhecimento agronomico
# ---------------------------------------------------------------------------
ROTULOS_PERDA = {
    "toco": "Toco (corte basal alto)",
    "tolete": "Tolete (rebolo no chao)",
    "cana_inteira": "Cana inteira",
    "ponteiro": "Ponteiro (cana no ponteiro)",
    "estilhaco": "Estilhaco / lasca",
}

# Para cada tipo de perda: (causa provavel, acao recomendada)
BASE_CONHECIMENTO = {
    "toco": (
        "Corte de base acima do nivel do solo, facas do disco basal gastas "
        "ou terreno mal sistematizado.",
        "Rebaixar o corte de base, trocar/afiar as facas do disco basal e "
        "ativar o controle automatico de altura (quando disponivel).",
    ),
    "tolete": (
        "Velocidade excessiva da colhedora, embuchamento no elevador ou "
        "transbordo fora de sincronia com a colhedora.",
        "Reduzir a velocidade para a faixa ideal, revisar o elevador e "
        "sincronizar o transbordo (piloto automatico / comunicacao).",
    ),
    "cana_inteira": (
        "Divisores de linha mal regulados ou canavial acamado colhido "
        "contra o sentido do tombamento.",
        "Ajustar os divisores de linha e planejar a colheita no sentido do "
        "acamamento da cana.",
    ),
    "ponteiro": (
        "Cortador de pontas (despontador) regulado muito baixo, levando "
        "colmo junto com o ponteiro.",
        "Elevar a altura do despontador e ajustar conforme o porte da "
        "variedade.",
    ),
    "estilhaco": (
        "Facas do picador sem fio ou rotacao excessiva do extrator primario, "
        "que estilhaca e arremessa cana para fora.",
        "Afiar/trocar as facas do picador e reduzir a rotacao do extrator "
        "primario.",
    ),
}


# ---------------------------------------------------------------------------
# CALCULOS BASICOS
# ---------------------------------------------------------------------------
def calcular_kg_total(amostras: dict) -> float:
    """Funcao: soma os kg recolhidos de todos os tipos de perda."""
    total = 0.0
    for tipo in TIPOS_PERDA:
        total += float(amostras.get(tipo, 0.0))
    return round(total, 3)


def calcular_perda_t_ha(kg_total: float, area_amostrada_m2: float) -> float:
    """Funcao: converte kg recolhidos na area amostrada em toneladas/hectare."""
    if area_amostrada_m2 <= 0:
        raise ValueError("A area amostrada deve ser maior que zero.")
    return round(kg_total / area_amostrada_m2 * 10, 3)


def calcular_perda_pct(perda_t_ha: float, produtividade_t_ha: float) -> float:
    """Funcao: percentual da cana produzida que ficou no campo."""
    producao_total = produtividade_t_ha + perda_t_ha
    if producao_total <= 0:
        return 0.0
    return round(perda_t_ha / producao_total * 100, 2)


def calcular_prejuizo(perda_t_ha: float, area_ha: float, atr_kg_t: float,
                      preco_kg_atr: float) -> float:
    """Funcao: valor (R$) deixado no campo, pelo modelo de pagamento por ATR."""
    return round(perda_t_ha * area_ha * atr_kg_t * preco_kg_atr, 2)


def classificar_perda(perda_pct: float, faixas: tuple) -> str:
    """
    Funcao: classifica a perda percentual.
    faixas -> tupla com 3 limites crescentes, ex.: (2.5, 5.0, 10.0)
    """
    for indice, limite in enumerate(faixas):
        if perda_pct <= limite:
            return CLASSES_PERDA[indice]
    return CLASSES_PERDA[-1]


def composicao_perdas(amostras: dict) -> dict:
    """Funcao: participacao (%) de cada tipo de perda no total recolhido."""
    total = calcular_kg_total(amostras)
    composicao = {}
    for tipo in TIPOS_PERDA:
        if total > 0:
            composicao[tipo] = round(float(amostras.get(tipo, 0.0)) / total * 100, 1)
        else:
            composicao[tipo] = 0.0
    return composicao


# ---------------------------------------------------------------------------
# PROCESSAMENTO COMPLETO DE UMA AVALIACAO
# ---------------------------------------------------------------------------
def processar_avaliacao(avaliacao: dict, talhao: dict, parametros: dict) -> dict:
    """
    Funcao: recebe a avaliacao "crua" (dados de campo) e devolve um NOVO
    dicionario com os indicadores calculados (perda t/ha, %, R$, classe).
    """
    economia = parametros["economia"]
    faixas = tuple(parametros["metas"]["faixas_classificacao_pct"])

    resultado = dict(avaliacao)  # copia para nao alterar o original
    kg_total = calcular_kg_total(avaliacao["amostras"])
    perda_t_ha = calcular_perda_t_ha(kg_total, avaliacao["area_amostrada_m2"])
    perda_pct = calcular_perda_pct(perda_t_ha, talhao["produtividade_t_ha"])

    resultado["kg_total"] = kg_total
    resultado["perda_t_ha"] = perda_t_ha
    resultado["perda_pct"] = perda_pct
    resultado["prejuizo_rs"] = calcular_prejuizo(
        perda_t_ha, talhao["area_ha"],
        economia["atr_medio_kg_t"], economia["preco_kg_atr_rs"])
    resultado["classificacao"] = classificar_perda(perda_pct, faixas)
    return resultado


# ---------------------------------------------------------------------------
# DIAGNOSTICO (o diferencial da solucao)
# ---------------------------------------------------------------------------
def diagnosticar(avaliacao: dict, parametros: dict) -> list:
    """
    Funcao: gera uma LISTA de recomendacoes priorizadas.
    Cada item e uma TUPLA (prioridade, titulo, causa, acao).

    Regras:
      1. Todo tipo de perda com participacao >= limite configurado gera
         recomendacao (o maior tipo vem primeiro).
      2. Velocidade da colhedora acima da faixa ideal gera alerta.
      3. Colheita manual acima de 5% foge do padrao historico.
      4. Avaliacao abaixo da meta recebe reforco positivo.
    """
    agronomia = parametros["agronomia"]
    meta = parametros["metas"]["meta_perda_pct"]
    recomendacoes = []

    composicao = composicao_perdas(avaliacao["amostras"])
    ordenados = sorted(composicao.items(), key=lambda par: par[1], reverse=True)

    prioridade = 1
    for tipo, participacao in ordenados:
        if participacao >= agronomia["participacao_minima_diagnostico_pct"]:
            causa, acao = BASE_CONHECIMENTO[tipo]
            titulo = f"{ROTULOS_PERDA[tipo]} = {participacao:.1f}% da perda"
            recomendacoes.append((prioridade, titulo, causa, acao))
            prioridade += 1

    velocidade = avaliacao.get("velocidade_kmh")
    vel_max = agronomia["velocidade_ideal_max_kmh"]
    vel_min = agronomia["velocidade_ideal_min_kmh"]
    if avaliacao.get("tipo_colheita") == "MECANIZADA" and velocidade:
        if velocidade > vel_max:
            recomendacoes.append((
                prioridade,
                f"Velocidade de {velocidade:.1f} km/h acima do ideal",
                f"A faixa recomendada e de {vel_min:.1f} a {vel_max:.1f} km/h. "
                "Acima disso o rolo alimentador nao processa toda a cana.",
                f"Reduzir a velocidade para ate {vel_max:.1f} km/h nesse talhao.",
            ))
            prioridade += 1
        elif velocidade < vel_min:
            recomendacoes.append((
                prioridade,
                f"Velocidade de {velocidade:.1f} km/h abaixo do ideal",
                "Velocidade muito baixa reduz a capacidade operacional e "
                "aumenta custo por tonelada, sem ganho relevante de perda.",
                f"Operar entre {vel_min:.1f} e {vel_max:.1f} km/h.",
            ))
            prioridade += 1

    if avaliacao.get("tipo_colheita") == "MANUAL" and avaliacao.get("perda_pct", 0) > 5:
        recomendacoes.append((
            prioridade,
            "Perda manual acima de 5%",
            "Na colheita manual as perdas raramente passam de 5%.",
            "Revisar treinamento da equipe de corte e o enleiramento.",
        ))
        prioridade += 1

    if avaliacao.get("perda_pct", 0) <= meta:
        recomendacoes.append((
            prioridade,
            f"Perda dentro da meta ({meta:.1f}%)",
            "A regulagem atual esta adequada para este talhao.",
            "Registrar os parametros da colhedora como referencia de boas praticas.",
        ))

    return recomendacoes


# ---------------------------------------------------------------------------
# SIMULADOR E INDICADORES GERENCIAIS
# ---------------------------------------------------------------------------
def simular_meta(avaliacao: dict, talhao: dict, meta_pct: float,
                 parametros: dict) -> dict:
    """
    Funcao: "E se?" - quanto dinheiro volta para o produtor se a perda
    deste talhao cair para a meta informada.
    """
    economia = parametros["economia"]
    produtividade = talhao["produtividade_t_ha"]
    # perda (t/ha) que corresponde exatamente a meta percentual
    perda_meta_t_ha = meta_pct * produtividade / (100 - meta_pct)
    perda_atual = avaliacao["perda_t_ha"]
    reducao_t_ha = max(0.0, perda_atual - perda_meta_t_ha)
    toneladas = reducao_t_ha * talhao["area_ha"]
    ganho = calcular_prejuizo(reducao_t_ha, talhao["area_ha"],
                              economia["atr_medio_kg_t"],
                              economia["preco_kg_atr_rs"])
    return {
        "perda_atual_t_ha": round(perda_atual, 3),
        "perda_meta_t_ha": round(perda_meta_t_ha, 3),
        "toneladas_recuperadas": round(toneladas, 2),
        "ganho_rs": ganho,
    }


def estatisticas(valores: list) -> dict:
    """Funcao: media, minimo e maximo de uma lista numerica."""
    if not valores:
        return {"qtd": 0, "media": 0.0, "minimo": 0.0, "maximo": 0.0}
    return {
        "qtd": len(valores),
        "media": round(sum(valores) / len(valores), 2),
        "minimo": round(min(valores), 2),
        "maximo": round(max(valores), 2),
    }


def agrupar_media(avaliacoes: list, chave: str, campo: str = "perda_pct") -> list:
    """
    Funcao: agrupa a tabela de memoria por 'chave' (colhedora, turno,
    talhao, operador) e devolve LISTA DE TUPLAS (grupo, media, qtd, prejuizo)
    ordenada da MAIOR para a menor media de perda (ranking).
    """
    grupos = {}
    for avaliacao in avaliacoes:
        grupo = avaliacao.get(chave) or "-"
        if grupo not in grupos:
            grupos[grupo] = {"valores": [], "prejuizo": 0.0}
        grupos[grupo]["valores"].append(avaliacao[campo])
        grupos[grupo]["prejuizo"] += avaliacao.get("prejuizo_rs", 0.0)

    ranking = []
    for grupo, dados in grupos.items():
        media = sum(dados["valores"]) / len(dados["valores"])
        ranking.append((grupo, round(media, 2), len(dados["valores"]),
                        round(dados["prejuizo"], 2)))
    ranking.sort(key=lambda item: item[1], reverse=True)
    return ranking


def composicao_geral(avaliacoes: list) -> dict:
    """Funcao: soma dos kg por tipo de perda em todas as avaliacoes."""
    soma = {tipo: 0.0 for tipo in TIPOS_PERDA}
    for avaliacao in avaliacoes:
        for tipo in TIPOS_PERDA:
            soma[tipo] += float(avaliacao["amostras"].get(tipo, 0.0))
    return soma
