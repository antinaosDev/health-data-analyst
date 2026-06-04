import codecs

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

target = """        def asignar_centro(row):
        dist = row['DISTRITO']
        comunidad = row['COMUNIDAD']
        if dist == 'repocura':
            return repocura_comunidad_a_centro.get(comunidad.upper(), "NO_ESPECIFICADO")
        return distrito_a_centro.get(dist, "NO_ESPECIFICADO")"""

replacement = """    def asignar_centro(row):
        dist = row['DISTRITO']
        comunidad = row['COMUNIDAD']
        if dist == 'repocura':
            return repocura_comunidad_a_centro.get(comunidad.upper(), "NO_ESPECIFICADO")
        return distrito_a_centro.get(dist, "NO_ESPECIFICADO")"""

if target in contenido:
    contenido = contenido.replace(target, replacement)
    print("Indetacion corregida con exito.")
else:
    print("No se encontro target Exacto. Intentando búsqueda flexible...")
    # Reemplazar línea por línea si es necesario
    lineas = contenido.split('\n')
    for i, l in enumerate(lineas):
        if 'def asignar_centro(row):' in l and l.startswith('        '):
            lineas[i] = '    def asignar_centro(row):'
            # Ajustar cuerpo
            lineas[i+1] = '        ' + lineas[i+1].strip()
            lineas[i+2] = '        ' + lineas[i+2].strip()
            lineas[i+3] = '        ' + lineas[i+3].strip()
            lineas[i+4] = '            ' + lineas[i+4].strip()
            lineas[i+5] = '        ' + lineas[i+5].strip()
            print("Indetacion corregida línea por línea.")
            break
    contenido = '\n'.join(lineas)

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)
