
import csv
import math

# "talhoes" é uma lista que guarda cada talhão como um dicionário
talhoes = []
next_id = 1  # id incremental para cada talhão novo

# Função para calcular área conforme tipo de forma
def calcular_area(t):
    tipo = t.get("tipo_area", "retangulo")
    if tipo == "retangulo":
        # área = comprimento * largura
        return float(t.get("comprimento", 0.0)) * float(t.get("largura", 0.0))
    elif tipo == "trapezio":
        # trapézio: (base_maior + base_menor) * altura / 2
        return (float(t.get("base_maior", 0.0)) + float(t.get("base_menor", 0.0))) * float(t.get("altura", 0.0)) / 2.0
    else:
        return 0.0

# Função para calcular insumo necessário (em mL e em L)
def calcular_insumo(t):
    taxa_ml_por_m = float(t.get("taxa_ml_por_m", 0.0))   # mL por metro linear
    numero_linhas = int(t.get("numero_linhas", 1))       # número de ruas/linhas
    comprimento = float(t.get("comprimento", 0.0))      # comprimento em metros
    total_ml = taxa_ml_por_m * numero_linhas * comprimento
    total_l = total_ml / 1000.0
    return {"mL": total_ml, "L": total_l}

# Criar um novo talhão pedindo dados ao usuário
def criar_talhao():
    global next_id
    print("\n--- Criar talhão ---")
    cultura = input("Cultura (ex: Milho / Soja): ").strip()
    # para o trabalho: vamos aceitar retangulo ou trapezio
    tipo = input("Tipo de área (retangulo/trapezio): ").strip().lower()
    t = {"id": next_id, "cultura": cultura, "tipo_area": tipo}

    if tipo == "retangulo":
        t["comprimento"] = float(input("Comprimento (m): "))
        t["largura"] = float(input("Largura (m): "))
    elif tipo == "trapezio":
        t["base_maior"] = float(input("Base maior (m): "))
        t["base_menor"] = float(input("Base menor (m): "))
        t["altura"] = float(input("Altura (m): "))
        # como 'comprimento' precisamos para calcular insumo linear:
        t["comprimento"] = float(input("Comprimento (m) (comprimento da lavoura): "))
    else:
        print("Tipo não reconhecido. Salvando com área 0.")

    t["produto"] = input("Produto (ex: Fosfato): ").strip()
    t["taxa_ml_por_m"] = float(input("Taxa do produto (mL por metro linear): "))
    t["numero_linhas"] = int(input("Número de ruas/linhas na lavoura: "))

    talhoes.append(t)
    print(f"Talhão criado com id = {next_id}")
    next_id += 1

# Listar todos os talhões e mostrar área e insumo
def listar_talhoes():
    if not talhoes:
        print("Nenhum talhão cadastrado.")
        return
    print("\n--- Lista de Talhões ---")
    for t in talhoes:
        area = calcular_area(t)
        insumo = calcular_insumo(t)
        print(f"ID {t['id']} | {t['cultura']} | Tipo: {t['tipo_area']}")
        print(f"  Área (m²): {area:.2f}")
        print(f"  Produto: {t.get('produto')} — Necessário: {insumo['mL']:.2f} mL ({insumo['L']:.3f} L)")
        print("-" * 30)

# Atualizar talhão por ID
def atualizar_talhao():
    id_busca = int(input("Digite o ID do talhão a atualizar: "))
    for t in talhoes:
        if t["id"] == id_busca:
            print("Encontrado. Pressione Enter para manter o valor atual.")
            for chave in ["cultura","tipo_area","comprimento","largura","base_maior","base_menor","altura","produto","taxa_ml_por_m","numero_linhas"]:
                atual = t.get(chave, "")
                novo = input(f"{chave} (atual: {atual}): ")
                if novo.strip() != "":
                    # tenta converter para número quando faz sentido
                    if chave in ["comprimento","largura","base_maior","base_menor","altura","taxa_ml_por_m"]:
                        t[chave] = float(novo)
                    elif chave == "numero_linhas":
                        t[chave] = int(novo)
                    else:
                        t[chave] = novo
            print("Talhão atualizado.")
            return
    print("ID não encontrado.")

# Deletar talhão por ID
def deletar_talhao():
    id_del = int(input("ID do talhão a deletar: "))
    global talhoes
    tam_antes = len(talhoes)
    talhoes = [t for t in talhoes if t["id"] != id_del]
    if len(talhoes) < tam_antes:
        print("Talhão removido.")
    else:
        print("ID não encontrado; nada removido.")

# Salvar para CSV
def salvar_csv(nome="talhoes.csv"):
    # vamos garantir as colunas em ordem previsível
    campos = ["id","cultura","tipo_area","comprimento","largura","base_maior","base_menor","altura","produto","taxa_ml_por_m","numero_linhas"]
    with open(nome, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for t in talhoes:
            # escrever vazio quando chave não existir
            row = {c: t.get(c, "") for c in campos}
            writer.writerow(row)
    print(f"Salvo em {nome}")

# Carregar de CSV
def carregar_csv(nome="talhoes.csv"):
    global talhoes, next_id
    try:
        with open(nome, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            talhoes = []
            for row in reader:
                # converter tipos que deveriam ser números
                for key in ["id","comprimento","largura","base_maior","base_menor","altura","taxa_ml_por_m","numero_linhas"]:
                    if row.get(key, "") != "":
                        # id e numero_linhas -> int
                        if key in ["id","numero_linhas"]:
                            row[key] = int(float(row[key]))
                        else:
                            row[key] = float(row[key])
                talhoes.append(row)
        ids = [t["id"] for t in talhoes if "id" in t]
        next_id = max(ids) + 1 if ids else 1
        print(f"Arquivo {nome} carregado. {len(talhoes)} talhões.")
    except FileNotFoundError:
        print("Arquivo não encontrado.")

# Menu principal com loop e decisões
def menu():
    while True:
        print("\n=== FarmTech Menu ===")
        print("1 - Criar talhão")
        print("2 - Listar talhões")
        print("3 - Atualizar talhão")
        print("4 - Deletar talhão")
        print("5 - Salvar em CSV")
        print("6 - Carregar CSV")
        print("0 - Sair")
        escolha = input("Escolha: ").strip()
        if escolha == "1":
            criar_talhao()
        elif escolha == "2":
            listar_talhoes()
        elif escolha == "3":
            atualizar_talhao()
        elif escolha == "4":
            deletar_talhao()
        elif escolha == "5":
            salvar_csv()
        elif escolha == "6":
            carregar_csv()
        elif escolha == "0":
            print("Saindo. Até mais!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
