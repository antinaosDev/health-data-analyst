import pandas as pd
import re
from collections import defaultdict
import unicodedata

def preprocesar_texto(texto):
    """Normaliza texto: elimina acentos, caracteres especiales y estandariza formatos"""
    if not isinstance(texto, str):
        return ""
    # Normaliza caracteres unicode y convierte a minúsculas
    texto = unicodedata.normalize('NFKD', texto).lower()
    # Elimina caracteres especiales excepto ñ, espacios, guiones y números
    texto = re.sub(r'[^a-z0-9ñáéíóúü\- ]', '', texto)
    # Reemplaza múltiples espacios por uno solo
    texto = re.sub(r'\s+', ' ', texto).strip()
    # Estandariza formatos de números (n, no, n°)
    texto = re.sub(r'\b(n|no|n°)\s*(\d+)', r'\2', texto)
    return texto

def construir_patrones():
    """Diccionario jerárquico de patrones para clasificación"""
    return [
        # 1. PATRONES EXACTOS (Máxima prioridad)
        (r'\b(coihue[ -]?curaco|llanquinao|santa[ -]?rosa|tranahuil|el mirador)\b', 'tranahuillin', 'exacto'),
        (r'\b(rapahue|rucapangue|huamaqui|rucapangui)\b', 'rapahue', 'exacto'),
        (r'\b(repocura|cullinco|cuyinco|launache|playa blanca)\b', 'repocura', 'exacto'),
        (r'\b(carirriñe|huechucon|huiñoco|boldoche|romulhue|carrerrine)\b', 'carirriñe', 'exacto'),
        (r'\b(coilaco|pitraco|tosc?a|curanilahue|peuchen|los[ -]?carrizos|coihue painemal)\b', 'cholchol', 'exacto'),
        
        # 2. VARIANTES ORTOGRÁFICAS
        (r'(chol[\s\-]*chol|ch[l1i][o0]l[\s\-]*chol|chochol|ch[l1i]chol|chol[\s\-]chol|chiol)', 'cholchol', 'ortografia'),
        (r'(c[au]r[rñ][i!1]ñe|carreriñe|carirreñe|carrerrine|carrerine)', 'carirriñe', 'ortografia'),
        (r'(tr[au]n[au]h[ui]l{1,2}in|tranagullin|trañi|tranahuil|trani)', 'tranahuillin', 'ortografia'),
        (r'(rep[o0][ck]ura|rep[o0]gura|r[ée]pocura|pocura|repokura)', 'repocura', 'ortografia'),
        (r'(rapa(ng?|h)ue|r[au]capangue|rucapangui|rapangui|rapa)', 'rapahue', 'ortografia'),
        
        # 3. CONTEXTO GEOGRÁFICO
        (r'(villa (el[ -]?esfuerzo|los[ -]?alerces|la[ -]?dehesa|vista hermosa|el fuerte))', 'cholchol', 'contexto'),
        (r'(camino (a[ -]?cholchol|cholchol[ -]?imperial|galvarino|huamaqui|repocura))', 'cholchol', 'contexto'),
        (r'(sector (rojo|azul|verde|centro|huamaqui|repocura|la foresta|picuta))', 'cholchol', 'contexto'),
        (r'(parcel(a|e)[ -]?\d+|km[ -]?\d+|hijuela \d+|fundo [a-z\- ]+)', 'cholchol', 'contexto'),
        
        # 4. INSTITUCIONES/COMUNIDADES
        (r'(comunidad [a-z\- ]+|reduccion [a-z\- ]+)', 'carirriñe', 'comunidad'),
        (r'(liceo (bicentenario|principe[ -]?de[ -]?gales|intercultural)|colegio [a-z\- ]+)', 'cholchol', 'institucion'),
        (r'(posta[ -]?(rural|huamaqui|cholchol|malalche)|escuela [a-z\- ]+)', 'cholchol', 'institucion'),
        (r'(centro de salud|cecosf|consultorio)', 'cholchol', 'institucion'),
        
        # 5. FALLBACKS GEOGRÁFICOS
        (r'(fundo [a-z\- ]+|camino [a-z\- ]+|ruta [a-z\- ]+)', 'cholchol', 'fallback'),
        (r'(paraje|lugar|aldea|localidad) [a-z\- ]+', 'cholchol', 'fallback'),
        
        # 6. PATRONES PARA CÓDIGOS ESPECIALES
        (r'\b(huia\d+oco|carreri?a?\d+e)\b', 'carirriñe', 'codigo'),
        
        # 7. ÚLTIMO FALLBACK (Patrones débiles)
        (r'(chol|choch|chilchol|chiol|ch[l1i])', 'cholchol', 'weak_match'),
        (r'(tranahuil|trañi|trani|tr[au]n)', 'tranahuillin', 'weak_match'),
        (r'(rapah|rucapa|rapa|r[au]ca)', 'rapahue', 'weak_match'),
        (r'(repoc|repok|repo|pocu)', 'repocura', 'weak_match'),
        (r'(carirri|carreri|carre|rirri)', 'carirriñe', 'weak_match')
    ]

def clasificar_direccion(direccion, patrones):
    """Clasifica una dirección usando patrones jerárquicos"""
    texto = preprocesar_texto(direccion)
    
    # Verificar primero patrones exactos
    for patron, distrito, tipo in patrones[:5]:
        if re.search(patron, texto):
            return distrito, tipo
    
    # Luego verificar otros patrones
    for patron, distrito, tipo in patrones[5:]:
        if re.search(patron, texto):
            return distrito, tipo
            
    return 'cholchol', 'no_match'  # Default

def procesar_dataset(input_path, output_path):
    """Procesa un archivo CSV y exporta resultados con metadatos"""
    # Cargar datos
    df = pd.read_csv(input_path)
    
    # Construir patrones
    patrones = construir_patrones()
    
    # Clasificar cada registro
    resultados = []
    for _, row in df.iterrows():
        direccion = row['value'] if 'value' in row else row['direccion']
        distrito, tipo_clasif = clasificar_direccion(direccion, patrones)
        
        resultados.append({
            'direccion_original': direccion,
            'direccion_normalizada': preprocesar_texto(direccion),
            'distrito': distrito,
            'tipo_clasificacion': tipo_clasif,
            'coincidencia': 'manual' if distrito == 'cholchol' and tipo_clasif == 'no_match' else 'automatica'
        })
    
    # Crear DataFrame y exportar
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ Resultados exportados a {output_path}")
    return df_resultados

# Ejecución
if __name__ == "__main__":
    input_csv = "datos_direcciones.csv"  # Cambiar por tu archivo de entrada
    output_csv = "resultados_clasificacion.csv"
    resultados = procesar_dataset(r"C:\Users\alain\Downloads\2025-08-06T02-04_export.csv", output_csv)