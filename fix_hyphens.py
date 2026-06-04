import codecs
import re

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

def clear_hyphen_in_dict(name, text):
    match = re.search(f'{name} = \\{{(.*?)\\}}', text, re.DOTALL)
    if not match: return text
    cuerpo = match.group(1)
    lineas = cuerpo.split('\n')
    for i, l in enumerate(lineas):
        if ':' in l:
            try:
                k, v = l.split(':', 1)
                if '-' in k:
                    k_new = k.replace('-', ' ')
                    lineas[i] = k_new + ':' + v
            except:
                pass
    cuerpo_nuevo = '\n'.join(lineas)
    return text.replace(match.group(1), cuerpo_nuevo)

contenido = clear_hyphen_in_dict('sector_a_comunidad', contenido)
contenido = clear_hyphen_in_dict('sector_a_distrito', contenido)
contenido = clear_hyphen_in_dict('repocura_comunidad_a_centro', contenido)

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Guiones corregidos en claves de diccionarios.")
