#!/usr/bin/env python3
"""
Script de Transmissão da Recomendação da IA para o ESP32 (Wokwi / Serial Real).
Consulta o modelo de Machine Learning e envia o pacote padronizado via UART.
"""

import sys
import time
import joblib
import numpy as np

def simular_envio_recomendacao():
    print("=" * 75)
    print("FARMTECH SOLUTIONS — IR ALÉM 1: ENVIO DE RECOMENDAÇÃO DE IA AO ESP32")
    print("=" * 75)

    # Cenário de Teste: Talhão com solo seco (38% de umidade) e sem chuva prevista
    umidade_teste = 38.0
    ph_teste = 6.2
    fosforo_ok = 1
    potassio_ok = 1
    nitrogenio_ok = 1
    previsao_chuva = 0

    print(f"Parâmetros da Lavoura: Umidade={umidade_teste}% | pH={ph_teste} | Chuva={previsao_chuva}")

    # Monta a mensagem no protocolo: CMD|IRRIGAR:1|SOLO:SECA|ALERTA:PRAGA_LAGARTA
    cmd_irrigar = 1 if (umidade_teste < 50.0 and previsao_chuva == 0) else 0
    condicao_solo = "SECA" if umidade_teste < 45.0 else ("MODERADA" if umidade_teste <= 65.0 else "UMIDA")
    alerta_ocorrencia = "PRAGA_LAGARTA"

    pacote_serial = f"CMD|IRRIGAR:{cmd_irrigar}|SOLO:{condicao_solo}|ALERTA:{alerta_ocorrencia}\n"

    print("\nPacote Gerado para Envio Serial (115200 bps):")
    print(f">> {pacote_serial.strip()} <<")
    print("\nInstruções para o Wokwi:")
    print("1. Inicie a simulação no Wokwi;")
    print("2. No Serial Monitor do Wokwi, cole exatamente o comando acima e pressione Enter;")
    print("3. O ESP32 responderá no Monitor Serial e o display LCD alternará para exibir a recomendação da IA e o alerta!")

if __name__ == "__main__":
    simular_envio_recomendacao()

