import codecs
import re
import unicodedata

# 1. Lista de 27 Ausentes
ausentes_list = [
    "Comunidad Rayén Lafquén", "Comunidad Fermín Huenchual", "Comunidad Ramón Painemal",
    "Comunidad Tren Tren", "Comunidad Juan Curral", "Comunidad Manuel Huenchunao",
    "Comunidad Juan Ancalle", "Comunidad Juan Colipí", "Comunidad Huenul Llancán",
    "Comunidad Domín Colín", "Comunidad Juan Mauricio Huaiquián", "Comunidad Levio Huenchual",
    "Los Aromos", "Comunidad Pailacura Lincomil", "Comunidad Mateo Lleupi",
    "Comunidad Ramón Antilaf", "Comunidad Cacique Lienqueo", "Comunidad Pascual Painemilla Dos",
    "La Dehesa", "Comunidad Pedro Marín Calfucura", "Comunidad Agustín Painaqueo",
    "Comunidad Alberto Véjar", "Comunidad Venancio Coñoepán", "Comunidad Santos Marillán",
    "Comunidad Viuda de José Ñanculef", "Comunidad Juan Antinao", "Comunidad Huenchul Alcamán Colipí"
]

# 2. Parsear el texto del usuario
texto_usuario = """
Comunidad Pedro Cayuqueo	LUNA	RAPAHUE	PSR MALALCHE
Comunidad Rayén Lafquén	LUNA	RAPAHUE	PSR MALALCHE
Comunidad Francisco Maliqueo	LUNA	RAPAHUE	PSR MALALCHE
Comunidad José Chanqueo	LUNA	RAPAHUE	PSR MALALCHE
Comunidad Rosario Morales	LUNA	RAPAHUE	PSR MALALCHE
Comunidad Ramón Painemal	LUNA	RAPAHUE	PSR MALALCHE
Comunidad Tren Tren	LUNA	RAPAHUE	PSR MALALCHE
Los Aromos	LUNA	RAPAHUE	PSR MALALCHE
Comunidad Cacique Lienqueo	LUNA	RAPAHUE	PSR MALALCHE
Comunidad Rincón Rucapangue	LUNA	RAPAHUE	PSR MALALCHE
Comunidad Pascual Painemilla Dos	LUNA	RAPAHUE	PSR MALALCHE
Dollinco	LUNA	RAPAHUE	PSR MALALCHE
Comunidad Antonio Painemal	LUNA	CARIRRIÑE	PSR MALALCHE
Comunidad Mulato Huenulef	LUNA	CARIRRIÑE	PSR MALALCHE
Comunidad Antonio Huichapán	LUNA	CARIRRIÑE	PSR MALALCHE
Comunidad Pablo Ignacio Hueichapán	LUNA	CARIRRIÑE	PSR MALALCHE
Comunidad Juan Antinao	LUNA	CARIRRIÑE	PSR MALALCHE
Comunidad Flora Chihuaillán	LUNA	CARIRRIÑE	PSR MALALCHE
Comunidad Huenchul Alcamán Colipí	LUNA	CARIRRIÑE	PSR MALALCHE
Comunidad Juan Ancalle	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Federico Antinao	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Agustín Chihuaicura	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Juan Levio	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Juan Colipí	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Juan Curihual	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Huenul Llancán	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Domín Colín	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Juan Mauricio Huaiquián	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Levio Huenchual	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Pedro Marín Calfucura	LUNA	REPOCURA	PSR HUENTELAR
Repocura	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Agustín Painaqueo	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Alberto Véjar	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Juan Huilipán	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Juan Nahuelpi	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Anselmo Quintriqueo	LUNA	REPOCURA	PSR HUENTELAR
Comunidad José Epulef	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Hueichao Millán	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Juan Cayul	LUNA	REPOCURA	PSR HUENTELAR
Comunidad José Curiqueo	LUNA	REPOCURA	PSR HUENTELAR
Malalche Rincón	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Quintul Viuda de Alcamán	LUNA	REPOCURA	PSR HUENTELAR
Comunidad Viuda de José Ñanculef	LUNA	REPOCURA	PSR HUENTELAR
Malalche Alto	LUNA	REPOCURA	PSR HUENTELAR
Huamaqui	LUNA	REPOCURA	PSR HUENTELAR
Cholchol	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Domingo Coñoepán	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Juan Curral	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Manuel Cayunao	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Miguel Lemunao	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Manuel Huenchunao	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Juan Huaiquil Curillán	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Juan Melinao	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Domingo Coñoepán	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Juan Millapán	SOL	CHOLCHOL	CESFAM CHOLCHOL
Rinconada	SOL	CHOLCHOL	CESFAM CHOLCHOL
La Dehesa	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Pedro Huircán	SOL	CHOLCHOL	CESFAM CHOLCHOL
Pitraco	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Venancio Coñoepán	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad Santos Marillán	SOL	CHOLCHOL	CESFAM CHOLCHOL
Comunidad La Foresta I	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad La Foresta II	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Juan de Dios Lleuvul	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Dionisio Paillao	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Fermín Huenchual	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Notromahuida	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Calvunao Caniupán	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Renaco	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Villa El Estero	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad José Calfulaf	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Abelino Huinca	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Juan Mulato	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad José Traipe	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Carilaf Chifca	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad José Miguel Huaiquean	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Domingo Chañillao	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Pailacura Lincomil	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Gabriel Chicahual	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Juan Calbuqueo	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Pedro Curihuinca	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Mateo Lleupi	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Ramón Antilaf	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad José Soto Neilaf	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad Juan Santiago	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
La Foresta	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
Comunidad La Foresta III	SOL	TRANAHUILLIN	CESFAM CHOLCHOL
"""

def clean_txt(s):
    nfkd = unicodedata.normalize('NFD', s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()

mapeos = {}
for line in texto_usuario.strip().split('\n'):
    parts = line.split('\t')
    if len(parts) >= 4:
        nombre = parts[0].strip()
        distrito = parts[2].strip()
        centro = parts[3].strip()
        if nombre in ausentes_list:
            mapeos[nombre] = {"distrito": distrito, "centro": centro}

print(f"Mapeos filtrados (Ausentes): {len(mapeos)}")

# 3. Leer analisis_func.py
with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

# Preparar fragmentos para insertar
com_items = []
dist_items = []
repo_items = []

for nombre, m in mapeos.items():
    nombre_clean = clean_txt(nombre.replace("Comunidad ", ""))
    dist_val = m["distrito"].lower()
    centro_val = m["centro"]
    
    # dict item code strings
    com_items.append(f'    "{nombre_clean}": "{nombre.replace("Comunidad ", "")}",')
    dist_items.append(f'    "{nombre_clean}": "{dist_val}",')
    if dist_val == 'repocura':
        # repocura_comunidad_a_centro
        repo_items.append(f'    "{nombre_clean}": "{centro_val}",')

print(f"A agregar a sector_a_comunidad: {len(com_items)}")
print(f"A agregar a sector_a_distrito: {len(dist_items)}")
print(f"A agregar a repocura_comunidad_a_centro: {len(repo_items)}")

def append_to_dict(name, new_items_list):
    global contenido
    if not new_items_list: return
    match = re.search(f'({name} = \\{{.*?)(\\}})', contenido, re.DOTALL)
    if match:
        body = match.group(1)
        tail = match.group(2)
        nuevo_bloque = body.rstrip() + "\n" + "\n".join(new_items_list) + "\n" + tail
        contenido = contenido.replace(match.group(0), nuevo_bloque)
        print(f"Insertados items en {name}")

append_to_dict('sector_a_comunidad', com_items)
append_to_dict('sector_a_distrito', dist_items)
append_to_dict('repocura_comunidad_a_centro', repo_items)

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)

print("Expansion completada.")
