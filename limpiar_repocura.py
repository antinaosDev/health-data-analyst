import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# 1. Cargar codigo generado para extraer el diccionario limpio
with open('codigo_generado.txt', 'r', encoding='utf-8') as f:
    lineas = f.readlines()

items_repocura = []
en_repocura = False
for l in lineas:
    if 'repocura_comunidad_a_centro = {' in l:
        en_repocura = True
        continue
    if en_repocura and '}' in l:
        break
    if en_repocura and '"' in l:
        items_repocura.append(l.strip())

# print(items_repocura)

# Construir cuerpo limpio
cuerpo_limpio = ",\n    ".join([f'    "{eval(l.split(":")[0])}": "{eval(l.split(":")[1].rstrip(","))}"' for l in items_repocura])
# print(cuerpo_limpio)

# 2. Reemplazar en analisis_func.py
# Buscar el bloque entero repocura_comunidad_a_centro = { ... }
# Como está corrupto, usar regex flexible

pattern = r'repocura_comunidad_a_centro = \{.*?\}'
replacement = 'repocura_comunidad_a_centro = {\n    ' + cuerpo_limpio + '\n    }'

match = re.search(pattern, contenido, re.DOTALL)
if match:
    contenido = re.sub(pattern, replacement, contenido, flags=re.DOTALL)
    print("Diccionario repocura_comunidad_a_centro limpiado.")
else:
    print("No se encontro repocura_comunidad_a_centro")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Actualizado.")
