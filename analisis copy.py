import streamlit as st
import pandas as pd
import chardet
from datetime import datetime
import numpy as np

st.title('Cargar múltiples archivos CSV (para análisis)')

archivos = st.file_uploader('Selecciona los archivos CSV', type='csv', accept_multiple_files=True)

# Aquí almacenaremos los dataframes
lista_dfs = []

if archivos:
    for archivo in archivos:
        st.subheader(f"Archivo: {archivo.name}")
        try:
            # Detectar codificación
            rawdata = archivo.read(10000)
            result = chardet.detect(rawdata)
            encoding = result['encoding'] or 'latin1'
            archivo.seek(0)  # volver al inicio

            # Leer archivo robustamente
            df = pd.read_csv(
                archivo,
                encoding=encoding,
                sep=None,              # autodetecta separador
                engine='python',
                on_bad_lines='skip'    # ignora filas mal formateadas
            )

            if 'RUT' in df.columns:
                df['RUT'] = df['RUT'].astype(str).str.strip() #Se limpia la cadena
            
            lista_dfs.append(df)
            st.success(f"Leído correctamente: {df.shape[0]} filas, {df.shape[1]} columnas")

            

        except Exception as e:
            st.error(f"No se pudo leer archivo {archivo.name}: {e}")

# Ejemplo: trabajar con los dataframes cargados

if lista_dfs:
    # Concatenar los DataFrames
    df_concat = pd.concat(lista_dfs, ignore_index=True)

    st.header("Dataframe concatenado")
    
    cols_work = [
        "RUT", "GENERO", "COMUNA", "PROCEDENCIA", "PAIS DE PROCEDENCIA", "ETNIA PERCEPCION", "ESCOLARIDAD",
        "SITUACION CALLE","ES DISCAPACITADA","ES SENAME","ES EMBARAZADA","RUT PROFESIONAL",
        "PREVISION", "FECHA NACIMIENTO", "ESPECIALIDAD", "SUBESPECIALIDAD", "POLICLINICO", "AGRUPACION", 
        "ESTABLECIMIENTO", "HORA GENERADA", "ESTADO HORA", "ESTADO ATENCION", "ACCION A TOMAR", 
        "FECHA ASIGNADA", "HORA ASIGNADA", "FECHA EJECUTADA", "HORA EJECUTADA", "FECHA ULT MOD", "HORA UTL MOD"
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
        "EDAD:0 A 9",
        "EDAD:10 A 19",
        "EDAD:20 A 29",
        "EDAD:30 A 39",
        "EDAD:40 A 49",
        "EDAD:50 A 59",
        "EDAD:60 A 69",
        "EDAD:70 A 79",
        "EDAD:80 A 89",
        "EDAD:90 O MAS"
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
        "Ingreso imponible mensual <= $440.000",
        "Ingreso imponible mensual > $440.000 y <= $642.400",
        "Ingreso imponible mensual > $642.400"
    ]

    df_concat["RANGO_SALARIAL"] = np.select(condiciones_3, valores_3, default="SIN DATOS")

    #---------------------SE CREA COLUMNA DE MES Y AÑO PARA IDENTIFICAR CADA PLANILLA-----------------------------------
    df_concat["FECHA ASIGNADA"] = pd.to_datetime(df_concat["FECHA ASIGNADA"],errors='coerce')

    #creacion columna mes
    df_concat['MES_ASIG_HR'] = df_concat["FECHA ASIGNADA"].dt.month_name(locale='es_ES')
    #creacion columna año
    df_concat['ANNO_ASIG_HR'] = df_concat["FECHA ASIGNADA"].dt.year.astype('Int64')

    #-----------------CREA COLUMNA DE MES Y AÑO PARA DETERMINAR LA EJECUCION DE LA HORA-------------------------------
    df_concat["FECHA EJECUTADA"] = pd.to_datetime(df_concat["FECHA EJECUTADA"],errors='coerce')

    #creacion columna mes
    df_concat['MES_EJEC_HR'] = df_concat["FECHA EJECUTADA"].dt.month_name(locale='es_ES')
    #creacion columna año
    df_concat['ANNO_EJEC_HR'] = df_concat["FECHA EJECUTADA"].dt.year.astype('Int64')

    #--------------Calculo de los dias entre asignacion de hora y atencion----------------------------------------
    # Calcular diferencia en días
    df_concat["DIAS_ATENCION"] = (df_concat["FECHA EJECUTADA"] - df_concat["FECHA ASIGNADA"]).dt.days.astype('Int64')

   
    # Reemplazar negativos por 0
    df_concat["DIAS_ATENCION"] = df_concat["DIAS_ATENCION"].clip(lower=0)


    #----------------------------------UNIR CON REPORTE PERCAPITA PARA DEFINIR LOS CENTROS----------------------------
    st.subheader('Cargar reporte percapita')
    archivo_excel = st.file_uploader('Selecciona el archivo xlsx', type='xlsx', accept_multiple_files=False)

    if archivo_excel is not None:
        # Reiniciar el puntero del archivo
        archivo_excel.seek(0)

        # Leer Excel sin codificación ni separadores (no se necesita para Excel)
        df_excel = pd.read_excel(archivo_excel)

        # Combinar por RUT solo con columnas necesarias
        df_comb = df_concat.merge(df_excel[["RUT", "NOMBRE_CENTRO"]], on="RUT", how="left")

        # Rellenar valores faltantes
        df_comb["NOMBRE_CENTRO"] = df_comb["NOMBRE_CENTRO"].fillna("S/R PERCAPITA")


        #---------------------Determinar la Ubicación de los centros---------------------------------------
        condicion_4 = [
            (df_comb["NOMBRE_CENTRO"] == "Posta De Salud Rural Huamaqui"),
            (df_comb["NOMBRE_CENTRO"] == "Posta De Salud Rural Huentelar"),
            (df_comb["NOMBRE_CENTRO"] == "Posta De Salud Rural Malalche"),
            (df_comb["NOMBRE_CENTRO"] == "Centro De Salud Familiar Chol Chol"),
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

        df_comb["LAT_CENTRO"] = np.select(condicion_4,valor_lat,"SIN DATOS")
        df_comb["LONG_CENTRO"] = np.select(condicion_4,valor_long,"SIN DATOS")

        import io
        # Convertir el DataFrame a CSV en memoria como bytes
        csv_buffer = io.BytesIO()
        csv_content = df_comb.to_csv(index=False).encode('utf-8')
        csv_buffer.write(csv_content)
        csv_buffer.seek(0)

        # Botón para descargar
        st.download_button(
            label="📥 Descargar CSV combinado",
            data=csv_buffer,
            file_name="DATA_REV.csv",
            mime="text/csv"
        )

        import streamlit as st
        import plotly.express as px
        import pandas as pd

        # ======================
        # Análisis y Visualización
        # ======================

        st.title("📊 Análisis de Datos de Atención de Salud")

        # Opcional: Limpiar valores nulos comunes
        df_comb['GENERO'] = df_comb['GENERO'].fillna('SIN DATO')
        df_comb['ESTADO ATENCION'] = df_comb['ESTADO ATENCION'].fillna('SIN DATO')
        df_comb['PREVISION'] = df_comb['PREVISION'].fillna('SIN DATO')
        df_comb['RANGO_SALARIAL'] = df_comb['RANGO_SALARIAL'].fillna('SIN DATO')
        df_comb['COMUNA'] = df_comb['COMUNA'].fillna('SIN DATO')
        df_comb['ESPECIALIDAD'] = df_comb['ESPECIALIDAD'].fillna('SIN DATO')

        # 1. Distribución por género
        fig_genero = px.histogram(df_comb, x="GENERO", title="Distribución por Género")

        # 2. Distribución Etaria por Género
        fig_edad = px.histogram(df_comb, x="EDAD", color="GENERO", nbins=10, title="Distribución Etaria por Género")

        # 3. Comuna vs cantidad de pacientes
        fig_comuna = px.histogram(df_comb, x="COMUNA", title="Pacientes por Comuna")

        # 4. Tiempo de atención por especialidad
        fig_tiempo_especialidad = px.box(df_comb, x="ESPECIALIDAD", y="DIAS_ATENCION", title="Tiempo de Espera por Especialidad")

        # 5. Estado de atención
        fig_estado = px.pie(df_comb, names="ESTADO ATENCION", title="Distribución Estado de Atención")

        # 6. Previsión de salud
        fig_prevision = px.pie(df_comb, names="PREVISION", title="Distribución por Previsión de Salud")

        # 7. Rango salarial
        fig_salarial = px.histogram(df_comb, x="RANGO_SALARIAL", title="Rango Salarial de los Pacientes")

        # Mostrar todos los gráficos
        st.subheader("Distribución por Género")
        st.plotly_chart(fig_genero)

        st.subheader("Distribución Etaria por Género")
        st.plotly_chart(fig_edad)

        st.subheader("Pacientes por Comuna")
        st.plotly_chart(fig_comuna)

        st.subheader("Tiempo de Espera por Especialidad")
        st.plotly_chart(fig_tiempo_especialidad)

        st.subheader("Estado de Atención")
        st.plotly_chart(fig_estado)

        st.subheader("Previsión de Salud")
        st.plotly_chart(fig_prevision)

        st.subheader("Rango Salarial de los Pacientes")
        st.plotly_chart(fig_salarial)
        