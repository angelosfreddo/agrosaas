#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar para compactar a entrega do Projeto FarmTech Solutions (FIAP - Fase 1)
Gera o arquivo entregavel_farmtech_fase1.zip contendo:
- Codigos Python (src/python/main.py)
- Codigos R (src/r/analysis.R e src/r/weather.R)
- Resumo do Artigo Embrapa (docs/resumo_artigo_embrapa.pdf)
- Link do Video (link_video.txt)
- Dataset (data/dados_fazenda.csv) e README.md
"""

import os
import zipfile

def criar_zip_entrega():
    nome_zip = "entregavel_farmtech_fase1.zip"
    diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
    caminho_zip = os.path.join(diretorio_raiz, nome_zip)

    arquivos_e_pastas = [
        "src/python/main.py",
        "src/r/analysis.R",
        "src/r/weather.R",
        "docs/resumo_artigo_embrapa.pdf",
        "data/dados_fazenda.csv",
        "link_video.txt",
        "README.md"
    ]

    print(f"[PACOTE] Criando pacote ZIP de entrega: {nome_zip}...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for rel_path in arquivos_e_pastas:
            full_path = os.path.join(diretorio_raiz, rel_path)
            if os.path.exists(full_path):
                zipf.write(full_path, arcname=rel_path)
                print(f"  [+] Adicionado: {rel_path}")
            else:
                print(f"  [!] Arquivo nao encontrado (ignorado): {rel_path}")

    print(f"\n[SUCESSO] Pacote ZIP gerado com sucesso em:\n   {caminho_zip}")
    print("Pronto para envio na plataforma FIAP!")

if __name__ == "__main__":
    criar_zip_entrega()
