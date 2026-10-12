-- ============================================================================
-- PROJETO: PerdaZero - Gestao de Perdas na Colheita Mecanizada de Cana
-- DISCIPLINA: Python e Alem (Fase 2 - FIAP)
-- BANCO DE DADOS: Oracle Database (oracle.fiap.com.br:1521/ORCL)
-- ============================================================================

-- 1. Tabela de Talhoes de Cana
CREATE TABLE PZ_TALHAO (
    CODIGO              VARCHAR2(10)  PRIMARY KEY,
    FAZENDA             VARCHAR2(60)  NOT NULL,
    AREA_HA             NUMBER(10,2)  NOT NULL CHECK (AREA_HA > 0),
    VARIEDADE           VARCHAR2(30)  NOT NULL,
    ESTAGIO_CORTE       NUMBER(2)     NOT NULL CHECK (ESTAGIO_CORTE BETWEEN 1 AND 15),
    PRODUTIVIDADE_T_HA  NUMBER(6,2)   NOT NULL CHECK (PRODUTIVIDADE_T_HA > 0)
);

-- 2. Tabela de Avaliacoes / Amostragens de Perda na Colheita
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
);

-- Indices para otimizacao de consultas e relatorios
CREATE INDEX IDX_PZ_AVAL_TALHAO ON PZ_AVALIACAO_PERDA(CODIGO_TALHAO);
CREATE INDEX IDX_PZ_AVAL_DATA ON PZ_AVALIACAO_PERDA(DATA_AVALIACAO);
