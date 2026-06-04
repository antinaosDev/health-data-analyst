import re
import codecs

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# Buscar patrones: @st.cache_data y la línea siguiente (def ...)
pattern = r'(@st\.cache_(?:data|resource).*?)\n\s*def\s+(\w+)\s*\((.*?)\):'
matches = re.findall(pattern, contenido, re.DOTALL)

output = []
output.append("=== FUNCIONES CON CACHE ===")

for dec, name, args in matches:
    output.append(f"\nFuncion: {name}")
    output.append(f"  Decorator: {dec.strip()}")
    output.append(f"  Argumentos: {args.strip()}")

with open('funciones_cache.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Lista de funciones de cache generada.")
