import re
import codecs

# Lista provista por el usuario en el paso 680
nuevas_comunas_raw = """
Cholchol
Comunidad La Foresta I
Comunidad La Foresta II
Comunidad Pedro Cayuqueo
Comunidad Rayén Lafquén
Comunidad Francisco Maliqueo
Comunidad José Chanqueo
Comunidad Juan de Dios Lleuvul
Comunidad Dionisio Paillao
Comunidad Fermín Huenchual
Comunidad Antonio Painemal
Comunidad Rosario Morales
Comunidad Ramón Painemal
Comunidad Tren Tren
Comunidad Domingo Coñoepán
Comunidad Juan Curral
Comunidad Manuel Cayunao
Comunidad Miguel Lemunao
Comunidad Manuel Huenchunao
Comunidad Juan Huaiquil Curillán
Comunidad Juan Melinao
Comunidad Domingo Coñoepán
Comunidad Juan Ancalle
Comunidad Federico Antinao
Comunidad Agustín Chihuaicura
Comunidad Juan Levio
Comunidad Juan Colipí
Comunidad Juan Curihual
Comunidad Huenul Llancán
Comunidad Domín Colín
Comunidad Juan Mauricio Huaiquián
Comunidad Levio Huenchual
Comunidad Juan Millapán
Rinconada
Los Aromos
Notromahuida
Comunidad Calvunao Caniupán
Renaco
Villa El Estero
Comunidad José Calfulaf
Comunidad Abelino Huinca
Comunidad Juan Mulato
Comunidad José Traipe
Comunidad Carilaf Chifca
Comunidad José Miguel Huaiquean
Comunidad Domingo Chañillao
Comunidad Pailacura Lincomil
Comunidad Gabriel Chicahual
Comunidad Juan Calbuqueo
Comunidad Pedro Curihuinca
Comunidad Mateo Lleupi
Comunidad Ramón Antilaf
Comunidad José Soto Neilaf
Comunidad Juan Santiago
La Foresta
Comunidad Cacique Lienqueo
Comunidad Rincón Rucapangue
Comunidad Pascual Painemilla Dos
La Dehesa
Comunidad La Foresta III
Comunidad Pedro Marín Calfucura
Repocura
Comunidad Agustín Painaqueo
Comunidad Alberto Véjar
Comunidad Juan Huilipán
Comunidad Pedro Huircán
Pitraco
Comunidad Venancio Coñoepán
Comunidad Santos Marillán
Comunidad Juan Nahuelpi
Comunidad Anselmo Quintriqueo
Comunidad José Epulef
Comunidad Hueichao Millán
Comunidad Juan Cayul
Comunidad José Curiqueo
Malalche Rincón
Comunidad Quintul Viuda de Alcamán
Comunidad Viuda de José Ñanculef
Comunidad Mulato Huenulef
Comunidad Antonio Huichapán
Comunidad Pablo Ignacio Hueichapán
Comunidad Juan Antinao
Comunidad Flora Chihuaillán
Comunidad Huenchul Alcamán Colipí
Malalche Alto
Huamaqui
Dollinco
""".strip().split('\n')

# Limpiar nombres (quitar "Comunidad " para buscar el núcleo)
def limpiar_nombre(n):
    n = n.replace("Comunidad ", "")
    n = n.upper().strip()
    return n

nuevas_comunidades = {limpiar_nombre(n): n for n in nuevas_comunas_raw if n.strip()}

# Leer diccionarios actuales
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

presentes = []
ausentes = []

for clean_n, original_n in nuevas_comunidades.items():
    # Buscar si coincide con alguna llave (inclusivo)
    encontrado = False
    for k in S_A_COM + S_A_DIST:
        if clean_n in k or k in clean_n:
            presentes.append(f"{original_n} -> Coincide con dicc: '{k}'")
            encontrado = True
            break
    if not encontrado:
        ausentes.append(original_n)

reporte = []
reporte.append("=== ANALISIS DE NUEVAS COMUNIDADES ===")
reporte.append(f"\nTotal provistas: {len(nuevas_comunidades)}")
reporte.append(f"Presentes/Similares: {len(presentes)}")
reporte.append(f"Ausentes (Sin Mapeo): {len(ausentes)}")

reporte.append("\n--- AUSENTES (Necesitan Distrito y Centro) ---")
for a in ausentes:
    reporte.append(f"- {a}")

reporte.append("\n--- PRESENTES ---")
for p in presentes:
    reporte.append(f"- {p}")

with open('reporte_nuevas.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(reporte))

print("Reporte generado en reporte_nuevas.txt")
print(f"Ausentes: {len(ausentes)}")
