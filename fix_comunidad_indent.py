import codecs

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# Quitar 4 espacios extras a la línea de 'def asignar_comunidad'
target = "        def asignar_comunidad(texto):"
replacement = "    def asignar_comunidad(texto):"

if target in contenido:
    contenido = contenido.replace(target, replacement)
    print("Indetación de asignar_comunidad corregida.")
else:
    print("No se halló la línea con 8 espacios.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Sintaxis reparada.")
