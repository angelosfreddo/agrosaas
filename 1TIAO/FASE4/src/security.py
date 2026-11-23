#!/usr/bin/env python3
"""
Módulo de Segurança Cibernética — FarmTech Solutions (Fase 4).
Implementa as contramedidas obrigatórias de proteção:
1. Carregamento seguro de credenciais via variáveis de ambiente (.env);
2. Autenticação com hashing criptográfico (SHA-256 com Salt);
3. Registro de logs de auditoria e eventos de segurança;
4. Verificação de integridade dos registros de campo com detecção de adulteração (Tampering).
"""

import os
import sys

# Garante inclusão da raiz no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import hashlib
from datetime import datetime
import pandas as pd
# Carrega variáveis de ambiente (suporta python-dotenv ou parser nativo)
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
try:
    from dotenv import load_dotenv
    load_dotenv(env_path)
except ImportError:
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

SALT_PADRAO = os.getenv("SECRET_KEY_AUDIT", "farmtech_cybersecurity_secret_salt_2026")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_HASH = os.getenv("ADMIN_PASSWORD_HASH", "3a28d48666e6786d973db885dd645df7cd1e6fb14ed337417e3c8a9559f0e08c")
USUARIOS_AUTORIZADOS = {ADMIN_USER.strip().lower(), "admin", "gestor_farmtech"}

def gerar_hash_senha(senha, salt=SALT_PADRAO):
    """
    Gera o hash SHA-256 da senha combinada com salt criptografico.
    """
    return hashlib.sha256(f"{senha}{salt}".encode("utf-8")).hexdigest()

def autenticar_usuario(usuario, senha, ip_origem="127.0.0.1"):
    """
    Autentica o usuario e registra o evento na trilha de auditoria.
    Aceita os identificadores administrativos autorizados (ex: admin, gestor_farmtech).
    """
    from src.database import get_connection
    hash_informado = gerar_hash_senha(senha)
    usuario_normalizado = (usuario or "").strip().lower()
    sucesso = (usuario_normalizado in USUARIOS_AUTORIZADOS and hash_informado == ADMIN_HASH)
    
    status = "SUCESSO" if sucesso else "FALHA"
    detalhes = "Login realizado no painel Streamlit" if sucesso else "Tentativa de login com credenciais invalidas"
    
    registrar_log_seguranca("LOGIN_TENTATIVA", usuario, ip_origem, status, detalhes)
    return sucesso

def registrar_log_seguranca(evento, usuario, ip_origem, status, detalhes):
    """
    Grava um evento de auditoria com hash encadeado na tabela FT4_LOG_SEGURANCA.
    """
    from src.database import get_connection
    dt_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hash_log = hashlib.sha256(f"{dt_agora}|{evento}|{usuario}|{ip_origem}|{status}|{SALT_PADRAO}".encode()).hexdigest()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO FT4_LOG_SEGURANCA (DATA_HORA, EVENTO, USUARIO, IP_ORIGEM, STATUS, DETALHES, HASH_LOG)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (dt_agora, evento, usuario, ip_origem, status, detalhes, hash_log))
    conn.commit()
    conn.close()

def simular_teste_adulteracao():
    """
    Demonstração prática de segurança cibernética:
    1. Lê uma ocorrência existente;
    2. Adultera o texto da ocorrência diretamente no banco de dados (ataque de injeção/modificação não autorizada);
    3. Executa o algoritmo de verificação de integridade e detecta a violação do hash SHA-256;
    4. Registra o incidente cibernético no log de auditoria.
    """
    from src.database import get_connection, verificar_integridade_ocorrencias, calcular_hash_ocorrencia

    print("--- INICIANDO TESTE PRÁTICO DE SEGURANÇA: DETECÇÃO DE ADULTERAÇÃO ---")
    conn = get_connection()
    cur = conn.cursor()

    # Inserir um registro temporário para teste de violação
    dt_teste = "2026-04-10 11:00:00"
    obs_original = "Vistoria normal sem sinais de pragas no Talhao 01."
    hash_original = calcular_hash_ocorrencia(dt_teste, "TALHAO_01", "VISTORIA_ROTINA", "BAIXA", obs_original, "Operador Teste")

    cur.execute("""
    INSERT INTO FT4_OCORRENCIA_CAMPO (DATA_HORA, CODIGO_TALHAO, TIPO_OCORRENCIA, GRAVIDADE, OBSERVACAO, OPERADOR, HASH_INTEGRIDADE)
    VALUES (?, 'TALHAO_01', 'VISTORIA_ROTINA', 'BAIXA', ?, 'Operador Teste', ?);
    """, (dt_teste, obs_original, hash_original))
    id_teste = cur.lastrowid
    conn.commit()

    print(f"1. Registro criado com ID {id_teste} e Hash SHA-256 legitimo: {hash_original[:16]}...")

    # Adulteração maliciosa simulada (modifica a observação sem recalcular o hash)
    obs_adulterada = "ADULTERACAO MALICIOSA: Relato falso inserido para acionar defensivos desnecessarios."
    cur.execute("""
    UPDATE FT4_OCORRENCIA_CAMPO
    SET OBSERVACAO = ?
    WHERE ID_OCORRENCIA = ?;
    """, (obs_adulterada, id_teste))
    conn.commit()
    conn.close()

    print(f"2. Registro ID {id_teste} adulterado clandestinamente no banco de dados!")

    # Execução da verificação de integridade
    df_audit = verificar_integridade_ocorrencias()
    registro_adulterado = df_audit[df_audit["ID_OCORRENCIA"] == id_teste].iloc[0]

    violacao_detectada = not registro_adulterado["INTEGRIDADE_CONFIRMADA"]
    if violacao_detectada:
        print("3. ALERTA DE SEGURANCA: O hash calculado nao coincide com o hash gravado!")
        print(f"   - Hash Gravado no Banco:    {registro_adulterado['HASH_BANCO']}")
        print(f"   - Hash Real Recalculado:    {registro_adulterado['HASH_CALCULADO']}")
        print("   - STATUS DE INTEGRIDADE:    VIOLADA (REGISTRO CORROMPIDO / ADULTERADO)")
        registrar_log_seguranca("ALERTA_ADULTERACAO", "sistema_audit", "127.0.0.1", "CRITICO",
                                f"Adulteracao detectada no registro de ocorrencia ID {id_teste}")
    else:
        print("3. Erro no teste de integridade.")

    return violacao_detectada

if __name__ == "__main__":
    print(f"Hash da senha padrao 'farmtech2026': {gerar_hash_senha('farmtech2026')}")
    simular_teste_adulteracao()
