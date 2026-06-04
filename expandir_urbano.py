import codecs
import re
import unicodedata

# 1. Lista provista por el usuario (Calles urbanas de Cholchol)
calles_raw = """
Bernardo O'Higgins
Errázuriz
Teodoro Schmidt
Chamil
Pasaje Recreo
Ercilla
Avenida Balmaceda
Avenida Arturo Prat
Diego Portales
Cacique Millapán
José Joaquín Pérez
Aldunate
Los Canelos
Avenida Lastarria
Saavedra
Amunátegui
Castellón
Pasaje Los Robles
Vicuña Mackenna
Lazcano
Manuel Montt
Aníbal Pinto
Cacique Lemu Nahuel
Nueva Uno
Nueva Dos
Pasaje Zedan
Pasaje Los Pioneros
Pasaje Colo Colo
Pasaje Lautaro
""".strip().split('\n')

def clean_txt(s):
    nfkd = unicodedata.normalize('NFD', s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

def extract_dict_keys(name):
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

nuevos_items = []
presentes = []

for c in calles_raw:
    c = c.strip()
    if not c: continue
    key = clean_txt(c)
    
    if key in S_A_COM and key in S_A_DIST:
        presentes.append(c)
    else:
        nuevos_items.append((key, c))

print(f"Calles totales: {len(calles_raw)}")
print(f"A agregar: {len(nuevos_items)}")
print(f"Ya presentes: {len(presentes)}")

com_lines = []
dist_lines = []

for key, orig in nuevos_items:
    # Usar el nombre original en upper como valor de comunidad para que el usuario obtenga el literal detallado
    com_lines.append(f'    "{key}": "{orig.upper()}",')
    dist_lines.append(f'    "{key}": "cholchol",')

def append_to_dict(name, lines):
    global contenido
    if not lines: return
    match = re.search(f'({name} = \\{{.*?)(\\}})', contenido, re.DOTALL)
    if match:
        body = match.group(1)
        tail = match.group(2)
        nuevo_bloque = body.rstrip() + "\n" + "\n".join(lines) + "\n" + tail
        contenido = contenido.replace(match.group(0), nuevo_bloque)
        print(f"Insertados en {name}")

append_to_dict('sector_a_comunidad', com_lines)
append_to_dict('sector_a_distrito', dist_lines)

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Expansión urbana completada.")
