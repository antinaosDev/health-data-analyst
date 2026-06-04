import pandas as pd
import re
import codecs

# 1. Cargar datos nuevos
df_nuevos = pd.read_csv('nuevas_ubicaciones.tsv', sep='\t')
df_nuevos['Nombre_ubicacion_norm'] = df_nuevos['Nombre_ubicacion'].str.upper().str.strip()

output_lines = []
output_lines.append(f"Total registros nuevos: {len(df_nuevos)}")

# 2. Leer analisis_func.py para extraer diccionarios
with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

def extraer_diccionario(nombre_dict):
    match = re.search(r'{} = \{{(.*?)\}}'.format(nombre_dict), contenido, re.DOTALL)
    if not match:
        return {}
    dict_str = match.group(1)
    # Limpiar y evaluar
    lineas = dict_str.split('\n')
    d = {}
    for linea in lineas:
        linea = linea.strip()
        if not linea or linea.startswith('#'):
            continue
        try:
            # Reemplazar comas al final
            linea = linea.rstrip(',')
            # Evaluar linea como 'key': 'value' o 'key': ['value']
            if ':' not in linea:
                continue
            k, v = linea.split(':', 1)
            k = eval(k.strip())
            v = eval(v.strip())
            d[k] = v
        except Exception as e:
            pass
    return d

sector_a_comunidad = extraer_diccionario('sector_a_comunidad')
sector_a_distrito = extraer_diccionario('sector_a_distrito')

output_lines.append(f"Elementos en sector_a_comunidad: {len(sector_a_comunidad)}")
output_lines.append(f"Elementos en sector_a_distrito: {len(sector_a_distrito)}")

# 3. Comparar
output_lines.append("\n--- ANALISIS ---")

# A. Comunidad
output_lines.append("\nUbicaciones en TSV:")
for idx, row in df_nuevos.iterrows():
    nombre = row['Nombre_ubicacion_norm']
    encuentra_com = False
    for k, v in sector_a_comunidad.items():
        if k in nombre:
            encuentra_com = True
            break
    
    encuentra_dist = False
    for k, v in sector_a_distrito.items():
        if k in nombre:
            encuentra_dist = True
            break

    if not encuentra_com or not encuentra_dist:
        output_lines.append(f"FALTA MAPPED: {row['Nombre_ubicacion']} | Sector: {row['Sector']} | Distrito: {row['Distrito']} | Centro: {row['Area_inf_centro']}")

# 4. Generar Diccionario para Area_inf_centro
output_lines.append("\n--- PROPUESTA DICCIONARIO AREA_INF_CENTRO ---")
dict_centro = {}
for idx, row in df_nuevos.iterrows():
    nombre = row['Nombre_ubicacion_norm']
    centro = row['Area_inf_centro']
    if nombre not in dict_centro:
        dict_centro[nombre] = centro

output_lines.append("sector_a_centro = {")
for k, v in dict_centro.items():
    output_lines.append(f'    "{k}": "{v}",')
output_lines.append("}")

# 5. Generar actualizaciones para sector_a_comunidad y sector_a_distrito
output_lines.append("\n--- NUEVOS ELEMENTOS PARA sector_a_comunidad ---")
nuevos_com = {}
for idx, row in df_nuevos.iterrows():
    nombre = row['Nombre_ubicacion_norm']
    actual = row['Nombre_ubicacion']
    if not any(k in nombre for k in sector_a_comunidad.keys()):
        nuevos_com[nombre] = actual

for k, v in nuevos_com.items():
    output_lines.append(f'    "{k}": "{v}",')

output_lines.append("\n--- NUEVOS ELEMENTOS PARA sector_a_distrito ---")
nuevos_dist = {}
for idx, row in df_nuevos.iterrows():
    nombre = row['Nombre_ubicacion_norm']
    distrito = row['Distrito'].lower()
    if not any(k in nombre for k in sector_a_distrito.keys()):
        nuevos_dist[nombre] = distrito

for k, v in nuevos_dist.items():
    output_lines.append(f'    "{k}": "{v}",')

# Guardar a archivo
with open('detalles_analisis.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("Analisis completado y guardado en detalles_analisis.txt")
