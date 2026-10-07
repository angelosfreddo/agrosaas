"""
banco_oracle.py
---------------
Conexao e CRUD no banco de dados ORACLE (Capitulo 6).

Segue o padrao ensinado no capitulo:
    conn = oracledb.connect(user=..., password=..., dsn='oracle.fiap.com.br:1521/ORCL')
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

Melhorias aplicadas em relacao ao exemplo do capitulo:
  - VARIAVEIS DE LIGACAO (bind variables :nome) em vez de f-string no SQL,
    o que impede SQL Injection e trata aspas/acentos automaticamente;
  - criacao automatica das tabelas na primeira execucao (se nao existirem);
  - restricoes CHECK/FK no proprio banco, como ultima barreira de consistencia;
  - cada funcao recebe a conexao por PARAMETRO (subalgoritmos reutilizaveis).

Tabelas (prefixo PZ_ para nao colidir com outras tabelas do schema FIAP):
  PZ_TALHAO          -> cadastro dos talhoes de cana
  PZ_AVALIACAO_PERDA -> cada amostragem de perdas realizada apos a colheita
"""

from datetime import date

# O driver pode nao estar instalado (ou estar bloqueado pela politica do
# computador). Nesse caso o sistema continua funcionando em MODO OFFLINE.
try:
    import oracledb
    DRIVER_OK = True
    DRIVER_ERRO = ""
except Exception as erro:  # ImportError ou DLL bloqueada
    oracledb = None
    DRIVER_OK = False
    DRIVER_ERRO = str(erro)


# ---------------------------------------------------------------------------
# DDL - estrutura das tabelas (mesmo conteudo de scripts/ddl_perdazero.sql)
# ---------------------------------------------------------------------------
DDL_TABELAS = (
    ("PZ_TALHAO", """
        CREATE TABLE PZ_TALHAO (
            CODIGO              VARCHAR2(10)  PRIMARY KEY,
            FAZENDA             VARCHAR2(60)  NOT NULL,
            AREA_HA             NUMBER(10,2)  NOT NULL CHECK (AREA_HA > 0),
            VARIEDADE           VARCHAR2(30)  NOT NULL,
            ESTAGIO_CORTE       NUMBER(2)     NOT NULL CHECK (ESTAGIO_CORTE BETWEEN 1 AND 15),
            PRODUTIVIDADE_T_HA  NUMBER(6,2)   NOT NULL CHECK (PRODUTIVIDADE_T_HA > 0)
        )"""),
    ("PZ_AVALIACAO_PERDA", """
        CREATE TABLE PZ_AVALIACAO_PERDA (
            ID                  NUMBER GENERATED AS IDENTITY PRIMARY KEY,
            COD_AVALIACAO       VARCHAR2(30)  NOT NULL UNIQUE,
            CODIGO_TALHAO       VARCHAR2(10)  NOT NULL REFERENCES PZ_TALHAO (CODIGO),
            DATA_AVALIACAO      DATE          NOT NULL,
            TIPO_COLHEITA       VARCHAR2(12)  NOT NULL CHECK (TIPO_COLHEITA IN ('MECANIZADA', 'MANUAL')),
            COLHEDORA           VARCHAR2(20),
            OPERADOR            VARCHAR2(60),
            TURNO               VARCHAR2(10)  NOT NULL CHECK (TURNO IN ('DIURNO', 'NOTURNO')),
            VELOCIDADE_KMH      NUMBER(4,1),
            PONTOS_AMOSTRADOS   NUMBER(3)     NOT NULL,
            AREA_AMOSTRADA_M2   NUMBER(8,2)   NOT NULL CHECK (AREA_AMOSTRADA_M2 > 0),
            KG_TOCO             NUMBER(8,2)   DEFAULT 0 NOT NULL,
            KG_TOLETE           NUMBER(8,2)   DEFAULT 0 NOT NULL,
            KG_CANA_INTEIRA     NUMBER(8,2)   DEFAULT 0 NOT NULL,
            KG_PONTEIRO         NUMBER(8,2)   DEFAULT 0 NOT NULL,
            KG_ESTILHACO        NUMBER(8,2)   DEFAULT 0 NOT NULL,
            KG_TOTAL            NUMBER(10,2)  NOT NULL,
            PERDA_T_HA          NUMBER(8,3)   NOT NULL,
            PERDA_PCT           NUMBER(6,2)   NOT NULL,
            PREJUIZO_RS         NUMBER(14,2)  NOT NULL,
            CLASSIFICACAO       VARCHAR2(10)  NOT NULL
        )"""),
)

# Tupla com a ordem das colunas usada no SELECT e na conversao para dict
COLUNAS_AVALIACAO = (
    "COD_AVALIACAO", "CODIGO_TALHAO", "DATA_AVALIACAO", "TIPO_COLHEITA",
    "COLHEDORA", "OPERADOR", "TURNO", "VELOCIDADE_KMH", "PONTOS_AMOSTRADOS",
    "AREA_AMOSTRADA_M2", "KG_TOCO", "KG_TOLETE", "KG_CANA_INTEIRA",
    "KG_PONTEIRO", "KG_ESTILHACO", "KG_TOTAL", "PERDA_T_HA", "PERDA_PCT",
    "PREJUIZO_RS", "CLASSIFICACAO",
)


# ===========================================================================
# CONEXAO E ESTRUTURA
# ===========================================================================
def conectar(usuario: str, senha: str, dsn: str):
    """
    Funcao: abre a conexao com o Oracle e devolve o objeto de conexao.
    Levanta RuntimeError com mensagem amigavel em caso de falha.
    """
    if not DRIVER_OK:
        raise RuntimeError(f"driver oracledb indisponivel: {DRIVER_ERRO}")
    try:
        return oracledb.connect(user=usuario, password=senha, dsn=dsn)
    except Exception as erro:
        raise RuntimeError(f"falha ao conectar no Oracle: {erro}") from erro


def desconectar(conn) -> None:
    """Procedimento: fecha a conexao, ignorando erros de rede."""
    try:
        if conn is not None:
            conn.close()
    except Exception:
        pass


def criar_estrutura(conn) -> list:
    """
    Funcao: cria as tabelas que ainda nao existem no schema do usuario.
    Devolve a lista com os nomes das tabelas criadas nesta execucao.
    """
    criadas = []
    cursor = conn.cursor()
    for nome, ddl in DDL_TABELAS:
        cursor.execute(
            "SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = :nome",
            {"nome": nome})
        existe = cursor.fetchone()[0] > 0
        if not existe:
            cursor.execute(ddl)
            criadas.append(nome)
    conn.commit()
    cursor.close()
    return criadas


# ===========================================================================
# TALHOES
# ===========================================================================
def listar_talhoes(conn) -> list:
    """Funcao: devolve todos os talhoes como lista de dicionarios."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT CODIGO, FAZENDA, AREA_HA, VARIEDADE, ESTAGIO_CORTE, PRODUTIVIDADE_T_HA
          FROM PZ_TALHAO ORDER BY CODIGO""")
    talhoes = []
    for linha in cursor.fetchall():
        talhoes.append({
            "codigo": linha[0],
            "fazenda": linha[1],
            "area_ha": float(linha[2]),
            "variedade": linha[3],
            "estagio_corte": int(linha[4]),
            "produtividade_t_ha": float(linha[5]),
        })
    cursor.close()
    return talhoes


def salvar_talhao(conn, talhao: dict) -> None:
    """
    Procedimento: insere OU atualiza um talhao (MERGE = upsert).
    Usado tanto no cadastro/alteracao quanto na sincronizacao offline.
    """
    cursor = conn.cursor()
    cursor.execute("""
        MERGE INTO PZ_TALHAO T
        USING (SELECT :codigo AS CODIGO FROM DUAL) S
           ON (T.CODIGO = S.CODIGO)
        WHEN MATCHED THEN UPDATE SET
             FAZENDA = :fazenda, AREA_HA = :area_ha, VARIEDADE = :variedade,
             ESTAGIO_CORTE = :estagio_corte, PRODUTIVIDADE_T_HA = :produtividade_t_ha
        WHEN NOT MATCHED THEN INSERT
             (CODIGO, FAZENDA, AREA_HA, VARIEDADE, ESTAGIO_CORTE, PRODUTIVIDADE_T_HA)
             VALUES (:codigo, :fazenda, :area_ha, :variedade, :estagio_corte, :produtividade_t_ha)
        """, {
            "codigo": talhao["codigo"],
            "fazenda": talhao["fazenda"],
            "area_ha": talhao["area_ha"],
            "variedade": talhao["variedade"],
            "estagio_corte": talhao["estagio_corte"],
            "produtividade_t_ha": talhao["produtividade_t_ha"],
        })
    conn.commit()
    cursor.close()


def excluir_talhao(conn, codigo: str) -> int:
    """Funcao: exclui o talhao e devolve a quantidade de linhas afetadas."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM PZ_TALHAO WHERE CODIGO = :codigo", {"codigo": codigo})
    afetadas = cursor.rowcount
    conn.commit()
    cursor.close()
    return afetadas


# ===========================================================================
# AVALIACOES DE PERDA
# ===========================================================================
def _linha_para_avaliacao(linha: tuple) -> dict:
    """Funcao interna: converte uma linha do SELECT em dicionario."""
    dados = dict(zip(COLUNAS_AVALIACAO, linha))
    data_bd = dados["DATA_AVALIACAO"]
    velocidade = dados["VELOCIDADE_KMH"]
    return {
        "cod_avaliacao": dados["COD_AVALIACAO"],
        "codigo_talhao": dados["CODIGO_TALHAO"],
        "data_avaliacao": data_bd.date().isoformat() if hasattr(data_bd, "date") else str(data_bd),
        "tipo_colheita": dados["TIPO_COLHEITA"],
        "colhedora": dados["COLHEDORA"],
        "operador": dados["OPERADOR"],
        "turno": dados["TURNO"],
        "velocidade_kmh": float(velocidade) if velocidade is not None else None,
        "pontos_amostrados": int(dados["PONTOS_AMOSTRADOS"]),
        "area_amostrada_m2": float(dados["AREA_AMOSTRADA_M2"]),
        "amostras": {
            "toco": float(dados["KG_TOCO"]),
            "tolete": float(dados["KG_TOLETE"]),
            "cana_inteira": float(dados["KG_CANA_INTEIRA"]),
            "ponteiro": float(dados["KG_PONTEIRO"]),
            "estilhaco": float(dados["KG_ESTILHACO"]),
        },
        "kg_total": float(dados["KG_TOTAL"]),
        "perda_t_ha": float(dados["PERDA_T_HA"]),
        "perda_pct": float(dados["PERDA_PCT"]),
        "prejuizo_rs": float(dados["PREJUIZO_RS"]),
        "classificacao": dados["CLASSIFICACAO"],
    }


def listar_avaliacoes(conn) -> list:
    """Funcao: devolve todas as avaliacoes como lista de dicionarios."""
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT {', '.join(COLUNAS_AVALIACAO)} FROM PZ_AVALIACAO_PERDA "
        "ORDER BY DATA_AVALIACAO, ID")
    avaliacoes = [_linha_para_avaliacao(linha) for linha in cursor.fetchall()]
    cursor.close()
    return avaliacoes


def existe_avaliacao(conn, cod_avaliacao: str) -> bool:
    """Funcao: verifica se a avaliacao ja esta gravada no banco."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM PZ_AVALIACAO_PERDA WHERE COD_AVALIACAO = :cod",
        {"cod": cod_avaliacao})
    existe = cursor.fetchone()[0] > 0
    cursor.close()
    return existe


def inserir_avaliacao(conn, avaliacao: dict) -> None:
    """Procedimento: grava uma avaliacao ja processada (com indicadores)."""
    amostras = avaliacao["amostras"]
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO PZ_AVALIACAO_PERDA (
            COD_AVALIACAO, CODIGO_TALHAO, DATA_AVALIACAO, TIPO_COLHEITA, COLHEDORA,
            OPERADOR, TURNO, VELOCIDADE_KMH, PONTOS_AMOSTRADOS, AREA_AMOSTRADA_M2,
            KG_TOCO, KG_TOLETE, KG_CANA_INTEIRA, KG_PONTEIRO, KG_ESTILHACO,
            KG_TOTAL, PERDA_T_HA, PERDA_PCT, PREJUIZO_RS, CLASSIFICACAO
        ) VALUES (
            :cod, :talhao, :data_av, :tipo, :colhedora,
            :operador, :turno, :velocidade, :pontos, :area,
            :toco, :tolete, :cana_inteira, :ponteiro, :estilhaco,
            :kg_total, :perda_t_ha, :perda_pct, :prejuizo, :classe
        )""", {
            "cod": avaliacao["cod_avaliacao"],
            "talhao": avaliacao["codigo_talhao"],
            "data_av": date.fromisoformat(avaliacao["data_avaliacao"]),
            "tipo": avaliacao["tipo_colheita"],
            "colhedora": avaliacao.get("colhedora"),
            "operador": avaliacao.get("operador"),
            "turno": avaliacao["turno"],
            "velocidade": avaliacao.get("velocidade_kmh"),
            "pontos": avaliacao["pontos_amostrados"],
            "area": avaliacao["area_amostrada_m2"],
            "toco": amostras["toco"],
            "tolete": amostras["tolete"],
            "cana_inteira": amostras["cana_inteira"],
            "ponteiro": amostras["ponteiro"],
            "estilhaco": amostras["estilhaco"],
            "kg_total": avaliacao["kg_total"],
            "perda_t_ha": avaliacao["perda_t_ha"],
            "perda_pct": avaliacao["perda_pct"],
            "prejuizo": avaliacao["prejuizo_rs"],
            "classe": avaliacao["classificacao"],
        })
    conn.commit()
    cursor.close()


def excluir_avaliacao(conn, cod_avaliacao: str) -> int:
    """Funcao: exclui uma avaliacao e devolve as linhas afetadas."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM PZ_AVALIACAO_PERDA WHERE COD_AVALIACAO = :cod",
                   {"cod": cod_avaliacao})
    afetadas = cursor.rowcount
    conn.commit()
    cursor.close()
    return afetadas


def consultar_ranking_sql(conn) -> list:
    """
    Funcao: exemplo de consulta analitica executada DENTRO do Oracle
    (GROUP BY), devolvendo lista de tuplas (colhedora, qtd, media %, prejuizo).
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT NVL(COLHEDORA, 'MANUAL'), COUNT(*), ROUND(AVG(PERDA_PCT), 2),
               ROUND(SUM(PREJUIZO_RS), 2)
          FROM PZ_AVALIACAO_PERDA
         GROUP BY NVL(COLHEDORA, 'MANUAL')
         ORDER BY 3 DESC""")
    resultado = [(l[0], int(l[1]), float(l[2]), float(l[3])) for l in cursor.fetchall()]
    cursor.close()
    return resultado
