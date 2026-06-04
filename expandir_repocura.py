import codecs
import re
import unicodedata

# 1. Lista provista por el usuario (Comunidades Repocura - PSR Huamaqui)
lugares_raw = """
El Chilco
Huamaqui
Huamaqui Alto
La Montaña
Madilhue Pellahuen
Corrientes Blancas
El Aromo
La Quinta
Pellahuen La Herradura
Quicheltue
Repocura Deuco
""".strip().split('\n')

def clean_txt(s):
    # Eliminar acentos y poner en mayúsculas
    nfkd = unicodedata.normalize('NFD', s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

def extract_dict_keys(name):
    # Match básico para jalar las llaves del diccionario de forma segura con Regex
    match = re.search(f'{name} = \\{{(.*?)\\}}', contenido, re.DOTALL)
    if match:
        try:
            d = eval('{' + match.group(1) + '}')
            return [str(k).upper() for k in d.keys()]
        except:
            return []
    return []

S_A_COM = extract_dict_keys('sector_a_comunidad')
S_A_DIST = extract_dict_keys('sector_a_distrito')
R_C_A_C = extract_dict_keys('repocura_comunidad_a_centro')

nuevos_items = []
presentes = []

for l in lugares_raw:
    l = l.strip()
    if not l: continue
    key = clean_txt(l)
    
    if key in S_A_COM and key in S_A_DIST:
        presentes.append(l)
    else:
        nuevos_items.append((key, l))

print(f"Lugares totales: {len(lugares_raw)}")
print(f"A agregar: {len(nuevos_items)}")
print(f"Ya presentes: {len(presentes)}")

com_lines = []
dist_lines = []
centro_lines = []

for key, orig in nuevos_items:
    com_lines.append(f'    "{key}": "{orig.upper()}",')
    dist_lines.append(f'    "{key}": "repocura",')
    # Añadir a repocura_comunidad_a_centro con Title Case para consistencia
    centro_lines.append(f'    "{orig.upper()}": "PSR Huamaqui",')

def append_to_dict(name, lines):
    global contenido
    if not lines: return
    # Regex para capturar el cuerpo del diccionario
    match = re.search(f'({name} = \\{{.*?)(\\}})', contenido, re.DOTALL)
    if match:
        body = match.group(1)
        tail = match.group(2)
        nuevo_bloque = body.rstrip() + "\n" + "\n".join(lines) + "\n" + tail
        contenido = contenido.replace(match.group(0), nuevo_bloque)
        print(f"✅ Insertados {len(lines)} items en {name}")
    else:
        print(f"⚠️ No se pudo inyectar en {name}")

append_to_dict('sector_a_comunidad', com_lines)
append_to_dict('sector_a_distrito', dist_lines)
append_to_dict('repocura_comunidad_a_centro', centro_lines)

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Expansión rural Repocura completada.")
