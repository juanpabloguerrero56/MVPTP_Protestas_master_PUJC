import random
import math
import pandas as pd
from collections import defaultdict
from itertools import product
import os

# ======================
# CONFIGURACIÓN
# ======================
RUTA_EXCEL = r"C:\Users\juanp\Documentos\MODELO MVPTP TESIS\Data barrios cali.xlsx"
RUTA_SALIDA = r"C:\Users\juanp\Documentos\MODELO MVPTP TESIS\Instancias Cali"

BETA_0 = 0.945736477
BETA_1 = 1.136916857

os.makedirs(RUTA_SALIDA, exist_ok=True)
random.seed(123)

# ======================
# DEPÓSITOS
# ======================
DEPOSITOS = {
    "D1": (3.44437361502593, -76.5279282954603),
    "D2": (3.47510091489602, -76.4902315682344),
    "D3": (3.41525202277559, -76.5520992996521),
    "D4": (3.42694495609322, -76.4840529301288),
}

# ======================
# FUNCIONES AUXILIARES
# ======================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def haversine_adjusted(lat1, lon1, lat2, lon2):
    return BETA_0 + BETA_1 * haversine(lat1, lon1, lat2, lon2)

def seleccionar_focos(df, n_focos):

    tau = math.ceil(math.sqrt(n_focos))
    comunas_disponibles = df["Comuna"].unique().tolist()

    comunas = random.sample(comunas_disponibles, tau)

    # Calcular cupos ideales
    base = n_focos // tau
    extra = n_focos % tau

    # Capacidad real por comuna
    capacidad = {
        c: len(df[df["Comuna"] == c])
        for c in comunas
    }

    # Inicializar cupos
    cupos = {c: base for c in comunas}

    # Asignar extras solo a comunas con capacidad suficiente
    comunas_ordenadas = sorted(
        comunas,
        key=lambda c: capacidad[c],
        reverse=True
    )

    asignados = 0
    for c in comunas_ordenadas:
        if asignados >= extra:
            break
        if capacidad[c] >= base + 1:
            cupos[c] += 1
            asignados += 1

    # Validación final
    for c in comunas:
        if cupos[c] > capacidad[c]:
            raise ValueError(f"La comuna {c} no tiene suficiente capacidad.")

    # Selección final de focos respetando cupos
    focos_list = []

    for c in comunas:
        barrios = df[df["Comuna"] == c].sample(
            n=cupos[c],
            replace=False
        )
        focos_list.append(barrios)

    focos_df = pd.concat(focos_list).reset_index(drop=True)

    return focos_df, tau


def generar_demanda_y_servicio(ids):
    niveles = [25, 50, 75, 100, 125]
    dem, s = {}, {}
    for i in ids:
        d = random.choice(niveles)
        gamma = random.uniform(0.014, 0.020)
        dem[i] = d
        s[i] = round(d * gamma, 2)
    return dem, s

def generar_mu(dem):
    mu = {}
    for i, d in dem.items():
        if d == 25:
            mu_k2 = 1
        elif d in (50, 75):
            mu_k2 = random.randint(1, 2)
        else:
            mu_k2 = random.randint(2, 3)
        mu[i] = {1: 0, 2: mu_k2}
    return mu

def generar_ventanas(ids):

    # Generar alpha
    alpha = {i: random.randint(6, 14) for i in ids}

    # 2 Definir grupos y probabilidades
    grupos = ["G1", "G2", "G3"]
    probabilidades = [0.2, 0.3, 0.5]

    beta = {}

    for i in ids:

        # 3 Seleccionar grupo según probabilidad
        grupo = random.choices(grupos, weights=probabilidades, k=1)[0]

        # 4Definir incremento según grupo
        if grupo == "G1":
            delta = random.choice([4, 5])
        elif grupo == "G2":
            delta = random.choice([6, 7])
        else:  # G3
            delta = random.choice([8, 9, 10])

        beta[i] = alpha[i] + delta

    return alpha, beta


def normalizar_por_max(dic):
    m = max(dic.values())
    return {k: v / m if m > 0 else 0 for k, v in dic.items()}

def generar_prioridades(nodos):
    INF = {i: random.uniform(100, 1500) for i in nodos}
    INF_n = normalizar_por_max(INF)
    return {
        i: round(
            0.5 * nodos[i]["RD"] +
            0.3 * nodos[i]["DP"] +
            0.2 * INF_n[i],
            3
        )
        for i in nodos
    }

def generar_clusteres_por_comuna(focos_df):

    clusteres = []

    comunas_presentes = focos_df["Comuna"].unique().tolist()

    for idx, comuna in enumerate(comunas_presentes, start=1):

        ids = focos_df[focos_df["Comuna"] == comuna]["ID"].tolist()

        clusteres.append({
            "id": idx,
            "comuna": comuna,
            "nodos": ids
        })

    return clusteres



# ======================
# GENERAR INSTANCIA
# ======================
def generar_instancia(df, num_focos, nombre_archivo):

    #---SELECCION DE NODOS-----
    focos_df, tau = seleccionar_focos(df, num_focos)

    map_excel_a_F = {}
    nodos = {}

    for i, row in focos_df.iterrows():

        nombre_f = f"F{i+1}"
        excel_id = row["ID"]

        map_excel_a_F[excel_id] = nombre_f

        nodos[nombre_f] = {
            "lat": row["Latitud"],
            "lon": row["Longitud"],
            "comuna": row["Comuna"],
            "RD": row["RD"],
            "DP": row["DP"],
            "ID": excel_id
        }

    # ----CREAR CLUSTERES----
    clusteres_raw = generar_clusteres_por_comuna(focos_df)

    clusteres = []

    for c in clusteres_raw:

        nodos_F = [map_excel_a_F[x] for x in c["nodos"]]

        clusteres.append({
            "id": c["id"],
            "comuna": c["comuna"],
            "nodos": nodos_F
        })

    #----CALCULAR DISTANCIAS ENTRE NODOS-----
    coords = {i: (d["lat"], d["lon"]) for i, d in nodos.items()}
    coords.update(DEPOSITOS)

    dist = {
        (i, j): round(0 if i == j else haversine_adjusted(*coords[i], *coords[j]), 2)
        for i, j in product(coords, coords)
    }


    #------DEFINIR PARAMETROS VARIABLES-------
    dem, s = generar_demanda_y_servicio(nodos)
    alpha, beta = generar_ventanas(nodos)
    P = generar_prioridades(nodos)
    mu = generar_mu(dem)

    ruta = os.path.join(RUTA_SALIDA, nombre_archivo)

# ====================== # ESCRIBIR ARCHIVO .DAT # ======================

    with open(ruta, "w", encoding="utf-8") as f:

        f.write("##------CONJUNTOS\n")
        # Conjuto de Depósitos y tipos de vehículos
        f.write("set D := " + " ".join(DEPOSITOS) + ";\n")
        f.write("set K := 1 2;\n\n")
        
        # Conjunto de focos
        f.write("set I := ")
        f.write(" ".join(nodos.keys()))
        f.write(";\n\n")

        # Comentarios informativos
        for nombre_f, datos in nodos.items():
            f.write(
                f"# {nombre_f} -> Excel {datos['ID']}, "
                f"Comuna {datos['comuna']}\n"
            )

        f.write("\n")

        # ---------------------
        # Clusteres
        # ---------------------
        f.write("# Clústeres\n")
        f.write("set C := ")
        f.write(" ".join(f"C{c['id']}" for c in clusteres))
        f.write(";\n")

        for c in clusteres:

            f.write(f"set IC[C{c['id']}] := ")
            f.write(" ".join(c["nodos"]))
            f.write(";\n")

        # Vehículos por depósito
        f.write("\n")
        f.write("# Número de vehículos por tipo y depósito\n")
        f.write("set R[D1,1] := V1 V2 V3 V4;\n")
        f.write("set R[D1,2] := K1 K2;\n")
        f.write("set R[D2,1] := V5 V6 V7 V8;\n")
        f.write("set R[D2,2] := K3;\n")
        f.write("set R[D3,1] := V9 V10 V11 V12;\n")
        f.write("set R[D3,2] := K4;\n")
        f.write("set R[D4,1] := V13 V14 V15 V16;\n")
        f.write("set R[D4,2] := K5 K6;\n\n")

        # Parametros fijos
        f.write("##------PARAMETROS GLOBALES\n")
        f.write("param Vel := 25;\n\n")
        f.write("##------CAPACIDAD DE VEHÍCULOS (agentes que pueden transportar)\n")
        f.write("param q :=\n1 5\n2 10\n;\n\n")
        f.write("##------POLICÍAS DISPONIBLES en cada depósito\n")
        f.write("param h :=\nD1 40\nD2 30\nD3 30\nD4 40\n;\n\n")
        f.write("##------VEHÍCULOS DISPONIBLES por tipo y depósito\n")
        f.write("param v:\n\t1\t2 :=\n")
        f.write("D1\t4\t2\nD2\t4\t1\nD3\t4\t1\nD4\t4\t2\n;\n\n")

      
        # Distancias
        f.write("##-----DISTANCIAS ENTRE NODOS [km]\n")
        f.write("param dist:\n\t" + "\t".join(coords) + " :=\n")
        for i in coords:
            f.write(i + "\t" + "\t".join(str(dist[(i, j)]) for j in coords) + "\n")
        f.write(";\n\n")

        # -----------------------------
        # DEMANDA DE POLICÍAS
        # -----------------------------
        f.write("#### DEMANDA DE POLICÍAS (por nodo i)\n")
        f.write("param dem :=\n")
        for k2, v in dem.items():
            f.write(f"{k2} {v}\n")
        f.write(";\n\n")


        # -----------------------------
        # DEMANDA DE VEHÍCULOS
        # -----------------------------
        f.write("#### DEMANDA DE VEHÍCULOS (por tipo)\n")
        f.write("param mu:\n")
        f.write("    1   2 :=\n")

        for i in nodos:
            f.write(f" {i}  {mu[i][1]}  {mu[i][2]}\n")

        f.write(";\n\n")


        # -----------------------------
        # TIEMPOS DE SERVICIO
        # -----------------------------
        f.write("#### TIEMPOS DE SERVICIO [horas]\n")
        f.write("param s :=\n")
        for k2, v in s.items():
            f.write(f"{k2} {v:.2f}\n")
        f.write(";\n\n")


        # -----------------------------
        # VENTANAS DE TIEMPO
        # -----------------------------
        f.write("#### VENTANAS DE TIEMPO [horas]\n")

        f.write("param alpha :=\n")
        for k2, v in alpha.items():
            f.write(f"{k2} {v}\n")
        f.write(";\n\n")

        f.write("param beta :=\n")
        for k2, v in beta.items():
            f.write(f"{k2} {v}\n")
        f.write(";\n\n")


        # -----------------------------
        # PRIORIDAD
        # -----------------------------
        f.write("#### PRIORIDAD DE LOS NODOS\n")
        f.write("param P :=\n")
        for k2, v in P.items():
            f.write(f"{k2} {v:.3f}\n")
        f.write(";\n\n")


# ======================
# GENERACIÓN MASIVA
# ======================
df = pd.read_excel(RUTA_EXCEL)
df["Comuna"] = df["Comuna"].astype(int)

INSTANCIAS_POR_TAM = 5
TAMANOS = [8, 12, 16, 20, 24, 28]

total_instancias = 0

for n in TAMANOS:

    generadas_n = 0

    for rep in range(1, INSTANCIAS_POR_TAM + 1):

        random.seed(1000 * n + rep)

        nombre = f"MVPTP_CALI_{n}_{rep}.dat"

        try:
            generar_instancia(df, n, nombre)
            generadas_n += 1
            total_instancias += 1

        except Exception as e:
            print(f"[ERROR] Tamaño {n}, instancia {rep}: {e}")

    print(f"{generadas_n} instancias de tamaño {n} generadas correctamente.")

print(f"\nTotal de instancias generadas: {total_instancias}")
