import codecs

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# Quitar indentación a import difflib al inicio del archivo
target_indent = '    import difflib'
rep_indent = 'import difflib'

if target_indent in contenido:
    contenido = contenido.replace(target_indent, rep_indent)
    print("Indentación de import difflib corregida.")
else:
    print("No se encontró el import indentado.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Sintaxis de cabecera reparada.")
