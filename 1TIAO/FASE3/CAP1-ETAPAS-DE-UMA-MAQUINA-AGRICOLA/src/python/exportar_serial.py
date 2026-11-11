"""
exportar_serial.py - Etapa 1 da Parte 1: exportacao das leituras do Monitor Serial.

Como o Wokwi gratuito nao conecta em banco de dados, o historico e obtido assim:
  1. roda-se o firmware src/iot_esp32/sketch.ino no Wokwi, variando os sensores
     (slider do DHT22, luminosidade do LDR e botoes N, P e K);
  2. copia-se TODO o texto do Monitor Serial para data/raw/monitor_serial_wokwi.txt;
  3. este script le esse texto, separa as linhas de dados CSV das mensagens
     (linhas iniciadas por '#', boot do ESP32, etc.) e grava
     data/raw/leituras_brutas_wokwi.csv, sem alterar nenhum valor.

Nenhuma limpeza e feita aqui: o arquivo gerado e o dado BRUTO. A limpeza fica
em tratamento_dados.py.

Execucao:
    python src/python/exportar_serial.py
"""

import csv
import re
import sys

import config

# Uma linha de dados comeca com "AAAA-MM-DD HH:MM," (data/hora do relogio simulado)
PADRAO_LINHA_DADOS = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2},")


def extrair_linhas(caminho_txt):
    """Le o log do Monitor Serial e devolve (linhas_de_dados, estatisticas).

    Cada linha de dados vira uma lista com os 9 campos do firmware. Linhas com
    numero de campos diferente sao contadas como corrompidas (ex.: linha cortada
    no momento da copia) e descartadas.
    """
    dados = []
    estat = {"total": 0, "dados": 0, "mensagens": 0, "corrompidas": 0}

    with open(caminho_txt, encoding="utf-8", errors="replace") as arq:
        for linha in arq:
            estat["total"] += 1
            linha = linha.strip()
            if not linha or linha.startswith("data_hora"):
                continue                       # linha vazia ou cabecalho
            if not PADRAO_LINHA_DADOS.match(linha):
                estat["mensagens"] += 1        # '#', boot do ESP32, alertas...
                continue
            campos = [c.strip() for c in linha.split(",")]
            if len(campos) != len(config.COLUNAS_SERIAL):
                estat["corrompidas"] += 1
                continue
            dados.append(campos)
            estat["dados"] += 1
    return dados, estat


def gravar_csv(linhas, caminho_csv):
    """Grava as linhas no CSV bruto, acrescentando a coluna origem = WOKWI."""
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_csv, "w", newline="", encoding="utf-8") as arq:
        escritor = csv.writer(arq)
        escritor.writerow(config.COLUNAS_SERIAL + ["origem"])
        for campos in linhas:
            escritor.writerow(campos + ["WOKWI"])


def main():
    if not config.ARQ_MONITOR_SERIAL.exists():
        print(f"Arquivo nao encontrado: {config.ARQ_MONITOR_SERIAL}")
        print("Cole o texto do Monitor Serial do Wokwi nesse arquivo e rode novamente.")
        sys.exit(1)

    linhas, estat = extrair_linhas(config.ARQ_MONITOR_SERIAL)
    gravar_csv(linhas, config.ARQ_BRUTO_WOKWI)

    print("Exportacao do Monitor Serial concluida")
    print(f"  Linhas lidas no log ........: {estat['total']}")
    print(f"  Linhas de dados (CSV) ......: {estat['dados']}")
    print(f"  Mensagens/alertas ignorados : {estat['mensagens']}")
    print(f"  Linhas corrompidas .........: {estat['corrompidas']}")
    if linhas:
        print(f"  Periodo simulado ...........: {linhas[0][0]} ate {linhas[-1][0]}")
    print(f"  Arquivo gerado .............: {config.ARQ_BRUTO_WOKWI}")


if __name__ == "__main__":
    main()

