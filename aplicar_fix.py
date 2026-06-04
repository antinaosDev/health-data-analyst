import re
import codecs

# 1. Leer codigo generado
with open('codigo_generado.txt', 'r', encoding='utf-8') as f:
    lineas = f.readlines()

comunidad_updates = []
distrito_updates = []
centros_output = []

current_section = None
for l in lineas:
    l_strip = l.strip()
    if '--- sector_a_comunidad_updates ---' in l:
        current_section = 'comunidad'
        continue
    elif '--- sector_a_distrito_updates ---' in l:
        current_section = 'distrito'
        continue
    elif '--- NUEVOS DICCIONARIOS CENTROS ---' in l:
        current_section = 'centros'
        continue

    if not l_strip:
        # if current_section == 'centros':
        #     centros_output.append(l)
        continue

    if l_strip.endswith(',,'):
        l = l.replace(',,', ',')

    if current_section == 'comunidad':
        comunidad_updates.append(l)
    elif current_section == 'distrito':
        distrito_updates.append(l)
    elif current_section == 'centros':
        centros_output.append(l)

# 2. Leer analisis_func.py
with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# A. Actualizar sector_a_comunidad
match_com = re.search(r'sector_a_comunidad = \{(.*?)\}', contenido, re.DOTALL)
if match_com:
    cuerpo_actual = match_com.group(1)
    # Agregar los nuevos elementos al final del cuerpo actual
    # Pero primero, remover si ya estaban (de un fix anterior fallido)
    # Para simplificar, podemos buscar si ya estan alli.
    # O simplemente concatenar los nuevos al final. El dict sobreescribirá si hay duplicados.
    cuerpo_nuevo = cuerpo_actual.rstrip() + '\n    # --- NUEVOS ELEMENTOS ---\n' + "".join(comunidad_updates) + '\n    '
    contenido = contenido.replace(match_com.group(1), cuerpo_nuevo)
    print("Actualizado sector_a_comunidad")

# B. Actualizar sector_a_distrito
match_dist = re.search(r'sector_a_distrito = \{(.*?)\}', contenido, re.DOTALL)
if match_dist:
    cuerpo_actual = match_dist.group(1)
    cuerpo_nuevo = cuerpo_actual.rstrip() + '\n    # --- NUEVOS ELEMENTOS ---\n' + "".join(distrito_updates) + '\n    '
    contenido = contenido.replace(match_dist.group(1), cuerpo_nuevo)
    print("Actualizado sector_a_distrito")

# C. Actualizar repocura_comunidad_a_centro
match_repocura = re.search(r'repocura_comunidad_a_centro = \{(.*?)\}', contenido, re.DOTALL)
if match_repocura:
    cuerpo_nuevo = "".join([l for l in centros_output if '"' in l])
    contenido = re.sub(r'repocura_comunidad_a_centro = \{.*?\}', 'repocura_comunidad_a_centro = {\n' + cuerpo_nuevo + '\n    }', contenido, flags=re.DOTALL)
    print("Actualizado repocura_comunidad_a_centro")

# D. Asegurar .upper() en asignar_centro
match_fun = re.search(r'def asignar_centro\(row\):.*?if dist == \'repocura\':.*?return repocura_comunidad_a_centro\.get\(comunidad, "NO_ESPECIFICADO"\)', contenido, re.DOTALL)
if match_fun:
    sub = match_fun.group(0).replace('comunidad', 'comunidad.upper()')
    contenido = contenido.replace(match_fun.group(0), sub)
    print("Corregido lookup de comunidad a upper()")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Cambios aplicados con exito.")
