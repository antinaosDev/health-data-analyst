import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# 1. Insertar remove_accents helper inside normaliza_direcc
# Buscar el inicio de normaliza_direcc
match_norm = re.search(r'def normaliza_direcc\(df\):(.*?)def asignar_comunidad', contenido, re.DOTALL)
if match_norm:
    # Agregar remove_accents al inicio del bloque
    helper_code = """
    import unicodedata
    def remove_accents(input_str):
        if not isinstance(input_str, str): return ""
        nfkd_form = unicodedata.normalize('NFD', input_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

"""
    # Insertar justo después de def normaliza_direcc(df):
    bloque = match_norm.group(1)
    if 'def remove_accents' not in bloque:
        # Reemplazar el primer bloque antes de asignar_comunidad
        search_target = 'def normaliza_direcc(df):'
        contenido = contenido.replace(search_target, search_target + helper_code)
        print("Agregado remove_accents helper.")

# 2. Refinar asignar_comunidad (Longest Match First)
match_com = re.search(r'def asignar_comunidad\(texto\):.*?return "NO_ESPECIFICADO"', contenido, re.DOTALL)
if match_com:
    original = match_com.group(0)
    refinado = """def asignar_comunidad(texto):
        texto = texto.upper()
        # Ordenar por longitud de clave descendente para evitar falsas coincidencias parciales
        for sector, distrito in sorted(sector_a_comunidad.items(), key=lambda x: len(x[0]), reverse=True):
            if sector in texto:
                if isinstance(distrito, list): return distrito[0]
                return distrito
        return "NO_ESPECIFICADO" """
    contenido = contenido.replace(original, refinado)
    print("Refinado asignar_comunidad.")

# 3. Refinar asignar_distrito (Longest Match First)
match_dist = re.search(r'def asignar_distrito\(texto\):.*?return "NO_ESPECIFICADO"', contenido, re.DOTALL)
if match_dist:
    original = match_dist.group(0)
    refinado = """def asignar_distrito(texto):
        texto = texto.upper()
        # Ordenar por longitud de clave descendente
        for sector, distrito in sorted(sector_a_distrito.items(), key=lambda x: len(x[0]), reverse=True):
            if sector in texto:
                if isinstance(distrito, list): return distrito[0]
                return distrito
        return "NO_ESPECIFICADO" """
    contenido = contenido.replace(original, refinado)
    print("Refinado asignar_distrito.")

# 4. Refinar asignar_centro (Lookup con remove_accents)
match_centro = re.search(r'def asignar_centro\(row\):.*?if dist == \'repocura\':.*?return repocura_comunidad_a_centro\.get\(comunidad\.upper\(\), "NO_ESPECIFICADO"\)', contenido, re.DOTALL)
if match_centro:
    original = match_centro.group(0)
    refinado = """def asignar_centro(row):
        dist = row['DISTRITO']
        comunidad = row['COMUNIDAD']
        if dist == 'repocura':
            # Quitar acentos para el lookup
            com_clean = remove_accents(comunidad).upper()
            return repocura_comunidad_a_centro.get(com_clean, "NO_ESPECIFICADO")"""
    
    # Reemplazar la parte del lookup
    sub_orig = re.search(r'if dist == \'repocura\':.*?return repocura_comunidad_a_centro\.get\(comunidad\.upper\(\), "NO_ESPECIFICADO"\)', original, re.DOTALL).group(0)
    sub_refinado = """if dist == 'repocura':
            com_clean = remove_accents(comunidad).upper()
            return repocura_comunidad_a_centro.get(com_clean, "NO_ESPECIFICADO")"""
    
    nuevo_centro = original.replace(sub_orig, sub_refinado)
    contenido = contenido.replace(original, nuevo_centro)
    print("Refinado asignar_centro.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Refinamientos aplicados.")
