import re
import unicodedata  # <-- Esto faltaba
import pandas as pd
def normaliza_direcc(df):

    # --- Funciones de limpieza ---
    # 1️⃣ Normalizar mayúsculas y eliminar tildes
    def normalizar_texto(texto):
        texto = str(texto).upper()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                        if unicodedata.category(c) != 'Mn')
        return texto

    # 2️⃣ Limpiar caracteres raros y múltiples espacios
    def limpiar_basico(texto):
        texto = re.sub(r'[^A-Z0-9Ñ\s]', ' ', texto)  # eliminar símbolos raros
        texto = re.sub(r'\s+', ' ', texto).strip()   # quitar espacios extras
        return texto

    # 3️⃣ Normalizar abreviaturas comunes
    def normalizar_abreviaturas(texto):
        reemplazos = {
            r'\bN[º°?.]?\b': ' NUMERO ',
            r'\bS/N\b': ' SIN NUMERO ',
            r'\bSN\b': ' SIN NUMERO ',
            r'\bCAM\b': ' CAMINO ',
            r'\bLG\b': ' LUGAR ',
            r'\bPJE\b': ' PASAJE ',
        }
        for patron, reemplazo in reemplazos.items():
            texto = re.sub(patron, reemplazo, texto)
        return texto

    # 4️⃣ Corregir errores frecuentes
    errores_comunes = {
        "CARRERRI E": "CARRERRENE",
        "CARRERRIA": "CARRERRENE",
        "CARRERRIÑE": "CARRERRENE",
        "CHOL CHOL": "CHOLCHOL",
    }

    def corregir_errores(texto):
        for mal, bien in errores_comunes.items():
            texto = texto.replace(mal, bien)
        return texto

    # --- Pipeline completo ---
    def limpiar_direccion(texto):
        texto = normalizar_texto(texto)
        texto = limpiar_basico(texto)
        texto = normalizar_abreviaturas(texto)
        texto = corregir_errores(texto)
        return texto

    # Aplicar limpieza a la columna 'DIRECCION'
    df['DIRECCION_NORM'] = df['DIRECCION'].apply(limpiar_direccion)

    # Mostrar ejemplo
    print(df[['DIRECCION', 'DIRECCION_NORM']].head(20))

    sector_a_comunidad = {
    ##########COMUNIDADES
    "ANSELMO QUINTRI": "Anselmo Quintriqueo",
    "PEDRO MARIN": "Pedro Marin Calcucura",
    "AGUSTIN PAINE": "Juan Agustin Painequeo",
    "ALBERTO BEJAR": "Alberto Bejar",
    "JUAN LIENAN": "Juan Lienan",
    "CHIHUAI": "Agustín Chihuaicura",
    "JUAN DE DIOS HUIC": "Juan de Dios Huichaleo",
    "JUAN ANCAYE": "Juan Ancaye",
    "FEDERICO ANTI": "Federico Antinao",
    "JUAN LEVIO": "Juan Levio",
    "JUAN COLIPI": "Juan Colipi Huechunao",
    "JOSE CURI": "José Curiqueo",
    "ANTONIO CAYUL": "Antonio Cayul",
    "JUAN CURIGL": "Juan Curigual",
    "JUAN CURIH": "Juan Curihual",
    "JOSE CURIQ": "José Curiqueo",
    "LORENZO CAYUL": "Lorenzo Cayul",
    "LORENSO CAYUL": "Lorenzo Cayul",
    "HUEICHAO": "Hueichao Millan",
    "GUENUL LLANCAL": "Guenul Llancal",
    "DOMINGO COLIN": "Domingo Colin",
    "LEVIN LEMUNAO": "Levin Lemunao",
    "MAURICIO GUAIQUEAN": "Juan Mauricio Guaiquean",
    "MAURICIO HUAIQUEAN": "Juan Mauricio Guaiquean",
    "QUINTUL": "Quintul V. De Alcaman Cayul",
    "MANUEL PAINENAO": "Manuel Painenao",
    "MULATO HUENULEF": "Mulato Huenulef",
    "MULATO GUENULEF": "Mulato Huenulef",
    "HUENCHUL ANCAMA": "Huenchul Ancaman Colipi",
    "FLORA CHIHUAILLAN": "Flora Chiguaillan V. De Lienqueo",
    "BRIONES PAIN": "Briones Painemal",
    "JUAN ANTONIO": "Juan Antonio",
    "PEDRO IGNACIO GUICHAPAN": "Pablo Ignacio Guichapan",
    "PEDRO IGNACIO HUICHAPAN": "Pablo Ignacio Guichapan",
    "LUIS COLLIO": "José Luis Collio",
    "ANTONIO PAINEMAL": "Antonio Painemal",
    "JUAN PAINEN": "Juan Painenao",
    "RAMON ANCAMIL": "Ramon Ancamil",
    "RAMON PAINE": "Ramon Painemal",
    "TRENG": "TRENG-TRENG",
    "MULATO CHIG": "MulatoChiguaihue",
    "PEDRO CAY": "Pedro Cayuqueo",
    "RAYEN LAF": "Rayen Lafken De Newenko",
    "FRANCISCO MAL": "Francisco Maliqueo",
    "PEDRO MAL": "Francisco Maliqueo",
    "MANUELHUA": "Manuelhual",
    "CALVUL COLL": "Calvul Collio",
    "CALBUL COL": "Calvul Collio",
    "JOSE NIN": "José Niño",
    "MANUEL CAY": "Manuel Cayunao",
    "JUAN CURA": "Juan Curall",
    "JUAN MELI": "Juan Melinao",
    "DOMINGO COÑO": "Domingo Coñoepan",
    "DOMINGO CONOE": "Domingo Coñoepan",
    "JUAN GUAI": "Juan Guaiquil",
    "JUAN HUAI": "Juan Guaiquil",
    "MIGUEL LEMU": "Miguel Lemunao",
    "PEDRO GUIL": "Pedro Guilcan",
    "PEDRO HUIL": "Pedro Guilcan",
    "BENITO NAI": "Benito Nain",
    "JUAN MILLA": "Juan Millapan",
    "BENANCIO COÑO": "Benancio Coñoepan",
    "BENANCIO CONOE": "Benancio Coñoepan",
    "LOS CARRIZOS": "LOS CARRIZOS",
    "LOS CARRISOS": "LOS CARRIZOS",
    "CARRIZOS": "LOS CARRIZOS",
    "CARRRISOS": "LOS CARRIZOS",
    "DOMINGO MARIL": "Domingo Marillan",
    "JOSE LONCO": "José Loncomil",
    "ROSARIO QUE": "Rosario Quezada",
    "HUINCA HUENC": "Huincha Huenchuleo",
    "GUINCA GUENC": "Guinca Guenchuleo",
    "ROSA MILL": "Rosa Millapan",
    "FERMIN GUEN": "Fermin Guenchual",
    "FERMIN HUEN": "Fermin Guenchual",
    "CALVUNAO CANIU": "Calvunao Cañiupan",
    "CALVUNAO CAÑU": "Calvunao Cañiupan",
    "CALBUNAO CANIU": "Calvunao Cañiupan",
    "CALBUNAO CAÑU": "Calvunao Cañiupan",
    "PEDRO CURI": "Pedro Curihuinca",
    "JUAN DE DIOS LLEU": "Juan de Dios Lleuvul",
    "DIONISIO PAILL": "Dionisio Paillao",
    "JUAN CALBU": "Juan Calbuqueo",
    "JUAN CALVU": "Juan Calbuqueo",
    "GABRIEL CHICA": "Gabriel Chicahual",
    "FRANCISCO CURI": "Francisco Curiqueo",
    "JOSE CHAN": "José Chanqueo",
    "MATEO YAU": "Mateo Yaupi",
    "MATEO LLAU": "Mateo Yaupi",
    "DOMINGO CHAÑ": "Domingo Chañillao",
    "DOMINGO CHAN": "Domingo Chañillao",
    "CALFUL": "Calfulaf",
    "RAMON ANTIL": "Ramon Antilaf",
    "ANTONIO TROP": "Antonio Tropa",
    "JUAN SANT": "Juan Santiago",
    "SOTO NEI": "José Soto Neillai Nielaf",
    "AVELINO HUINC": "Avelino Huinca",
    "ABELINO HUINC": "Avelino Huinca"
}

    # Función para asignar distrito
    def asignar_distrito(texto):
        texto = texto.upper()
        for sector, distrito in sector_a_comunidad.items():
            if sector in texto:
                # Si hay varios posibles distritos, toma el primero
                if isinstance(distrito, list):
                    return distrito[0]
                return distrito
        return "NO_ESPECIFICADO"

    # Aplicar la función
    df = df[df['COMUNA'] == 'CHOL CHOL']
    df['COMUNIDAD'] = df['DIRECCION_NORM'].apply(asignar_distrito)

    # Ver resultados
    print(df[['DIRECCION_NORM', 'COMUNIDAD']].head(20))

    # Crear la columna SECTOR con un valor por defecto
    df['SECTOR'] = 'NO_ESPECIFICADO'
    df['LAT_SEC'] = 'NO_ESPECIFICADO'
    df['LON_SEC'] = 'NO_ESPECIFICADO'

    
    df.to_csv('fg2.csv',index=False)
    return df

df = pd.read_csv(
    r"D:\DESARROLLO PROGRAMACION\analisis tendencia\comb\Agenda_médica_[2015, 2016, 2017, 2018, 2019, 2020, 2022, 2023, 2024, 2025].csv",
    sep=';',
    on_bad_lines='skip',
    encoding='latin1'   # <-- o cp1252 si latin1 falla
)

# Normalizar encabezados
df.columns = df.columns.str.upper().str.strip()

print(df.columns.tolist())  # <-- para verificar

normaliza_direcc(df)
