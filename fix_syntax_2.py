import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# 1. Agregar coma en sector_a_distrito si falta
match_dist = re.search(r'("EL AROMO": "repocura")(\s*# --- NUEVOS ELEMENTOS ---)', contenido, re.DOTALL)
if match_dist:
    sub = match_dist.group(1) + ',' + match_dist.group(2)
    contenido = contenido.replace(match_dist.group(0), sub)
    print("Corregido coma en sector_a_distrito (EL AROMO)")
else:
    print("No se encontro target para sector_a_distrito")

# Adicionalmente, asegurar que NO haya otros errores de coma
# si es que quedaron mas dicts sin comas al final de su bloque original.
# Pero el traceback mostro especificamente este punto.

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Sintaxis corregida 2.")
