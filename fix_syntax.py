import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# 1. Agregar coma en sector_a_comunidad si falta
match_com = re.search(r'("EL AROMO": "El Aromo")(\s*# --- NUEVOS ELEMENTOS ---)', contenido, re.DOTALL)
if match_com:
    sub = match_com.group(1) + ',' + match_com.group(2)
    contenido = contenido.replace(match_com.group(0), sub)
    print("Corregido coma en sector_a_comunidad")

# 2. Agregar coma en sector_a_distrito si falta
match_dist = re.search(r'("SCH":"cholchol")(\s*# --- NUEVOS ELEMENTOS ---)', contenido, re.DOTALL)
if match_dist:
    sub = match_dist.group(1) + ',' + match_dist.group(2)
    contenido = contenido.replace(match_dist.group(0), sub)
    print("Corregido coma en sector_a_distrito")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Sintaxis corregida.")
