import codecs

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# 1. Agregar coma a "EL AROMO": "PSR Huamaqui"
target_comma = '"EL AROMO": "PSR Huamaqui"'
rep_comma = '"EL AROMO": "PSR Huamaqui",'

if target_comma in contenido:
    contenido = contenido.replace(target_comma, rep_comma)
    print("Coma agregada.")

# 2. Indentar los nuevos items
# Buscar el bloque que inserte
target_block = """    "JUAN ANCALLE": "PSR HUENTELAR",
    "JUAN COLIPI": "PSR HUENTELAR",
    "HUENUL LLANCAN": "PSR HUENTELAR",
    "DOMIN COLIN": "PSR HUENTELAR",
    "JUAN MAURICIO HUAIQUIAN": "PSR HUENTELAR",
    "LEVIO HUENCHUAL": "PSR HUENTELAR",
    "PEDRO MARIN CALFUCURA": "PSR HUENTELAR",
    "AGUSTIN PAINAQUEO": "PSR HUENTELAR",
    "ALBERTO VEJAR": "PSR HUENTELAR",
    "VIUDA DE JOSE NANCULEF": "PSR HUENTELAR","""

# En el archivo, están sin el indentado de 4 espacios (líneas 1335-1344 están como "JUAN ANCALLE")
search_block = """    "JUAN ANCALLE": "PSR HUENTELAR",
    "JUAN COLIPI": "PSR HUENTELAR",
    "HUENUL LLANCAN": "PSR HUENTELAR",
    "DOMIN COLIN": "PSR HUENTELAR",
    "JUAN MAURICIO HUAIQUIAN": "PSR HUENTELAR",
    "LEVIO HUENCHUAL": "PSR HUENTELAR",
    "PEDRO MARIN CALFUCURA": "PSR HUENTELAR",
    "AGUSTIN PAINAQUEO": "PSR HUENTELAR",
    "ALBERTO VEJAR": "PSR HUENTELAR",
    "VIUDA DE JOSE NANCULEF": "PSR HUENTELAR","""

# Espera, en el archivo (L1335) es "JUAN ANCALLE" (sin espacios al inicio o con 4?)
# En L1335 se lee: `1335:     "JUAN ANCALLE": "PSR HUENTELAR",`
# El prefijo es `    ` (4 espacios). Pero la linea anterior `1334:         "EL AROMO": "PSR Huamaqui"` tiene 8 espacios!
# Así que los nuevos items tienen 4 espacios, necesitan 8!
# Vamos a reemplazar el bloque agregando 4 espacios más a cada línea.

search_items = [
    '"JUAN ANCALLE": "PSR HUENTELAR",',
    '"JUAN COLIPI": "PSR HUENTELAR",',
    '"HUENUL LLANCAN": "PSR HUENTELAR",',
    '"DOMIN COLIN": "PSR HUENTELAR",',
    '"JUAN MAURICIO HUAIQUIAN": "PSR HUENTELAR",',
    '"LEVIO HUENCHUAL": "PSR HUENTELAR",',
    '"PEDRO MARIN CALFUCURA": "PSR HUENTELAR",',
    '"AGUSTIN PAINAQUEO": "PSR HUENTELAR",',
    '"ALBERTO VEJAR": "PSR HUENTELAR",',
    '"VIUDA DE JOSE NANCULEF": "PSR HUENTELAR",'
]

for item in search_items:
    contenido = contenido.replace("    " + item, "        " + item)

print("Indetación corregida.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Sintaxis reparada.")
