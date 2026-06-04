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

# Extraer diccionarios del archivo para trazabilidad
with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

def extract_dict(name):
    match = re.search(f'{name} = \\{{(.*?)\\}}', contenido, re.DOTALL)
    if match:
        # Evaluar el cuerpo para obtener el diccionario
        try:
            return eval('{' + match.group(1) + '}')
        except:
            print(f"Error parseando {name}")
            return {}
    return {}

sector_a_comunidad = extract_dict('sector_a_comunidad')
sector_a_distrito = extract_dict('sector_a_distrito')

print(f"Diccionarios cargados. Com: {len(sector_a_comunidad)}, Dist: {len(sector_a_distrito)}")

df = pd.read_csv('nuevas_ubicaciones.tsv', sep='\t')
df['DIRECCION'] = df['Nombre_ubicacion']

df_res = normaliza_direcc(df)

output = []
output.append("=== ANALISIS DE FALLAS DETALLADO ===")

for idx, row in df_res.iterrows():
    esperado = row['Area_inf_centro']
    obtenido = row['AREA_INF_CENTRO']
    nombre = row['Nombre_ubicacion']
    direccion_norm = row['DIRECCION_NORM']
    distrito = row['DISTRITO']
    comunidad = row['COMUNIDAD']

    if esperado != obtenido:
        output.append(f"\n--- FALLA en: '{nombre}' ---")
        output.append(f"  DIRECCION_NORM: '{direccion_norm}'")
        output.append(f"  DISTRITO Asignado: '{distrito}'")
        output.append(f"  COMUNIDAD Asignada: '{comunidad}'")
        output.append(f"  Esperado: '{esperado}' | Obtenido: '{obtenido}'")

        match_dist = []
        for s, d in sector_a_distrito.items():
            if s in direccion_norm:
                match_dist.append(f"{s} -> {d}")
        if match_dist:
            output.append(f"  Coincidencias Distrito: {match_dist}")
        else:
            output.append(f"  Coincidencias Distrito: Ninguna")

        match_com = []
        for s, c in sector_a_comunidad.items():
            if s in direccion_norm:
                match_com.append(f"{s} -> {c}")
        if match_com:
            output.append(f"  Coincidencias Comunidad: {match_com}")

with open('reporte_fallas.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Reporte de fallas generado en reporte_fallas.txt")
