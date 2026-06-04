import difflib
import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

def extract_dict(name):
    match = re.search(f'{name} = \\{{(.*?)\\}}', contenido, re.DOTALL)
    if match:
        try:
            return eval('{' + match.group(1) + '}')
        except Exception as e:
             return {}
    return {}

S_A_DIST = extract_dict('sector_a_distrito')
lista_dist = list(S_A_DIST.keys())

# Pruebas estáticas populares que fallaban
casos = [
    "PEDRO CAYUQ",
    "HUINCA GUENCHUL",
    "RAMON ANCAMIL CARIRRINE",
    "RAYEN LAFKEN",
    "NAHUELMAN"
]

reporte = []
reporte.append("=== TEST DIFUZO MANUAL ===")
reporte.append(f"Llaves en diccionario Distrito: {len(lista_dist)}")

for c in casos:
    # 1. Coincidencia difusa
    coinc = difflib.get_close_matches(c.upper(), lista_dist, n=1, cutoff=0.6)
    if coinc:
        match_key = coinc[0]
        reporte.append(f"\nConsulta: '{c}'")
        reporte.append(f"  Match: '{match_key}' -> Distrito: '{S_A_DIST[match_key]}'")
    else:
        reporte.append(f"\nConsulta: '{c}' -> Sin Coincidencias (cutoff=0.6)")

with open('reporte_fuzzy_manual.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(reporte))

print("Reporte manual generado.")
