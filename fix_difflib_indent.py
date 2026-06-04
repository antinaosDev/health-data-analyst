import codecs

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

target = """    import unicodedata
import difflib
    def remove_accents(input_str):"""

replacement = """    import unicodedata
    import difflib
    def remove_accents(input_str):"""

if target in contenido:
    contenido = contenido.replace(target, replacement)
    print("Indentación de import difflib en normaliza_direcc corregida.")
else:
    print("No se encontró el bloque exacto. Usando regex...")
    import re
    # Match exacto con saltos de línea para evitar problemas indeterminados
    pattern = r'(\s*import unicodedata\n)import difflib(\n\s*def remove_accents)'
    if re.search(pattern, contenido):
        contenido = re.sub(pattern, r'\1    import difflib\2', contenido)
        print("Corregido con regex.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Actualización de sintaxis finalizada.")
