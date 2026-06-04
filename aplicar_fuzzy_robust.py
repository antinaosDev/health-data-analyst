import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# 0. Agregar import difflib si no existe
if 'import difflib' not in contenido:
    contenido = contenido.replace('import unicodedata', 'import unicodedata\n    import difflib')
    print("Agregado import difflib.")

# 1. Modificar asignar_comunidad
match_com = re.search(r'(def asignar_comunidad\(texto\):.*?)(return "NO_ESPECIFICADO"\s*)', contenido, re.DOTALL)
if match_com:
    before = match_com.group(1)
    # Fallback
    fallback_com = """# 2. Fallback por Proximidad (Fuzzy)
        coincidencias = difflib.get_close_matches(texto, list(sector_a_comunidad.keys()), n=1, cutoff=0.6)
        if coincidencias:
            item_com = sector_a_comunidad[coincidencias[0]]
            if isinstance(item_com, list): return item_com[0]
            return item_com
        return "NO_ESPECIFICADO" """
    
    nuevo_bloque_com = before + fallback_com
    contenido = contenido.replace(match_com.group(0), nuevo_bloque_com)
    print("Modificado asignar_comunidad.")

# 2. Modificar asignar_distrito
match_dist = re.search(r'(def asignar_distrito\(texto\):.*?)(return "NO_ESPECIFICADO"\s*)', contenido, re.DOTALL)
if match_dist:
    before = match_dist.group(1)
    fallback_dist = """# 2. Fallback por Proximidad (Fuzzy)
        coincidencias = difflib.get_close_matches(texto, list(sector_a_distrito.keys()), n=1, cutoff=0.6)
        if coincidencias:
            item_dist = sector_a_distrito[coincidencias[0]]
            if isinstance(item_dist, list): return item_dist[0]
            return item_dist
        return "NO_ESPECIFICADO" """
    
    nuevo_bloque_dist = before + fallback_dist
    contenido = contenido.replace(match_dist.group(0), nuevo_bloque_dist)
    print("Modificado asignar_distrito.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Actualización de Fuzzy Robust completa.")
