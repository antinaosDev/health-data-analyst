import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# 1. Definir el bloque limpio a insertar
bloque_limpio = """    def asignar_comunidad(texto):
        texto = texto.upper()
        for sector, distrito in sorted(sector_a_comunidad.items(), key=lambda x: len(x[0]), reverse=True):
            if sector in texto:
                if isinstance(distrito, list): return distrito[0]
                return distrito
        # 2. Fallback por Proximidad (Fuzzy)
        coincidencias = difflib.get_close_matches(texto, list(sector_a_comunidad.keys()), n=1, cutoff=0.6)
        if coincidencias:
            item_com = sector_a_comunidad[coincidencias[0]]
            if isinstance(item_com, list): return item_com[0]
            return item_com
        return "NO_ESPECIFICADO"

    def asignar_distrito(texto):
        texto = texto.upper()
        for sector, distrito in sorted(sector_a_distrito.items(), key=lambda x: len(x[0]), reverse=True):
            if sector in texto:
                if isinstance(distrito, list): return distrito[0]
                return distrito
        # 2. Fallback por Proximidad (Fuzzy)
        coincidencias = difflib.get_close_matches(texto, list(sector_a_distrito.keys()), n=1, cutoff=0.6)
        if coincidencias:
            item_dist = sector_a_distrito[coincidencias[0]]
            if isinstance(item_dist, list): return item_dist[0]
            return item_dist
        return "NO_ESPECIFICADO"

    distrito_a_centro"""

# 2. Buscar la frontera desde def asignar_comunidad hasta distrito_a_centro
# Usamos un regex que abrace todo lo intermedio
pattern = r'def asignar_comunidad\(texto\):(.*?)distrito_a_centro'
match = re.search(pattern, contenido, re.DOTALL)

if match:
    contenido = re.sub(pattern, bloque_limpio, contenido, flags=re.DOTALL)
    print("Bloque de funciones reconstruido.")
else:
    print("No se pudo hallar el patrón para reconstruir.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Reconstrucción finalizada.")
