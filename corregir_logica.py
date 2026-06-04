import codecs

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

target = """    def asignar_centro(row):
        dist = row['DISTRITO']
        comunidad.upper() = row['COMUNIDAD']
        if dist == 'repocura':
            return repocura_comunidad.upper()_a_centro.get(comunidad.upper(), "NO_ESPECIFICADO")
        return distrito_a_centro.get(dist, "NO_ESPECIFICADO")"""

replacement = """    def asignar_centro(row):
        dist = row['DISTRITO']
        comunidad = row['COMUNIDAD']
        if dist == 'repocura':
            return repocura_comunidad_a_centro.get(comunidad.upper(), "NO_ESPECIFICADO")
        return distrito_a_centro.get(dist, "NO_ESPECIFICADO")"""

if target in contenido:
    contenido = contenido.replace(target, replacement)
    print("Logica corregida con exito.")
else:
    print("No se encontro el target EXACTO. Intentando regex...")
    import re
    # Intentar con regex mas flexible para espacios
    pattern = r'def asignar_centro\(row\):\s*dist = row\[\'DISTRITO\'\]\s*comunidad\.upper\(\) = row\[\'COMUNIDAD\'\]\s*if dist == \'repocura\':\s*return repocura_comunidad\.upper\(\)_a_centro\.get\(comunidad\.upper\(\), "NO_ESPECIFICADO"\)\s*return distrito_a_centro\.get\(dist, "NO_ESPECIFICADO"\)'
    match = re.search(pattern, contenido, re.DOTALL)
    if match:
        contenido = re.sub(pattern, replacement, contenido, flags=re.DOTALL)
        print("Logica corregida con regex.")
    else:
        print("Tampoco se encontro con regex.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)
