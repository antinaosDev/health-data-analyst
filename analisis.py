import streamlit as st
import pandas as pd
import chardet
from datetime import datetime
import numpy as np
import time
import io
from class_ges import *
from analisis_func import *


# ------------------ INICIALIZAR VARIABLES DE SESSION -------------------
if 'lista_dfs' not in st.session_state:
    st.session_state.lista_dfs = []

# ------------------ ENCABEZADO -------------------
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    st.image("D:/DESARROLLO PROGRAMACION/data_health/logo_data_s.png", width=90)
with col2:
    st.markdown("<h1 style='margin: 0; color: #0072B2;text-align: center ;'>Análisis de Datos Salud 🏥</h1>", unsafe_allow_html=True)
with col3:
    st.image("D:/DESARROLLO PROGRAMACION/data_health/logo_alain.png", width=120)

st.divider()



col4, col5 = st.columns([3, 4])
with col4:
    st.image("https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExem1sNWpxaGh2dmN1djR0endibDQyZTFpMGJxOXVtamIxd3FpMTdnMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/S8TzUKzRPjepzJx37U/giphy.gif", width=900)
with col5:
    st.subheader('💾Seleccione sus archivos .csv:')

    archivos = st.file_uploader("Subir archivos", type='csv', accept_multiple_files=True)

    with st.container():
        col1, col2, col3 = st.columns([2, 4, 2])
        with col2:
            btn_proc = st.button('Procesar archivos', icon='🖱️', use_container_width=True)

    if archivos and btn_proc:
        progress_text = "Procesando archivos..."
        my_bar = st.progress(0, text=progress_text)

        total = len(archivos)
        st.session_state.lista_dfs = []  # Reiniciar lista en cada procesamiento

        for i, archivo in enumerate(archivos):
            df = proc_csv(archivo)
            st.session_state.lista_dfs.append(df)

            my_bar.progress((i + 1) / total, text=f"{i + 1} de {total} archivos procesados")
            time.sleep(0.3)  # opcional

        my_bar.empty()
        st.success("Todos los archivos han sido procesados ✅")

# ------------------ PROCESAMIENTO Y UNIÓN CON REPORTE PERCÁPITA -------------------
if st.session_state.lista_dfs:
    df_concat = procesamiento_agenda(st.session_state.lista_dfs)

    st.subheader('📄 Cargar reporte percapita')
    archivo_excel = st.file_uploader('Selecciona el archivo xlsx', type='xlsx', accept_multiple_files=False)

    if archivo_excel is not None:
        archivo_excel.seek(0)
        df_excel = pd.read_excel(archivo_excel)

        if 'RUT' not in df_excel.columns or 'NOMBRE_CENTRO' not in df_excel.columns:
            st.error("El archivo Excel debe contener las columnas 'RUT' y 'NOMBRE_CENTRO'")
        else:
            df_comb = df_concat.merge(df_excel[["RUT", "NOMBRE_CENTRO"]], on="RUT", how="left")
            df_comb["NOMBRE_CENTRO"] = df_comb["NOMBRE_CENTRO"].fillna("S/R PERCAPITA")

            # ------------------ UBICACIONES MANUALES ------------------
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

            df_comb["LAT_CENTRO"] = np.select(condicion_4, valor_lat, default="SIN DATOS")
            df_comb["LONG_CENTRO"] = np.select(condicion_4, valor_long, default="SIN DATOS")

            # ------------------ DESCARGA ------------------
            csv_buffer = io.BytesIO()
            csv_content = df_comb.to_csv(index=False).encode('utf-8')
            csv_buffer.write(csv_content)
            csv_buffer.seek(0)

            st.download_button(
                label="📥 Descargar CSV combinado",
                data=csv_buffer,
                file_name="DATA_REV.csv",
                mime="text/csv"
            )
