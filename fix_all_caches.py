import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# 1. Fix normaliza_direcc
target_norm = r'def normaliza_direcc\(df\):'
rep_norm = "def normaliza_direcc(_df):\n    df = _df"

if re.search(target_norm, contenido):
    contenido = re.sub(target_norm, rep_norm, contenido)
    print("Normaliza_direcc corregido.")

# 2. Fix reporte_percapita
target_per = r'def reporte_percapita\(archivos\):'
rep_per = "def reporte_percapita(_archivos):\n    archivos = _archivos"

if re.search(target_per, contenido):
    contenido = re.sub(target_per, rep_per, contenido)
    print("Reporte_percapita corregido.")

# 3. Fix proc_csv
target_csv = r'def proc_csv\(archivo,sep=None\):'
rep_csv = "def proc_csv(_archivo,sep=None):\n    archivo = _archivo"

if re.search(target_csv, contenido):
    contenido = re.sub(target_csv, rep_csv, contenido)
    print("Proc_csv corregido.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Actualización de @st.cache_data completada.")
