import pandas as pd
import re
import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# 1. Cargar datos nuevos
df_nuevos = pd.read_csv('nuevas_ubicaciones.tsv', sep='\t')
df_nuevos['Nombre_ubicacion_norm'] = df_nuevos['Nombre_ubicacion'].apply(lambda x: remove_accents(str(x).upper().strip()))

# 2. Generar nuevos elementos para sector_a_comunidad
with open('relaciones_centros.txt', 'r', encoding='utf-8') as f:
    contenido_centros = f.read()

repocura_sections = contenido_centros.split('--- Comunidades en Repocura por Centro ---')[1]
sub_sections = repocura_sections.split('\n\n')

repocura_dict = {}
for sec in sub_sections:
    sec = sec.strip()
    if not sec: continue
    lineas = sec.split('\n')
    header = lineas[0]
    centro = header.split(' (')[0].replace('Centro: ', '').strip()
    for l in lineas[1:]:
        comunidad = l.strip().replace('- ', '').strip()
        if comunidad:
            # Remover acentos de la clave para coincidir con DIRECCION_NORM
            clave = remove_accents(comunidad.upper())
            repocura_dict[clave] = centro

output = []

with open('detalles_analisis.txt', 'r', encoding='utf-8') as f:
    det_analisis = f.read()

output.append("--- sector_a_comunidad_updates ---")
comunidades_missing = re.findall(r'--- NUEVOS ELEMENTOS PARA sector_a_comunidad ---\n(.*?)--- NUEVOS ELEMENTOS PARA sector_a_distrito ---', det_analisis, re.DOTALL)[0]

# Procesar 'comunidades_missing' para remover acentos de las llaves
com_lines = comunidades_missing.strip().split('\n')
for line in com_lines:
    line = line.strip()
    if ':' in line:
        k, v = line.split(':', 1)
        k_clean = remove_accents(eval(k.strip()))
        output.append(f'    "{k_clean}": {v.strip()},')

output.append("\n--- sector_a_distrito_updates ---")
distritos_missing = re.findall(r'--- NUEVOS ELEMENTOS PARA sector_a_distrito ---\n(.*)', det_analisis, re.DOTALL)[0]

# Procesar 'distritos_missing' para remover acentos
dist_lines = distritos_missing.strip().split('\n')
for line in dist_lines:
    line = line.strip()
    if ':' in line:
        k, v = line.split(':', 1)
        k_clean = remove_accents(eval(k.strip()))
        output.append(f'    "{k_clean}": {v.strip()},')

output.append("\n--- NUEVOS DICCIONARIOS CENTROS ---")
output.append("""
distrito_a_centro = {
    "cholchol": "Cesfam Cholchol",
    "tranahuillin": "Cesfam Cholchol",
    "rapahue": "PSR Malalche",
    "carirriñe": "PSR Malalche"
}
""")

output.append("repocura_comunidad_a_centro = {")
for k, v in repocura_dict.items():
    output.append(f'    "{k}": "{v}",')
output.append("}")

with open('codigo_generado.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Codigo generado correctamente con normalizacion de acentos.")
