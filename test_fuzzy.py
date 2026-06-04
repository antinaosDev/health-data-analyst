import difflib
import pandas as pd
import sys
import re
import codecs

# Bulletproof Streamlit Mock
import streamlit as st

def mock_decorator(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    return lambda f: f

st.cache_data = mock_decorator
st.cache_resource = mock_decorator

sys.path.append('.')
from analisis_func import normaliza_direcc

# Extraer diccionarios del archivo para probar difflib
with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

def extract_dict(name):
    match = re.search(f'{name} = \\{{(.*?)\\}}', contenido, re.DOTALL)
    if match:
        try:
            return eval('{' + match.group(1) + '}')
        except:
            print(f"Error parseando {name}")
            return {}
    return {}

S_A_COM = extract_dict('sector_a_comunidad')
S_A_DIST = extract_dict('sector_a_distrito')

print(f"Diccionarios cargados. Com: {len(S_A_COM)}, Dist: {len(S_A_DIST)}")

df = pd.read_csv('nuevas_ubicaciones.tsv', sep='\t')
df['DIRECCION'] = df['Nombre_ubicacion']
df_res = normaliza_direcc(df)

faltantes = df_res[df_res['AREA_INF_CENTRO'] == 'NO_ESPECIFICADO']

output = []
output.append("=== PRUEBA DE COINCIDENCIAS DIFUSA (difflib) ===")
output.append(f"Casos No Identificados: {len(faltantes)}")

# Lista de llaves
lista_dist = list(S_A_DIST.keys())

for idx, row in faltantes.iterrows():
    nombre = row['Nombre_ubicacion']
    dir_norm = row['DIRECCION_NORM']
    
    # Coincidencia difusa en Distrito
    coinc = difflib.get_close_matches(dir_norm, lista_dist, n=1, cutoff=0.6)
    
    if coinc:
         recom_key = coinc[0]
         recom_val = S_A_DIST[recom_key]
         output.append(f"\n- '{nombre}' (NORM: {dir_norm})")
         output.append(f"  Fuzzy Match en Distrito: '{recom_key}' -> Distrito: '{recom_val}'")

with open('reporte_fuzzy.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Reporte de fuzzy generado.")
print(f"Faltantes procesados: {len(faltantes)}")
