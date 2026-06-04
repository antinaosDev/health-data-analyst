import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# 0. Agregar import difflib al inicio de normaliza_direcc
if 'import difflib' not in contenido:
    # Insertar justo debajo de import unicodedata que agregué en el refinamiento
    match_import = re.search(r'import unicodedata', contenido)
    if match_import:
        contenido = contenido.replace('import unicodedata', 'import unicodedata\n    import difflib')
        print("Agregado import difflib.")

# 1. Modificar asignar_comunidad
match_com = re.search(r'def asignar_comunidad\(texto\):(.*?)return "NO_ESPECIFICADO"', contenido, re.DOTALL)
if match_com:
    original = match_com.group(0)
    # Reemplazar el final "return NO_ESPECIFICADO" con el fallback
    fallback_com = """# 2. Fallback por Proximidad (Fuzzy)
        coincidencias = difflib.get_close_matches(texto, list(sector_a_comunidad.keys()), n=1, cutoff=0.6)
        if coincidencias:
            item_com = sector_a_comunidad[coincidencias[0]]
            if isinstance(item_com, list): return item_com[0]
            return item_com
        return "NO_ESPECIFICADO" """
    nuevo_com = original.replace('return "NO_ESPECIFICADO"', fallback_com)
    contenido = contenido.replace(original, nuevo_com)
    print("Modificado asignar_comunidad con fallback.")

# 2. Modificar asignar_distrito
match_dist = re.search(r'def asignar_distrito\(texto\):(.*?)return "NO_ESPECIFICADO"', contenido, re.DOTALL)
if match_dist:
    original = match_dist.group(0)
    # Reemplazar el final "return NO_ESPECIFICADO" con el fallback
    fallback_dist = """# 2. Fallback por Proximidad (Fuzzy)
        coincidencias = difflib.get_close_matches(texto, list(sector_a_distrito.keys()), n=1, cutoff=0.6)
        if coincidencias:
            item_dist = sector_a_distrito[coincidencias[0]]
            if isinstance(item_dist, list): return item_dist[0]
            return item_dist
        return "NO_ESPECIFICADO" """
    nuevo_dist = original.replace('return "NO_ESPECIFICADO"', fallback_dist)
    contenido = contenido.replace(original, nuevo_dist)
    print("Modificado asignar_distrito con fallback.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Actualización de Fuzzy completa.")
