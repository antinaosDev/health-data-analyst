from narwhals import col
import streamlit as st
import pandas as pd
import chardet
from datetime import datetime
import numpy as np
import time
from class_ges import *
import io
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from PIL import Image



#--------------------- FUNCION PARA PROCESAR CSV -----------------------------
@st.cache_data(ttl=600) #Para carga mas rapida
def proc_csv(archivo):
    try:
        rawdata = archivo.read(10000)
        result = chardet.detect(rawdata)
        encoding = result['encoding'] or 'latin1'
        archivo.seek(0)

        df = pd.read_csv(
            archivo,
            encoding=encoding,
            sep=None,
            engine='python',
            on_bad_lines='skip'
        )

        if 'RUT' in df.columns:
            df['RUT'] = df['RUT'].astype(str).str.strip()
        return df

    except Exception as e:
        st.error(f"No se pudo leer el archivo {getattr(archivo, 'name', 'archivo desconocido')}: {e}")
        return None


# ------------------ DESCARGA EN EXCEL ------------------
def export_to_excel(df,nombre,mes,año,rango):
    excel_buffer = io.BytesIO()

    #Filtrado del DF
    df = df[(df['ANIO_CORTE'] >= rango[0]) & (df['ANIO_CORTE'] <= rango[1])]

    # Guardar el DataFrame en formato Excel en el buffer
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DATA')

    excel_buffer.seek(0)

    # Botón de descarga
    st.download_button(
        label="📥 Descargar Excel combinado",
        data=excel_buffer,
        file_name=f"{nombre}_{mes}_{año}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True
    )

def export_to_csv(df,nombre,año,rango):
    csv_buffer = io.BytesIO()

    #Filtrado del DF
    df = df[(df['ANIO_CORTE'] >= rango[0]) & (df['ANIO_CORTE'] <= rango[1])]


    csv_content = df.to_csv(index=False).encode('utf-8')
    csv_buffer.write(csv_content)
    csv_buffer.seek(0)

    st.download_button(
        label="📥 Descargar CSV combinado",
        data=csv_buffer,
        file_name=f"{nombre}_{año}.csv",
        mime="text/csv",use_container_width=True
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
        mime="text/csv",use_container_width=True
        )

def export_to_excel_gen(df,nombre,año):
    excel_buffer = io.BytesIO()


    # Guardar el DataFrame en formato Excel en el buffer
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DATA')

    excel_buffer.seek(0)

    # Botón de descarga
    st.download_button(
        label="📥 Descargar Excel combinado",
        data=excel_buffer,
        file_name=f"{nombre}_{año}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True
    )

@st.cache_data(ttl=600)
def procesamiento_agenda(lista_dfs):

    # Concatenar los DataFrames
    df_concat = pd.concat(lista_dfs, ignore_index=True)

    
    cols_work = [
        "RUT", "GENERO", "COMUNA", "PROCEDENCIA", "PAIS DE PROCEDENCIA", "ETNIA PERCEPCION", "ESCOLARIDAD",
        "SITUACION CALLE","ES DISCAPACITADA","ES SENAME","ES EMBARAZADA","RUT PROFESIONAL",
        "PREVISION", "FECHA NACIMIENTO", "ESPECIALIDAD", "SUBESPECIALIDAD", "POLICLINICO", "AGRUPACION", 
        "ESTABLECIMIENTO", "HORA GENERADA", "ESTADO HORA", "ESTADO ATENCION", "ACCION A TOMAR", 
        "FECHA ASIGNADA", "HORA ASIGNADA", "FECHA EJECUTADA", "HORA EJECUTADA", "FECHA ULT MOD", "HORA UTL MOD",
        "TIPO_DIAGNOSTICO 1","TIPO DIAGNOSTICO 2","TIPO DIAGNOSTICO 3",
        "DIAGNOSTICO 1","DIAGNOSTICO 2","DIAGNOSTICO 3"
    ]

    df_concat = df_concat[cols_work]
    df_concat = df_concat.fillna('SIN DATOS')

    # Estandarización por columnas

    # GENERO
    df_concat["GENERO"] = df_concat["GENERO"].replace({
        "HOMBRE": "MASCULINO",
        "MUJER": "FEMENINO"
    })

    # PAIS DE PROCEDENCIA
    df_concat["PAIS DE PROCEDENCIA"] = df_concat["PAIS DE PROCEDENCIA"].replace({
        "SIN INFORMACION": "SIN DATOS"
    })

    # ETNIA PERCEPCION
    df_concat["ETNIA PERCEPCION"] = df_concat["ETNIA PERCEPCION"].replace({
        "MAPUCHE ": "MAPUCHE",
        "NINGUNO ": "NINGUNO",
        "COLLA ": "COLLA",
        "DIAGUITA ": "DIAGUITA",
        "QUECHUA ": "QUECHUA",
        "ATACAMEÑO ": "ATACAMEÑO",
        "AIMARA ": "AIMARA",
        "SIN INFORMACION":"SIN DATOS",
        "NO CONTESTA ": "SIN DATOS",
        "OTRO PUEBLO ORIGINARIO DECLARADO ": "OTRO PUEBLO ORIGINARIO DECLARADO",
        "NO SABE ": "SIN DATOS",
        "ALACALUFE O KAWASHKAR": "ALACALUFE O KAWESQAR",
        "YAMANA O YAGAN ": "YAMANA O YAGAN",
        "ATACAMEÑO O LIKANANTAY": "ATACAMEÑO",
        "AYMARA ": "AIMARA",
        "ALACALUFE O KAWESQAR ": "ALACALUFE O KAWESQAR"
    })

    # ESCOLARIDAD
    df_concat["ESCOLARIDAD"] = df_concat["ESCOLARIDAD"].replace({
        "NO RESPONDE": "SIN DATOS",
        "NO RECUERDA": "SIN DATOS",
        "SIN INFORMACION": "SIN DATOS"
    })

    # PREVISION
    df_concat["PREVISION"] = df_concat["PREVISION"].astype(str).str.strip().str.upper()
    df_concat["PREVISION"] = df_concat["PREVISION"].replace({
        "ACTUALIZAR INFORMACION": "SIN DATOS",
        "SIN INFORMACION": "SIN DATOS",
        "INDIGENCIA": "SIN DATOS",
        "PARTICULAR (SIN PREVISION)": "SIN DATOS",
        "NO RESPONDE": "SIN DATOS"
    })

    #POLICLINICO
    df_concat["POLICLINICO"] = df_concat["POLICLINICO"].astype(str).str.strip().str.upper()

    import re

    # Función para limpiar nombres de comuna
    def normalizar_comuna(comuna):
        if pd.isnull(comuna):
            return "SIN COMUNA"
        # Elimina cualquier texto entre paréntesis y sus espacios
        comuna = re.sub(r"\s*\(.*?\)", "", comuna)
        # Elimina espacios extra
        comuna = comuna.strip()
        # Convierte a mayúsculas
        comuna = comuna.upper()
        return comuna

    # Aplicar normalización
    df_concat['COMUNA'] = df_concat['COMUNA'].apply(normalizar_comuna)


    #Eliminar duplicados
    df_concat = df_concat.drop_duplicates()

    #----------------Calcular edad---------------------------------------
    # Asegura que la columna esté en formato datetime
    df_concat["FECHA NACIMIENTO"] = pd.to_datetime(df_concat["FECHA NACIMIENTO"], errors='coerce')

    # Fecha actual
    hoy = pd.Timestamp.today()

    # Calcular edad
    df_concat["EDAD"] = df_concat["FECHA NACIMIENTO"].apply(lambda x: hoy.year - x.year - ((hoy.month, hoy.day) < (x.month, x.day)) if pd.notnull(x) else None)

    #---------------Calculo de rango etario ----------------------------
    # Define las condiciones por rango de edad
    condiciones = [
        (df_concat["EDAD"] >= 0) & (df_concat["EDAD"] <= 9),
        (df_concat["EDAD"] >= 10) & (df_concat["EDAD"] <= 19),
        (df_concat["EDAD"] >= 20) & (df_concat["EDAD"] <= 29),
        (df_concat["EDAD"] >= 30) & (df_concat["EDAD"] <= 39),
        (df_concat["EDAD"] >= 40) & (df_concat["EDAD"] <= 49),
        (df_concat["EDAD"] >= 50) & (df_concat["EDAD"] <= 59),
        (df_concat["EDAD"] >= 60) & (df_concat["EDAD"] <= 69),
        (df_concat["EDAD"] >= 70) & (df_concat["EDAD"] <= 79),
        (df_concat["EDAD"] >= 80) & (df_concat["EDAD"] <= 89),
        (df_concat["EDAD"] >= 90)
    ]

    # Resultados correspondientes
    valores = [
        "0 A 9",
        "10 A 19",
        "20 A 29",
        "30 A 39",
        "40 A 49",
        "50 A 59",
        "60 A 69",
        "70 A 79",
        "80 A 89",
        "90 O MAS"
    ]

    # Asignar rango etario
    df_concat["RANGO_ETARIO"] = np.select(condiciones, valores, default="SIN DATOS")

    #-------------------------CLASIFICACION ETARIA------------------------------------

    condiciones_2 = [
        (df_concat['EDAD']>=0) & (df_concat['EDAD']<=5),
        (df_concat['EDAD']>=6) & (df_concat['EDAD']<=11),
        (df_concat['EDAD']>=12) & (df_concat['EDAD']<=18),
        (df_concat['EDAD']>=19) & (df_concat['EDAD']<=26),
        (df_concat['EDAD']>=27) & (df_concat['EDAD']<=59),
        (df_concat["EDAD"]>=60)
    ]

    valores_2 = [
        "Primera infancia",
        "Infancia",
        "Adolescencia",
        "Juventud",
        "Adultez",
        "Persona mayor"
    ]

    df_concat["CLAS_ETARIA"] = np.select(condiciones_2,valores_2,"SIN DATOS")

    #----------------CLASIFICACION SALARIAL-----------------------
    condiciones_3 = [
        df_concat["PREVISION"] == "FONASA - A",
        df_concat["PREVISION"] == "FONASA - B",
        df_concat["PREVISION"] == "FONASA - C",
        df_concat["PREVISION"] == "FONASA - D"
    ]

    valores_3 = [
        "Carente de recursos",
        "Imponible mensual <= $440.000",
        "Imponible mensual > $440.000 y <= $642.400",
        "Imponible mensual > $642.400"
    ]

    df_concat["RANGO_SALARIAL"] = np.select(condiciones_3, valores_3, default="SIN DATOS")

    #---------------------SE CREA COLUMNA DE MES Y AÑO PARA IDENTIFICAR CADA PLANILLA-----------------------------------
    df_concat["FECHA ASIGNADA"] = pd.to_datetime(df_concat["FECHA ASIGNADA"],errors='coerce')

    #creacion columna dia
    df_concat['DIA_ASIG_HR'] = df_concat["FECHA ASIGNADA"].dt.day.astype('Int64')
    #creacion columna mes
    df_concat['MES_ASIG_HR'] = df_concat["FECHA ASIGNADA"].dt.month_name(locale='es_ES')
    #creacion columna año
    df_concat['ANIO_ASIG_HR'] = df_concat["FECHA ASIGNADA"].dt.year.astype('Int64')
    

    #-----------------CREA COLUMNA DE MES Y AÑO PARA DETERMINAR LA EJECUCION DE LA HORA-------------------------------
    df_concat["FECHA EJECUTADA"] = pd.to_datetime(df_concat["FECHA EJECUTADA"],errors='coerce')

    #creacion columna mes
    df_concat['DIA_EJEC_HR'] = df_concat["FECHA EJECUTADA"].dt.day.astype('Int64')
    #creacion columna mes
    df_concat['MES_EJEC_HR'] = df_concat["FECHA EJECUTADA"].dt.month_name(locale='es_ES')
    #creacion columna año
    df_concat['ANIO_EJEC_HR'] = df_concat["FECHA EJECUTADA"].dt.year.astype('Int64')

    #--------------Calculo de los dias entre asignacion de hora y atencion----------------------------------------
    # Calcular diferencia en días
    df_concat["DIAS_ATENCION"] = (df_concat["FECHA EJECUTADA"] - df_concat["FECHA ASIGNADA"]).dt.days.astype('Int64')

   
    # Reemplazar negativos por 0
    df_concat["DIAS_ATENCION"] = df_concat["DIAS_ATENCION"].clip(lower=0)

    # GES: búsqueda parcial
    def es_ges(fila):
        # Revisar si alguna celda tiene exactamente "GES" (ignorando mayúsculas/minúsculas y espacios)
        return 'SI' if any(str(f).strip().upper() == 'GES' for f in [
            fila['TIPO_DIAGNOSTICO 1'], 
            fila['TIPO DIAGNOSTICO 2'], 
            fila['TIPO DIAGNOSTICO 3']
        ]) else 'NO'


    df_concat['GES'] = df_concat.apply(es_ges, axis=1)

    return df_concat


        
#--------------------- REPORTE PERCAPITA -----------------------------
@st.cache_data(ttl=600)
def reporte_percapita(archivos):

    if archivos:
        lista = []

        progess_text = "Procesando archivos..."
        my_bar = st.progress(0,text=progess_text)
        total = len(archivos)

        for i, archivo in enumerate(archivos):
            df = proc_csv(archivo)
            if df is not None:
                lista.append(df)
                my_bar.progress((i + 1) / total, text=f"{i + 1} de {total} archivos procesados")
                time.sleep(0.3)

        if lista:
            df_per = pd.concat(lista, ignore_index=True)
        else:
            st.warning("No se pudo cargar ningún archivo correctamente.")

        #-------------------PROCESAR ARCHIVOS---------------------------
        #UNIFICACION DE COLUMNAS RUN Y DV PARA CREAR RUT
        df_per['RUT'] = df_per['RUN'].astype(str).str.strip() + '-' + df_per['DV'].astype(str).str.upper().str.strip()

        #SE EXTRAE MES Y AÑO DE LA FECHA_CORTE
        df_per['FECHA_CORTE'] = pd.to_datetime(df_per['FECHA_CORTE'], errors="coerce") #coerce convierte fechas inválidas en NaT

        df_per['ANIO_CORTE'] = df_per['FECHA_CORTE'].dt.year
        df_per['MES_CORTE'] = df_per['FECHA_CORTE'].dt.month_name(locale='es_ES')

        #----------------Calcular edad---------------------------------------
        # Asegura que la columna esté en formato datetime
        df_per["FECHA_NACIMIENTO"] = pd.to_datetime(df_per["FECHA_NACIMIENTO"], errors='coerce')

        # Fecha actual
        hoy = pd.Timestamp.today()

        # Calcular edad
        df_per["EDAD"] = df_per["FECHA_NACIMIENTO"].apply(lambda x: hoy.year - x.year - ((hoy.month, hoy.day) < (x.month, x.day)) if pd.notnull(x) else None)



        #Reemplazo de valores mal categorizados
        df_per['GENERO'] = df_per['GENERO'].replace({
            'HOMBRE':'MASCULINO',
            'M':'MASCULINO',
            'MUJER':'FEMENINO',
            'F':'FEMENINO'
        })

        #---------------------Determinar la Ubicación de los centros---------------------------------------
        condicion_4 = [
            (df_per["NOMBRE_CENTRO"] == "Posta De Salud Rural Huamaqui"),
            (df_per["NOMBRE_CENTRO"] == "Posta De Salud Rural Huentelar"),
            (df_per["NOMBRE_CENTRO"] == "Posta De Salud Rural Malalche"),
            (df_per["NOMBRE_CENTRO"] == "Centro De Salud Familiar Chol Chol"),
        ]

        valor_lat = [
            '-38.459427',
            '-38.499904',
            '-38.574594',
            '-38.607155'
        ]

        valor_long = [
            '-72.984437',
            '-72.885185',
            '-72.945315',
            '-72.842595'
        ]

        df_per["LAT_CENTRO"] = np.select(condicion_4,valor_lat,"SIN DATOS")
        df_per["LONG_CENTRO"] = np.select(condicion_4,valor_long,"SIN DATOS")

         #-------------------------CLASIFICACION ETARIA------------------------------------

        condiciones_5 = [
            (df_per['EDAD']>=0) & (df_per['EDAD']<=5),
            (df_per['EDAD']>=6) & (df_per['EDAD']<=11),
            (df_per['EDAD']>=12) & (df_per['EDAD']<=18),
            (df_per['EDAD']>=19) & (df_per['EDAD']<=26),
            (df_per['EDAD']>=27) & (df_per['EDAD']<=59),
            (df_per["EDAD"]>=60)
        ]

        valores_5 = [
            "Primera infancia",
            "Infancia",
            "Adolescencia",
            "Juventud",
            "Adultez",
            "Persona mayor"
        ]

        df_per['RANGO_ETARIO'] = np.select(condiciones_5,valores_5,'SIN DATOS')


        #Limpieza de registros duplicados DF GLOBAL
        df_per.drop_duplicates(inplace=True)


        #CREACION DE DF AUTORIZADOS
        df_per_auth = df_per[(df_per['ACEPTADO_RECHAZADO'] == 'ACEPTADO')]
        #limpieza de columnas innecesarias
        col_elem = ["RUN","DV","TRASLADO_POSITIVO","TRASLADO_NEGATIVO","EXBLOQUEADO","RECHAZADO_PREVISIONAL","RECHAZADO_FALLECIDO","AUTORIZADO","ACEPTADO_RECHAZADO","MOTIVO"]
        df_per_auth.drop(col_elem,axis=1,inplace=True) #Axis 1 indica que eliminare columnas

        #Creacion de DF Fallecidos
        df_per_fall = df_per[df_per['MOTIVO'] == 'RECHAZADO FALLECIDO']
        # Borrar ruts duplicados
        df_per_fall.drop_duplicates(subset='RUT', inplace=True)
        # Limpieza de columnas innecesarias
        col_df = ["RUT", "ANIO_CORTE", "MES_CORTE"]
        df_per_fall = df_per_fall[col_df]

    return df_per,df_per_auth,df_per_fall




@st.cache_resource
def load_logo(path):
    return Image.open(path)

def footer():
    with st.container():
        col1, col2, col3, col4 = st.columns([3,1,5,1])
        with col2:
            logo = load_logo(r"D:\DESARROLLO PROGRAMACION\data_health\logo_alain.png")
            st.image(logo, width=150)
        with col3:
            st.markdown("""
                <div style='text-align: left; color: #888888; font-size: 20px; padding-bottom: 20px;'>
                    💼 Aplicación desarrollada por <strong>Alain Antinao Sepúlveda</strong> <br>
                    📧 Contacto: <a href="mailto:alain.antinao.s@gmail.com" style="color: #4A90E2;">alain.antinao.s@gmail.com</a> <br>
                    🌐 Más información en: <a href="https://alain-antinao-s.notion.site/Alain-C-sar-Antinao-Sep-lveda-1d20a081d9a980ca9d43e283a278053e" target="_blank" style="color: #4A90E2;">Mi página personal</a>
                </div>
            """, unsafe_allow_html=True)