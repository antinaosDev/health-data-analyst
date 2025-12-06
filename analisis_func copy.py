import streamlit as st
import pandas as pd
import chardet
from datetime import datetime
import numpy as np
import time
import io
import re
import unicodedata
from PIL import Image
import plotly.express as px 
import plotly.figure_factory as ff
import plotly.graph_objects as go
from class_ges import * 
from class_pat import *



#--------------------- FUNCION PARA PROCESAR CSV -----------------------------
@st.cache_data(ttl=600)
def proc_csv(archivo,sep=None):
    try:
        rawdata = archivo.read(10000)
        result = chardet.detect(rawdata)
        encoding = result['encoding'] or 'latin1'
        archivo.seek(0)

        df = pd.read_csv(
            archivo,
            encoding=encoding,
            sep=sep,
            engine='python',
            on_bad_lines='skip'
        )

        if 'RUT' in df.columns:
            df['RUT'] = df['RUT'].astype(str).str.strip()
        return df

    except Exception as e:
        return None

# ------------------ FUNCIONES DE DESCARGA ------------------
def export_to_excel(df,nombre,mes,año,rango):
    excel_buffer = io.BytesIO()
    if 'ANIO_CORTE' in df.columns:
        df = df[(df['ANIO_CORTE'] >= rango[0]) & (df['ANIO_CORTE'] <= rango[1])]

    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DATA')

    excel_buffer.seek(0)
    st.download_button(
        label="📥 Descargar Excel combinado",
        data=excel_buffer,
        file_name=f"{nombre}_{mes}_{año}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

def export_to_csv(df,nombre,año,rango):
    csv_buffer = io.BytesIO()
    if 'ANIO_CORTE' in df.columns:
        df = df[(df['ANIO_CORTE'] >= rango[0]) & (df['ANIO_CORTE'] <= rango[1])]

    csv_content = df.to_csv(index=False).encode('utf-8')
    csv_buffer.write(csv_content)
    csv_buffer.seek(0)
    st.download_button(
        label="📥 Descargar CSV combinado",
        data=csv_buffer,
        file_name=f"{nombre}_{año}.csv",
        mime="text/csv",
        use_container_width=True
    )

def export_to_csv_gen(df,nombre,año):
    csv_buffer = io.BytesIO()
    csv_content = df.to_csv(index=False).encode('utf-8')
    csv_buffer.write(csv_content)
    csv_buffer.seek(0)
    st.download_button(
        label="📥 Descargar CSV combinado",
        data=csv_buffer,
        file_name=f"{nombre}_{año}.csv",
        mime="text/csv",
        use_container_width=True
    )

def export_to_excel_gen(df,nombre,año):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DATA')
    excel_buffer.seek(0)
    st.download_button(
        label="📥 Descargar Excel combinado",
        data=excel_buffer,
        file_name=f"{nombre}_{año}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ------------------ PROCESAMIENTO AGENDA (PRINCIPAL) ------------------
@st.cache_data(ttl=600)
def procesamiento_agenda(lista_dfs):

    # 1. Concatenar los DataFrames
    df_concat = pd.concat(lista_dfs, ignore_index=True)

    # 2. NORMALIZACIÓN DE ENCABEZADOS (A mayúsculas y sin espacios)
    df_concat.columns = df_concat.columns.str.strip().str.upper()

    # 3. RENOMBRADO INTELIGENTE
    # Mapeamos nombres comunes a los nombres exactos que tú quieres
    mapa_correccion = {
        # RUT
        "RUT_PROFESIONAL": "RUT PROFESIONAL",
        "RUT_PROF": "RUT PROFESIONAL",
        "RUN PROFESIONAL": "RUT PROFESIONAL",
        "RUT MEDICO": "RUT PROFESIONAL",
        
        # NOMBRE
        "NOMBRE_PROFESIONAL": "NOMBRE PROFESIONAL",
        "NOMBRES PROFESIONAL": "NOMBRE PROFESIONAL",
        "NOMBRES MEDICO": "NOMBRE PROFESIONAL",
        "PROFESIONAL": "NOMBRE PROFESIONAL", # Si viene todo junto, lo asumimos como Nombre
        
        # MATERNO
        "MATERNO_PROFESIONAL": "MATERNO PROFESIONAL",
        "APELLIDO MATERNO PROFESIONAL": "MATERNO PROFESIONAL",
        "MATERNO MEDICO": "MATERNO PROFESIONAL",
        
        # PATERNO (Por si acaso)
        "PATERNO_PROFESIONAL": "PATERNO PROFESIONAL",
        "APELLIDO PATERNO PROFESIONAL": "PATERNO PROFESIONAL",

        # OTROS
        "AGRUPACION_GES": "AGRUPACION",
        "ESPEC": "ESPECIALIDAD"
    }
    df_concat.rename(columns=mapa_correccion, inplace=True)

    # 4. Procesamiento externo
    df_concat = class_pat(df_concat)

    # 5. Lógica de Totales y Riesgo
    if "TOTAL_UNICAS" in df_concat.columns:
        df_concat["TOTAL"] = df_concat["TOTAL_UNICAS"].fillna(0).astype(int)
    else:
        df_concat["TOTAL"] = 0

    def class_risk(n):
        if n >= 5: return "G3:Riesgo severo"
        elif n >= 2: return "G2:Riesgo moderado"
        elif n == 1: return "G1:Riesgo leve"
        else: return "G0:Personas sanas o sin condiciones detectadas"

    df_concat["RIESGO"] = df_concat["TOTAL"].apply(class_risk)

    # =========================================================================
    # 6. GARANTIZAR COLUMNAS SOLICITADAS
    # =========================================================================
    cols_obligatorias = [
        "RUT PROFESIONAL", 
        "NOMBRE PROFESIONAL",
        "PATERNO PROFESIONAL",
        "MATERNO PROFESIONAL",
        "ESPECIALIDAD", 
        "SUBESPECIALIDAD", 
        "AGRUPACION"
    ]
    
    for col in cols_obligatorias:
        if col not in df_concat.columns:
            # Si no existe en el Excel, crearla con "SIN DATOS"
            df_concat[col] = "SIN DATOS"
        else:
            # Si existe, limpiar
            df_concat[col] = df_concat[col].fillna("SIN DATOS").astype(str).str.strip().str.upper()
            df_concat[col] = df_concat[col].replace(['NAN', 'NONE', 'NAT', 'nan'], "SIN DATOS")

    # =========================================================================
    # 7. LISTA FINAL DE EXPORTACIÓN (Actualizada)
    # =========================================================================
    all_cols = [
        "RUT", "GENERO","DIRECCION", "COMUNA", "PROCEDENCIA", "PAIS DE PROCEDENCIA", "ETNIA PERCEPCION", "ESCOLARIDAD",
        "SITUACION CALLE","ES DISCAPACITADA","ES SENAME","ES EMBARAZADA",
        
        # --- COLUMNAS DEL PROFESIONAL ---
        "RUT PROFESIONAL", 
        "NOMBRE PROFESIONAL",
        "PATERNO PROFESIONAL", 
        "MATERNO PROFESIONAL",
        "ESPECIALIDAD", 
        "SUBESPECIALIDAD", 
        "AGRUPACION",
        # -------------------------------

        "PREVISION", "FECHA NACIMIENTO", "POLICLINICO",
        "ESTABLECIMIENTO", "HORA GENERADA", "ESTADO HORA", "ESTADO ATENCION", "ACCION A TOMAR",
        "FECHA ASIGNADA", "HORA ASIGNADA", "FECHA EJECUTADA", "HORA EJECUTADA", "FECHA ULT MOD", "HORA UTL MOD",
        "TIPO_DIAGNOSTICO 1","TIPO_DIAGNOSTICO 2","TIPO_DIAGNOSTICO 3",
        "DIAGNOSTICO 1","DIAGNOSTICO 2","DIAGNOSTICO 3","ESTADO 1","ESTADO 2","ESTADO 3",
        "DIAGNOSTICO 1_CLASIFICADO","DIAGNOSTICO 2_CLASIFICADO", "DIAGNOSTICO 3_CLASIFICADO",
        "TOTAL_UNICAS", 
        "TOTAL","RIESGO","TELEFONO1","TELEFONO2","TELEFONO3"
    ]

    # FILTRO FINAL
    cols_work = [col for col in all_cols if col in df_concat.columns]
    
    # Crear copia final
    df_final = df_concat[cols_work].copy()
    df_final = df_final.fillna('SIN DATOS')

    # --- Estandarización General ---

    # GENERO
    if "GENERO" in df_final.columns:
        df_final["GENERO"] = df_final["GENERO"].replace({
            "HOMBRE": "MASCULINO", "MUJER": "FEMENINO", "M": "MASCULINO", "F": "FEMENINO"
        })

    # PAIS DE PROCEDENCIA
    if "PAIS DE PROCEDENCIA" in df_final.columns:
        df_final["PAIS DE PROCEDENCIA"] = df_final["PAIS DE PROCEDENCIA"].replace({"SIN INFORMACION": "SIN DATOS"})

    # ETNIA
    if "ETNIA PERCEPCION" in df_final.columns:
        reemplazos_etnia = {
            "MAPUCHE ": "MAPUCHE", "NINGUNO ": "NINGUNO", "COLLA ": "COLLA",
            "DIAGUITA ": "DIAGUITA", "QUECHUA ": "QUECHUA", "ATACAMEÑO ": "ATACAMEÑO",
            "AIMARA ": "AIMARA", "SIN INFORMACION":"SIN DATOS", "NO CONTESTA ": "SIN DATOS",
            "OTRO PUEBLO ORIGINARIO DECLARADO ": "OTRO PUEBLO ORIGINARIO DECLARADO",
            "NO SABE ": "SIN DATOS", "ALACALUFE O KAWASHKAR": "ALACALUFE O KAWESQAR",
            "YAMANA O YAGAN ": "YAMANA O YAGAN", "ATACAMEÑO O LIKANANTAY": "ATACAMEÑO",
            "AYMARA ": "AIMARA", "ALACALUFE O KAWESQAR ": "ALACALUFE O KAWESQAR"
        }
        df_final["ETNIA PERCEPCION"] = df_final["ETNIA PERCEPCION"].replace(reemplazos_etnia)

    # ESCOLARIDAD
    if "ESCOLARIDAD" in df_final.columns:
        df_final["ESCOLARIDAD"] = df_final["ESCOLARIDAD"].replace({
            "NO RESPONDE": "SIN DATOS", "NO RECUERDA": "SIN DATOS", "SIN INFORMACION": "SIN DATOS"
        })

    # PREVISION
    if "PREVISION" in df_final.columns:
        df_final["PREVISION"] = df_final["PREVISION"].astype(str).str.strip().str.upper()
        df_final["PREVISION"] = df_final["PREVISION"].replace({
            "ACTUALIZAR INFORMACION": "SIN DATOS", "SIN INFORMACION": "SIN DATOS",
            "INDIGENCIA": "SIN DATOS", "PARTICULAR (SIN PREVISION)": "SIN DATOS",
            "NO RESPONDE": "SIN DATOS"
        })

    # POLICLINICO
    if "POLICLINICO" in df_final.columns:
        df_final["POLICLINICO"] = df_final["POLICLINICO"].astype(str).str.strip().str.upper()

    # COMUNA
    def normalizar_comuna(comuna):
        if pd.isnull(comuna): return "SIN COMUNA"
        c = re.sub(r"\s*\(.*?\)", "", str(comuna))
        return c.strip().upper()

    if 'COMUNA' in df_final.columns:
        df_final['COMUNA'] = df_final['COMUNA'].apply(normalizar_comuna)

    # Eliminar duplicados
    df_final = df_final.drop_duplicates()

    # --- Calcular EDAD ---
    if "FECHA NACIMIENTO" in df_final.columns:
        df_final["FECHA NACIMIENTO"] = pd.to_datetime(df_final["FECHA NACIMIENTO"], errors='coerce',dayfirst=True)
        hoy = pd.Timestamp.today()
        df_final["EDAD"] = df_final["FECHA NACIMIENTO"].apply(lambda x: hoy.year - x.year - ((hoy.month, hoy.day) < (x.month, x.day)) if pd.notnull(x) else 0)
    else:
        df_final["EDAD"] = 0

    # --- Rango Etario ---
    condiciones = [
        (df_final["EDAD"] >= 0) & (df_final["EDAD"] <= 9),
        (df_final["EDAD"] >= 10) & (df_final["EDAD"] <= 19),
        (df_final["EDAD"] >= 20) & (df_final["EDAD"] <= 29),
        (df_final["EDAD"] >= 30) & (df_final["EDAD"] <= 39),
        (df_final["EDAD"] >= 40) & (df_final["EDAD"] <= 49),
        (df_final["EDAD"] >= 50) & (df_final["EDAD"] <= 59),
        (df_final["EDAD"] >= 60) & (df_final["EDAD"] <= 69),
        (df_final["EDAD"] >= 70) & (df_final["EDAD"] <= 79),
        (df_final["EDAD"] >= 80) & (df_final["EDAD"] <= 89),
        (df_final["EDAD"] >= 90)
    ]
    valores = ["0 A 9", "10 A 19", "20 A 29", "30 A 39", "40 A 49", "50 A 59", "60 A 69", "70 A 79", "80 A 89", "90 O MAS"]
    df_final["RANGO_ETARIO"] = np.select(condiciones, valores, default="SIN DATOS")

    # --- Clasificación Etaria ---
    condiciones_2 = [
        (df_final['EDAD']>=0) & (df_final['EDAD']<=5),
        (df_final['EDAD']>=6) & (df_final['EDAD']<=11),
        (df_final['EDAD']>=12) & (df_final['EDAD']<=18),
        (df_final['EDAD']>=19) & (df_final['EDAD']<=26),
        (df_final['EDAD']>=27) & (df_final['EDAD']<=59),
        (df_final["EDAD"]>=60)
    ]
    valores_2 = ["Primera infancia", "Infancia", "Adolescencia", "Juventud", "Adultez", "Persona mayor"]
    df_final["CLAS_ETARIA"] = np.select(condiciones_2,valores_2,"SIN DATOS")

    # --- Clasificación Salarial ---
    if "PREVISION" in df_final.columns:
        condiciones_3 = [
            df_final["PREVISION"] == "FONASA - A",
            df_final["PREVISION"] == "FONASA - B",
            df_final["PREVISION"] == "FONASA - C",
            df_final["PREVISION"] == "FONASA - D"
        ]
        valores_3 = [
            "Carente de recursos", "Imponible mensual <= $440.000",
            "Imponible mensual > $440.000 y <= $642.400", "Imponible mensual > $642.400"
        ]
        df_final["RANGO_SALARIAL"] = np.select(condiciones_3, valores_3, default="SIN DATOS")
    else:
        df_final["RANGO_SALARIAL"] = "SIN DATOS"

    # --- Fechas Asignadas ---
    MESES_ES = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

    if "FECHA ASIGNADA" in df_final.columns:
        df_final["FECHA ASIGNADA"] = pd.to_datetime(df_final["FECHA ASIGNADA"],errors='coerce',dayfirst=True)
        df_final['DIA_ASIG_HR'] = df_final["FECHA ASIGNADA"].dt.day.astype('Int64')
        df_final['MES_ASIG_HR'] = df_final['FECHA ASIGNADA'].dt.month.map(MESES_ES)
        df_final['ANIO_ASIG_HR'] = df_final["FECHA ASIGNADA"].dt.year.astype('Int64')

    # --- Fechas Ejecutadas ---
    if "FECHA EJECUTADA" in df_final.columns:
        df_final["FECHA EJECUTADA"] = pd.to_datetime(df_final["FECHA EJECUTADA"],errors='coerce',dayfirst=True)
        df_final['DIA_EJEC_HR'] = df_final["FECHA EJECUTADA"].dt.day.astype('Int64')
        df_final['MES_EJEC_HR'] = df_final['FECHA EJECUTADA'].dt.month.map(MESES_ES)
        df_final['ANIO_EJEC_HR'] = df_final["FECHA EJECUTADA"].dt.year.astype('Int64')

        if "FECHA ASIGNADA" in df_final.columns:
            df_final["DIAS_ATENCION"] = (df_final["FECHA EJECUTADA"] - df_final["FECHA ASIGNADA"]).dt.days.astype('Int64')
            df_final["DIAS_ATENCION"] = df_final["DIAS_ATENCION"].clip(lower=0)
        else:
            df_final["DIAS_ATENCION"] = 0

    # --- GES Flags ---
    def check_keyword(fila, cols, keyword):
        for col in cols:
            val = str(fila.get(col, '')).strip().upper()
            if val == keyword: return 'SI'
        return 'NO'

    cols_diag = ['TIPO_DIAGNOSTICO 1', 'TIPO_DIAGNOSTICO 2', 'TIPO_DIAGNOSTICO 3']
    cols_estado = ['ESTADO 1', 'ESTADO 2', 'ESTADO 3']

    df_final['ES_GES'] = df_final.apply(lambda row: check_keyword(row, cols_diag, 'GES'), axis=1)
    df_final['CONF_GES'] = df_final.apply(lambda row: check_keyword(row, cols_estado, 'CONFIRMACION GES'), axis=1)
    df_final['SOSP_GES'] = df_final.apply(lambda row: check_keyword(row, cols_estado, 'SOSPECHA GES'), axis=1)
    df_final['TRAT_GES'] = df_final.apply(lambda row: check_keyword(row, cols_estado, 'TRATAMIENTO GES'), axis=1)

    return df_final


#--------------------- REPORTE PERCAPITA -----------------------------
@st.cache_data(ttl=600)
def reporte_percapita(archivos):
    if archivos:
        lista = []
        progess_text = "Procesando archivos..."
        my_bar = st.progress(0,text=progess_text)
        total = len(archivos)

        for i, archivo in enumerate(archivos):
            df = proc_csv(archivo,sep=',')
            if df is not None:
                lista.append(df)
                my_bar.progress((i + 1) / total, text=f"{i + 1} de {total} archivos procesados")
                time.sleep(0.3)

        if lista:
            df_per = pd.concat(lista, ignore_index=True)
        else:
            st.warning("No se pudo cargar ningún archivo correctamente.")
            return None, None, None

        # UNIFICACION DE COLUMNAS RUN Y DV PARA CREAR RUT
        if 'RUN' in df_per.columns and 'DV' in df_per.columns:
            df_per['RUT'] = df_per['RUN'].astype(str).str.strip() + '-' + df_per['DV'].astype(str).str.upper().str.strip()
        elif 'RUN' in df_per.columns:
            df_per['RUT'] = df_per['RUN'].astype(str)

        # FECHAS CORTE
        df_per['FECHA_CORTE'] = pd.to_datetime(df_per['FECHA_CORTE'], errors="coerce")
        df_per['ANIO_CORTE'] = df_per['FECHA_CORTE'].dt.year
        MESES_ES = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
        df_per['MES_CORTE'] = df_per['FECHA_CORTE'].dt.month.map(MESES_ES)

        # EDAD
        df_per["FECHA_NACIMIENTO"] = pd.to_datetime(df_per["FECHA_NACIMIENTO"], errors='coerce')
        hoy = pd.Timestamp.today()
        df_per["EDAD"] = df_per["FECHA_NACIMIENTO"].apply(lambda x: hoy.year - x.year - ((hoy.month, hoy.day) < (x.month, x.day)) if pd.notnull(x) else None)

        # GENERO
        if 'GENERO' in df_per.columns:
            df_per['GENERO'] = df_per['GENERO'].replace({'HOMBRE':'MASCULINO','M':'MASCULINO','MUJER':'FEMENINO','F':'FEMENINO'})

        # UBICACION CENTROS
        condicion_4 = [
            (df_per["NOMBRE_CENTRO"] == "Posta De Salud Rural Huamaqui"),
            (df_per["NOMBRE_CENTRO"] == "Posta De Salud Rural Huentelar"),
            (df_per["NOMBRE_CENTRO"] == "Posta De Salud Rural Malalche"),
            (df_per["NOMBRE_CENTRO"] == "Centro De Salud Familiar Chol Chol"),
        ]
        valor_lat = ['-38.459427', '-38.499904', '-38.574594', '-38.607155']
        valor_long = ['-72.984437', '-72.885185', '-72.945315', '-72.842595']

        df_per["LAT_CENTRO"] = np.select(condicion_4,valor_lat,"SIN DATOS")
        df_per["LONG_CENTRO"] = np.select(condicion_4,valor_long,"SIN DATOS")

        # RANGO ETARIO
        condiciones_5 = [
            (df_per['EDAD']>=0) & (df_per['EDAD']<=5),
            (df_per['EDAD']>=6) & (df_per['EDAD']<=11),
            (df_per['EDAD']>=12) & (df_per['EDAD']<=18),
            (df_per['EDAD']>=19) & (df_per['EDAD']<=26),
            (df_per['EDAD']>=27) & (df_per['EDAD']<=59),
            (df_per["EDAD"]>=60)
        ]
        valores_5 = ["Primera infancia", "Infancia", "Adolescencia", "Juventud", "Adultez", "Persona mayor"]
        df_per['RANGO_ETARIO'] = np.select(condiciones_5,valores_5,'SIN DATOS')

        # DUPLICADOS
        df_per.drop_duplicates(inplace=True)

        # AUTORIZADOS
        if 'ACEPTADO_RECHAZADO' in df_per.columns:
            df_per_auth = df_per[(df_per['ACEPTADO_RECHAZADO'] == 'ACEPTADO') & (df_per['MES_CORTE'] == 'Septiembre')]
            col_elem = ["RUN","DV","TRASLADO_POSITIVO","TRASLADO_NEGATIVO","EXBLOQUEADO","RECHAZADO_PREVISIONAL","RECHAZADO_FALLECIDO","AUTORIZADO","ACEPTADO_RECHAZADO","MOTIVO"]
            col_elem = [c for c in col_elem if c in df_per_auth.columns]
            df_per_auth.drop(col_elem,axis=1,inplace=True)
        else:
            df_per_auth = df_per.copy()

        # FALLECIDOS
        if 'MOTIVO' in df_per.columns:
            df_per_fall = df_per[df_per['MOTIVO'] == 'RECHAZADO FALLECIDO']
            df_per_fall.drop_duplicates(subset='RUT', inplace=True)
            col_df = ["RUT", "ANIO_CORTE", "MES_CORTE"]
            col_df = [c for c in col_df if c in df_per_fall.columns]
            df_per_fall = df_per_fall[col_df]
        else:
             df_per_fall = pd.DataFrame()

    return df_per,df_per_auth,df_per_fall


@st.cache_data(ttl=600)
def normaliza_direcc(df):
    
    # --- Funciones de limpieza ---
    def normalizar_texto(texto):
        texto = str(texto).upper()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        return texto

    def limpiar_basico(texto):
        texto = re.sub(r'[^A-Z0-9Ñ\s]', ' ', texto)  
        texto = re.sub(r'\s+', ' ', texto).strip()   
        return texto

    def normalizar_abreviaturas(texto):
        reemplazos = {
            r'\bN[º°?.]?\b': ' NUMERO ', r'\bS/N\b': ' SIN NUMERO ', r'\bSN\b': ' SIN NUMERO ',
            r'\bCAM\b': ' CAMINO ', r'\bLG\b': ' LUGAR ', r'\bPJE\b': ' PASAJE ',
        }
        for patron, reemplazo in reemplazos.items():
            texto = re.sub(patron, reemplazo, texto)
        return texto

    errores_comunes = {
        "CARRERRI E": "CARRERRENE", "CARRERRIA": "CARRERRENE",
        "CARRERRIÑE": "CARRERRENE", "CHOL CHOL": "CHOLCHOL",
    }

    def corregir_errores(texto):
        for mal, bien in errores_comunes.items():
            texto = texto.replace(mal, bien)
        return texto

    def limpiar_direccion(texto):
        texto = normalizar_texto(texto)
        texto = limpiar_basico(texto)
        texto = normalizar_abreviaturas(texto)
        texto = corregir_errores(texto)
        return texto

    if 'DIRECCION' in df.columns:
        df['DIRECCION_NORM'] = df['DIRECCION'].apply(limpiar_direccion)
    else:
        df['DIRECCION_NORM'] = "SIN DATOS"

    if 'DIRECCION' in df.columns:
        print(df[['DIRECCION', 'DIRECCION_NORM']].head(20))

    sector_a_comunidad = {
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
    "LOS CARRIZOS": "Los carrizos",
    "LOS CARRISOS": "Los carrizos",
    "CARRIZOS": "Los carrizos",
    "CARRRISOS": "Los carrizos",
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

    # Diccionario de sectores a distritos
    sector_a_distrito = {
        "MALALCHE ALTO": "repocura",
        "ALTO":"repocura",
        "CHOLCHOL": "cholchol",
        "CULLINCO": "repocura",
        "RAPAHUE": "rapahue",
        "CURACO TRAÑI TRAÑI": "cholchol",
        "CURACO": "cholchol",
        "REPOCURA": "repocura",
        "HUECHUCON": "carirriñe",
        "HUIÑOCO": "carirriñe",
        "CARIRRIÑE": "carirriñe",
        "LAUNACHE": "repocura",
        "ROMULHUE": "carirriñe",
        "COIHUE CURACO": "cholchol",
        "LLANQUINAO": "tranahuillin",
        "COILACO": "cholchol",
        "HUAMAQUI":  "repocura",  
        "COIHUE":"cholchol",
        "CARRERRE":"carirriñe",
        "RUCUPURA":"repocura",
        "HUINOCO":"carirriñe",
        "CARRIRRE":"carirriñe",
        "RUKAPANGUI":"rapahue",
        "RUKA":"rapahue",
        "DOLLINCO":"rapahue",
        "ANCAPULLI":"repocura",
        "QUIRQUEN":"repocura",
        "CARRERENI":"carirriñe",
        "QUILQUEN":"repocura",
        "RAHUE":"rapahue",
        "COPINCHE":"carirriñe",
        "PRITACO":"cholchol",
        "TOSCA":"cholchol",
        "CARRERRENE":"carirriñe",
        "RENACO":"tranahuillin",
        "CARRERRINE":"carirriñe",
        "PASTALES":"tranahuillin",
        "RUKAPAGUE":"rapahue",
        "CAUTINCHE":"carirriñe",
        "HUICHUCON":"carirriñe",
        "CARRERRENI":"carirriñe",
        "BISQUICO":"tranahuillin",
        "QUILACO":"cholchol",
        "HUEICO":"repocura",
        "PEMURREHUE":"carirriñe",
        "HUITRAMALAL":"repocura",
        "LA FORESTA":"tranahuillin",
        "HUENTELAR":"repocura",
        "CARRERI":"carirriñe",
        "RUPANGUI":"rapahue",
        "RUCAPANJUE":"rapahue",
        "RUKAPANGUI":"rapahue",
        "CARRARRE":"carirriñe",
        "RUCAPANHUE":"rapahue",
        "RINCON":"repocura",
        "HUIRILEF":"cholchol",
        "COLILACO":"cholchol",
        "RANACO":"tranahuillin",
        "MALLALCHE":"carirriñe",
        "CARRERENE":"carirriñe",
        "COHIHUE":"cholchol",
        "PITRCO":"cholchol",
        "CHOL":"cholchol",
        "CCHOL":"cholchol",
        "CATRIMALAL":"carirriñe",
        "CHIVILCOYAN":"carirriñe",
        "HUENTELER":"repocura",
        "CARERRE":"carirriñe",
        "CARRIRREA":"carrirriñe",
        "ANCAPULLA":"repocura",
        "HUAMAQU":"repocura",
        "HUAMAQUE":"repocura",
        "CIOHUE":"cholchol",
        "PICUTA":"rapahue",
        "HUAMPOMALLIN":"cholchol",
        "HUECH":"carirriñe",
        "GUECHUCON":"carirriñe",
        "GUECH":"carirriñe",
        "TRANAHULLIN":"tranahuillin",
        "TRANITRANI":"cholchol",
        "QUILIMANZANO":"carirriñe",
        "CARRIRRINE":"carirriñe",
        "TRAMAHUILLIN":"tranahuillin",
        "QUILI":"carirriñe",
        "CARRE":"carirriñe",
        "CAUTINCE":"carirriñe",
        "RINE":"carirriñe",
        "TRANAULLIN":"tranahuillin",
        "TRNAHUILLIN":"tranahuillin",
        "MALLACHE":"carirriñe",
        "RUCA":"rapahue",
        "PANGUE":"rapahue",
        "MALALCE":"carirriñe",
        "NOTROMAHUIDA":"tranahuillin",
        "QUELIMANZANO":"carirriñe",
        "MALALCHE":"carirriñe",
        "QUELI":"carirriñe",
        "MANZANO":"carirriñe",
        "LOS CARRIZOS": "cholchol",
        "DURAZNOS":"cholchol",
        "REPUCURA":"repocura",
        "CARRIRRENE":"carirriñe",
        "MADILHUE":"repocura",
        "CARRERINE":"carirriñe",
        "PEMU":"tranahuillin",
        "REHUE":"tranahuillin",
        "MALACHE":"carirriñe",
        "SECTOR LOS DURAZNOS": "cholchol",
        "PITRACO BANDERA": "cholchol",
        "TRANAHUILLIN": "tranahuillin",
        "CUYINCO": "repocura",
        "AYEHUECO":"carirriñe",
        "AYEH":"carirriñe",
        "AYEGUE":"carirriñe",
        "ALLEHUECO":"carirriñe",
        "ALLEGUECO":"carirriñe",
        "ALLEG":"carirriñe",
        "NAHUEL":"repocura",
        "RUCAPANGUE": "rapahue",
        "BOLDOCHE": "carirriñe",
        "PITRACO": "cholchol",
        "SANTA CAROLINA": "cholchol",
        "PEUCHEN": "cholchol",
        "CURANILAHUE": "cholchol",
        "HIÑOCO": "carirriñe",
        "SANTA ROSA": "tranahuillin",
        "VILLA":"cholchol",
        "PIUCHEN":"cholchol",
        "VISQUICO":"tranahuillin",
        "CODIHUE":"rapahue",
        "CODIHUE 0310":"rapahue",
        "CODIHUE S":"rapahue",
        "MALACHI":"carirriñe",
        "MALANCHE":"carirriñe",
        "MALALYE":"carirriñe",
        "MALALCHA":"carirriñe",
        "MAALCHE":"carirriñe",
        "COIPUCO":"repocura",
        "TRA I TRA I":"cholchol",
        "PITRA":"cholchol",
        "CAUTIMCHE":"carirriñe",
        "TRANAMULLIN":"tranahuillin",
        "BOLILCHE":"carirriñe",
        "TROMEGUIELU":"carirriñe",
        "TROMENUELO":"carirriñe",
        "TROMENELO":"carirriñe",
        "TROME IELO":"carirriñe",
        "TROMEYELO":"carirriñe",
        "TROMEGUIELO":"carirriñe",
        "TROMENIELO":"carirriñe",
        "BOYECO":"tranahuillin",
        "BOY":"tranahuillin",
        "TRANA":"tranahuillin",
        "TROMEN":"tranahuillin",
        "TROMIA ELO":"carirriñe",
        "TROMILLELO":"carirriñe",
        "TROMINELO":"carirriñe",
        "NUTR":"tranahuillin",
        "TRANI TRANI":"cholchol",
        "TROMIYELO":"carirriñe",
        "HUENTELAL":"repocura",
        "DOYINCO":"rapahue",
        "DOLL":"rapahue",
        "PEREZ": "cholchol",
        "PERES": "cholchol",
        "PINTO": "cholchol",
        "PRAT": "cholchol",
        "BALMACEDA": "cholchol",
        "ERRAZURIZ": "cholchol",
        "ERAZURIZ": "cholchol",
        "LASTARRIA": "cholchol",
        "LAZCANO": "cholchol",
        "OHIGGINS": "cholchol",
        "O'HIGGINS": "cholchol",
        "SAAVEDRA": "cholchol",
        "PORTALES": "cholchol",
        "MACKENNA": "cholchol",
        "MANUEL MONTT": "cholchol",
        "RECREO": "cholchol",
        "ALDUNATE": "cholchol",
        "RAYEN": "cholchol",
        "NUEVA UNO": "cholchol",
        "NUEVA DOS": "cholchol",
        "HUI OCO":"carirriñe",
        "SECTOR DURAZNO":"cholchol",
        "ANCAP":"carirriñe",
        "COI":"cholchol",
        "CARRI":"carirriñe",
        "HUI":"carirriñe",
        "TRAA":"cholchol",
        "PASAJE LA ARAUCARIA  NUMERO  21": "cholchol",
        "COLO COLO": "cholchol",
        "LOS PIONEROS": "cholchol",
        "ANTONIO": "cholchol",
        "ANCULEO": "cholchol",
        "AMUNATEGUI S": "cholchol",
        "ERRAZURIS 0213": "cholchol",
        "CALLE CL NAMBRARD 06005 DP 110 BL 2 V ALLIPEN S  NUMERO": "cholchol",
        "SMIDT S": "cholchol",
        "IGNACIO": "cholchol",
        "DURAZNO": "cholchol",
        "PIONEROS": "cholchol",
        "MAITENES": "cholchol",
        "TARRIA": "cholchol",
        "MACKENA": "cholchol",
        "LASCANO": "cholchol",
        "ANCAPULLY": "carirriñe",
        "MONTT": "cholchol",
        "CALLE 2471019 S  NUMERO": "cholchol",
        "AUDOLIA MILLAPAN  NUMERO  1101 VISTA HERMOSA": "cholchol",
        "ERRASURIZ": "cholchol",
        "LICEO GUACOLDA": "cholchol",
        "LINGUE MALLIN": "cholchol",
        "LAS TARRIAS": "cholchol",
        "COIGUE": "cholchol",
        "SANTA LAURA": "cholchol",
        "ANCAPULI": "carirriñe",
        "SHMIT": "cholchol",
        "LAZCA": "cholchol",
        "CHAMIL": "cholchol",
        "CALLE IGN S": "cholchol",
        "ERCILLA": "cholchol",
        "LAS HORTENCIAS": "cholchol",
        "CALLE LOS TREBOLES": "cholchol",
        "CARRIRRI E": "carirriñe",
        "PELLAHUEN": "repocura",
        "ZEDAN": "cholchol",
        "PONEROS": "cholchol",
        "SAN MATEO": "cholchol",
        "CALLE ERCILLA  NUMERO  529": "cholchol",
        "MILLAPAN": "cholchol",
        "CALLE HUI OCO S  NUMERO  S  NUMERO": "carirriñe",
        "TARRIAS": "cholchol",
        "LOS SAUCES 150": "cholchol",
        "CALLE GALVARINO": "cholchol",
        "CALLE LAUTARO  NUMERO  429": "cholchol",
        "POIOTRACO":"cholchol",
        "AMUNATEGUI":"cholchol",
        "SMITH":"cholchol",
        "SMITT":"cholchol",
        "SMIHT":"cholchol",
        "CASTELLON":"cholchol",
        "CASRELLON":"cholchol",
        "CULL":"repocura",
        "SCH":"cholchol"
    }

    def asignar_comunidad(texto):
        texto = texto.upper()
        for sector, distrito in sector_a_comunidad.items():
            if sector in texto:
                if isinstance(distrito, list): return distrito[0]
                return distrito
        return "NO_ESPECIFICADO"

    def asignar_distrito(texto):
        texto = texto.upper()
        for sector, distrito in sector_a_distrito.items():
            if sector in texto:
                if isinstance(distrito, list): return distrito[0]
                return distrito
        return "NO_ESPECIFICADO"

    df['DISTRITO'] = df['DIRECCION_NORM'].apply(asignar_distrito)
    df['COMUNIDAD'] = df['DIRECCION_NORM'].apply(asignar_comunidad)

    if 'DIRECCION_NORM' in df.columns:
        print(df[['DIRECCION_NORM', 'DISTRITO']].head(20))

    df['SECTOR'] = 'NO_ESPECIFICADO'
    df['LAT_SEC'] = 'NO_ESPECIFICADO'
    df['LON_SEC'] = 'NO_ESPECIFICADO'

    df.loc[df['DISTRITO'].isin(['carirriñe', 'repocura', 'rapahue']), 'SECTOR'] = 'Luna'
    df.loc[df['DISTRITO'].isin(['cholchol', 'tranahuillin']), 'SECTOR'] = 'Sol'

    df.loc[df['DISTRITO'].isin(['repocura']), 'LAT_SEC'] = '-38.529326'
    df.loc[df['DISTRITO'].isin(['repocura']), 'LON_SEC'] = '-72.957807'
    df.loc[df['DISTRITO'].isin(['carirriñe']), 'LAT_SEC'] = '-38.601780'
    df.loc[df['DISTRITO'].isin(['carirriñe']), 'LON_SEC'] = '-72.959978'
    df.loc[df['DISTRITO'].isin(['rapahue']), 'LAT_SEC'] = '-38.679850'
    df.loc[df['DISTRITO'].isin(['rapahue']), 'LON_SEC'] = '-72.847577'
    df.loc[df['DISTRITO'].isin(['tranahuillin']), 'LAT_SEC'] = '-38.640449'
    df.loc[df['DISTRITO'].isin(['tranahuillin']), 'LON_SEC'] = '-72.794477'
    df.loc[df['DISTRITO'].isin(['cholchol']), 'LAT_SEC'] = '-38.563485'
    df.loc[df['DISTRITO'].isin(['cholchol']), 'LON_SEC'] = '-72.838224'

    df.drop(columns=['DIRECCION'], errors='ignore', inplace=True)
    
    return df

@st.cache_resource
def load_logo(path):
    try:
        return Image.open(path)
    except:
        return None

def footer():
    with st.container():
        col1, col2, col3, col4 = st.columns([3,1,5,1])
        with col2:
            try:
                logo = load_logo("logo_alain.png")
                if logo: st.image(logo, width=150)
            except: pass
        with col3:
            st.markdown("""
                <div style='text-align: left; color: #888888; font-size: 20px; padding-bottom: 20px;'>
                    💼 Aplicación desarrollada por <strong>Alain Antinao Sepúlveda</strong> <br>
                    📧 Contacto: <a href="mailto:alain.antinao.s@gmail.com" style="color: #4A90E2;">alain.antinao.s@gmail.com</a> <br>
                    🌐 Más información en: <a href="https://alain-antinao-s.notion.site/Alain-C-sar-Antinao-Sep-lveda-1d20a081d9a980ca9d43e283a278053e" target="_blank" style="color: #4A90E2;">Mi página personal</a>
                </div>
            """, unsafe_allow_html=True)