import streamlit as st
import pandas as pd
import chardet
from datetime import datetime
import numpy as np
import time
import io
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

# Importación de módulos propios
from class_ges import *
from analisis_func import *

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="Análisis Percápita", page_icon="📊")

# --- FUNCIÓN DE CARGA CON CACHÉ ---
@st.cache_data(show_spinner="Procesando y consolidando archivos...")
def cargar_datos_cache_v2(archivos_cargados):
    return reporte_percapita(archivos_cargados)

# --- FUNCIÓN AUXILIAR PARA CONVERTIR DF A CSV ---
@st.cache_data
def convert_df_to_csv(_df):
    return _df.to_csv(index=False, sep=';').encode('utf-8-sig') # utf-8-sig y sep=';' para que Excel abra bien las tildes y columnas

# --- ENCABEZADO ---
st.info(
    """
    **Análisis Percápita 📊**

    Esta sección permite cargar, consolidar y analizar el reporte per cápita, además de geolocalizar 
    los distintos centros de la comuna.
    """
)

col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeDl4a2pzZjUyaDVpdXYwZzBjdTNibjU5NDFkZmZhdHU2Ymo1djBqOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/nNOAPjUdo4mpZFkDf8/giphy.gif", use_container_width=True)
with col2:
    st.subheader('Cargar reporte percapita')
    archivos = st.file_uploader('Selecciona los archivos (CSV, TXT)', type=['csv', 'txt'], accept_multiple_files=True)

# --- LÓGICA PRINCIPAL ---
if archivos:
    try:
        df_global, df_auth, df_fall = cargar_datos_cache_v2(archivos)
    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
        st.stop()

    with st.expander("👁️ Ver vista previa de datos cargados"):
        st.markdown("#### Primeros 100 registros:")
        st.dataframe(df_global.head(100), hide_index=True, use_container_width=True)

    # Session State
    columnas_sesion = [
        "RUT", "NOMBRE_CENTRO", "NOMBRE_CENTRO_PROCEDENCIA", "NOMBRE_COMUNA_PROCEDENCIA",
        "NOMBRE_CENTRO_DESTINO", "NOMBRE_COMUNA_DESTINO", "ANIO_CORTE", "MES_CORTE", 
        "LAT_CENTRO", "LONG_CENTRO"
    ]
    cols_existentes = [c for c in columnas_sesion if c in df_auth.columns]
    st.session_state.df_autorizados = df_auth[cols_existentes]

    # --------------------- TABS -------------------------------------------------
    tab1, tab2, tab3 = st.tabs(['📈 Inscritos Percápita', '📉 Registro Fallecidos', '📊 Análisis de datos'])

    # Helper para años
    def obtener_anios_validos(df, col_anio):
        raw = df[col_anio].dropna()
        validos = raw[pd.to_numeric(raw, errors='coerce').notna()]
        anios = validos.astype(int).unique().tolist()
        return sorted(anios)

    año_export_insc = obtener_anios_validos(df_auth, 'ANIO_CORTE')
    año_export_fall = obtener_anios_validos(df_fall, 'ANIO_CORTE')

    # --- TAB 1: INSCRITOS (MODIFICADO) ---
    with tab1:
        with st.container(border=True):
            if año_export_insc:
                # 1. Selector de Rango de Años
                col_filt_1, col_filt_2 = st.columns(2)
                with col_filt_1:
                    if len(año_export_insc) >= 2:
                        opcion_año = st.select_slider(
                            '1. Seleccione rango de años 📆',
                            options=año_export_insc,
                            value=(min(año_export_insc), max(año_export_insc)),
                            key='slider_insc'
                        )
                    else:
                        st.info(f"Año único: {año_export_insc[0]}")
                        opcion_año = (año_export_insc[0], año_export_insc[0])
                
                # 2. Selector de Mes de Corte (NUEVO)
                with col_filt_2:
                    # Obtenemos los meses únicos disponibles en el dataframe
                    meses_disponibles = df_auth['MES_CORTE'].unique().tolist()
                    # Orden sugerido si es posible, sino por defecto
                    orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                    meses_ordenados = sorted([m for m in meses_disponibles if m in orden_meses], key=lambda x: orden_meses.index(x))
                    
                    # Si hay meses que no están en la lista estándar, los agregamos al final
                    otros_meses = [m for m in meses_disponibles if m not in orden_meses]
                    meses_finales = meses_ordenados + otros_meses
                    
                    mes_corte_seleccionado = st.selectbox(
                        "2. Seleccione Mes de Corte para el gráfico y exportación 🗓️",
                        options=meses_finales,
                        index=len(meses_finales)-1 if meses_finales else 0, # Por defecto el último mes (suele ser el más reciente)
                        help="Selecciona un mes único para evitar sumar duplicados de distintos meses en el mismo año."
                    )

                anio_inicio, anio_fin = opcion_año
                
                if not df_auth.empty and mes_corte_seleccionado:
                    # Filtrar por Años Y por Mes de Corte
                    df_filtrado = df_auth[
                        (df_auth['ANIO_CORTE'] >= anio_inicio) & 
                        (df_auth['ANIO_CORTE'] <= anio_fin) &
                        (df_auth['MES_CORTE'] == mes_corte_seleccionado) # Filtro clave
                    ]
                    
                    if not df_filtrado.empty:
                        # Gráfico
                        df_grouped = df_filtrado.groupby('ANIO_CORTE')['RUT'].count().reset_index()
                        df_grouped.columns = ['Año', 'Inscritos']
                        
                        st.markdown(f"### Evolución de Inscritos - Corte: {mes_corte_seleccionado}")
                        fig = px.bar(df_grouped, x='Año', y='Inscritos', text_auto=True, color='Año')
                        st.plotly_chart(fig, use_container_width=True)

                        st.divider()
                        st.markdown("#### Configuración de Exportación 📥")
                        
                        # 3. Selector de Columnas (NUEVO)
                        all_columns = df_filtrado.columns.tolist()
                        col_exp_1, col_exp_2 = st.columns([3, 1])
                        
                        with col_exp_1:
                            columnas_seleccionadas = st.multiselect(
                                "Seleccione las columnas a incluir en el CSV:",
                                options=all_columns,
                                default=all_columns, # Por defecto todas
                                key="cols_insc"
                            )
                        
                        with col_exp_2:
                            if columnas_seleccionadas:
                                # Preparamos el DF final para exportar
                                df_exportar = df_filtrado[columnas_seleccionadas]
                                csv_data = convert_df_to_csv(df_exportar)
                                
                                st.download_button(
                                    label="📥 Descargar CSV",
                                    data=csv_data,
                                    file_name=f'Inscritos_Percapita_{mes_corte_seleccionado}_{anio_inicio}-{anio_fin}.csv',
                                    mime='text/csv',
                                    use_container_width=True
                                )
                            else:
                                st.warning("Selecciona al menos una columna.")
                    else:
                        st.warning(f"No hay datos para el mes de {mes_corte_seleccionado} en el rango de años seleccionado.")
            else:
                st.warning("No se encontraron años válidos en los datos de inscritos.")

    # --- TAB 2: FALLECIDOS (Mantenemos lógica similar o estándar) ---
    with tab2:
        with st.container(border=True):
            if año_export_fall:
                if len(año_export_fall) >= 2:
                    opcion_año_fall = st.select_slider(
                        'Seleccione un rango de años 📆',
                        options=año_export_fall,
                        value=(min(año_export_fall), max(año_export_fall)),
                        key='slider_fall'
                    )
                else:
                    st.info(f"Año único: {año_export_fall[0]}")
                    opcion_año_fall = (año_export_fall[0], año_export_fall[0])
                anio_inicio_f, anio_fin_f = opcion_año_fall

                if not df_fall.empty:
                    # Aquí mantenemos la lógica estándar, pero podríamos aplicar lo mismo si lo deseas
                    df_filtrado_f = df_fall[
                        (df_fall['ANIO_CORTE'] >= anio_inicio_f) & (df_fall['ANIO_CORTE'] <= anio_fin_f)
                    ]
                    
                    df_grouped_f = df_filtrado_f.groupby('ANIO_CORTE')['RUT'].count().reset_index()
                    df_grouped_f.columns = ['Año', 'Fallecidos']

                    fig_f = px.bar(df_grouped_f, x='Año', y='Fallecidos', text_auto=True, color='Año', title=f"Fallecidos ({anio_inicio_f}-{anio_fin_f})")
                    st.plotly_chart(fig_f, use_container_width=True)

                    # Exportación básica (puedes actualizar esta también si quieres selector de columnas)
                    col_f1, col_f2 = st.columns([4, 1])
                    with col_f2:
                        csv_fall = convert_df_to_csv(df_filtrado_f)
                        st.download_button(
                            label="Descargar Nómina Fallecidos",
                            data=csv_fall,
                            file_name="Nomina_Fallecidos.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
            else:
                st.warning("No se encontraron años válidos en los datos de fallecidos.")

    # --- TAB 3: ANÁLISIS DETALLADO ---
    with tab3:
        st.subheader("Análisis estadístico detallado 📊")
        
        años_global = obtener_anios_validos(df_global, 'ANIO_CORTE')
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        meses_disp = df_global['MES_CORTE'].dropna().unique().tolist()
        meses_ordenados = sorted([m for m in meses_disp if m in orden_meses], key=lambda x: orden_meses.index(x))

        with st.container(border=True):
            c_filt1, c_filt2, c_filt3 = st.columns(3)
            with c_filt1:
                if len(años_global) >= 2:
                    año_slider = st.select_slider('Rango de años 📆', options=años_global, value=(min(años_global), max(años_global)), key='a_slider_an')
                elif años_global:
                    año_slider = (años_global[0], años_global[0])
                else:
                    año_slider = (2025, 2025)
            with c_filt2:
                if len(meses_ordenados) >= 2:
                    meses_slider = st.select_slider('Rango de meses 📆', options=meses_ordenados, value=(meses_ordenados[0], meses_ordenados[-1]), key='m_slider_an')
                elif meses_ordenados:
                    meses_slider = (meses_ordenados[0], meses_ordenados[0])
                else:
                    meses_slider = ("Enero", "Enero")
            with c_filt3:
                opciones_gender = list(df_global['GENERO'].unique()) + ['TODOS']
                select_gender = st.selectbox('Género:', opciones_gender, index=len(opciones_gender)-1)

            opciones_estab = sorted(df_global['NOMBRE_CENTRO'].astype(str).unique().tolist())
            select_estab = st.multiselect('Establecimientos (Dejar vacío para todos):', opciones_estab)

        idx_inicio = orden_meses.index(meses_slider[0])
        idx_fin = orden_meses.index(meses_slider[1])
        meses_filtrados = orden_meses[idx_inicio:idx_fin + 1]

        mask = (
            (df_global['ANIO_CORTE'] >= año_slider[0]) &
            (df_global['ANIO_CORTE'] <= año_slider[1]) &
            (df_global['MES_CORTE'].isin(meses_filtrados))
        )
        if select_gender != 'TODOS': mask &= (df_global['GENERO'] == select_gender)
        if select_estab: mask &= (df_global['NOMBRE_CENTRO'].isin(select_estab))

        df_filtered = df_global[mask]

        if not df_filtered.empty:
            # Gráficos (Código resumido para brevedad, igual al anterior)
            g1, g2, g3 = st.columns(3)
            with g1: st.plotly_chart(px.funnel(df_filtered.groupby(['RANGO_ETARIO', 'GENERO'])['RUT'].nunique().reset_index(), x='RUT', y='RANGO_ETARIO', color='GENERO', title='Clasificación Etaria'), use_container_width=True)
            with g2: 
                fig = px.bar(df_filtered.groupby(['TRAMO', 'GENERO'])['RUT'].nunique().reset_index(), x='TRAMO', y='RUT', text_auto=True, color='GENERO', barmode='group', title='Usuarios por Tramo')
                fig.update_yaxes(visible=False)
                st.plotly_chart(fig, use_container_width=True)
            with g3: 
                fig = px.bar(df_filtered.groupby(['NOMBRE_CENTRO', 'GENERO'])['RUT'].nunique().reset_index(), x='NOMBRE_CENTRO', y='RUT', text_auto=True, color='GENERO', barmode='group', title='Usuarios por Centro')
                fig.update_yaxes(visible=False)
                st.plotly_chart(fig, use_container_width=True)

            g4, g5, g6 = st.columns(3)
            with g4: st.plotly_chart(px.bar(pd.DataFrame({'Tipo': ['Traslado +', 'Traslado -'], 'Cantidad': [df_filtered[df_filtered['TRASLADO_POSITIVO'] == 'X']['RUT'].nunique(), df_filtered[df_filtered['TRASLADO_NEGATIVO'] == 'X']['RUT'].nunique()]}), x='Tipo', y='Cantidad', text='Cantidad', title='Balance Traslados', color='Tipo'), use_container_width=True)
            with g5: st.plotly_chart(px.bar(pd.DataFrame({'Tipo': ['Nuevo', 'Aceptado'], 'Cantidad': [df_filtered[df_filtered['NUEVO_INSCRITO'] == 'X']['RUT'].nunique(), df_filtered[df_filtered['ACEPTADO_RECHAZADO'] == 'ACEPTADO']['RUT'].nunique()]}), x='Tipo', y='Cantidad', text='Cantidad', title='Nuevos vs Aceptados', color='Tipo'), use_container_width=True)
            with g6: st.plotly_chart(px.bar(df_filtered.groupby('MOTIVO')['RUT'].nunique().reset_index().sort_values('RUT'), x='RUT', y='MOTIVO', text_auto=True, orientation='h', title='Motivos'), use_container_width=True)

            # Mapa
            with st.container(border=True):
                st.subheader("Distribución Geográfica 🗺️")
                # Limpieza de coords
                def clean_coord(val):
                    try: return float(pd.Series(str(val).replace(',', '.')).str.extract(r'(-?\d+\.\d+)')[0].iloc[0])
                    except: return np.nan
                
                df_map = df_filtered.groupby(['NOMBRE_CENTRO', 'LAT_CENTRO', 'LONG_CENTRO'])['RUT'].nunique().reset_index()
                df_map.columns = ['NOMBRE_CENTRO', 'LAT_CENTRO', 'LONG_CENTRO', 'COUNT_RUT']
                df_map['LAT_CENTRO'] = df_map['LAT_CENTRO'].apply(clean_coord)
                df_map['LONG_CENTRO'] = df_map['LONG_CENTRO'].apply(clean_coord)
                df_map = df_map.dropna(subset=['LAT_CENTRO', 'LONG_CENTRO'])
                df_map = df_map[df_map['COUNT_RUT'] > 0]

                if not df_map.empty:
                    try:
                        if df_map['COUNT_RUT'].nunique() == 1:
                            fig_map = px.scatter_map(df_map, lat='LAT_CENTRO', lon='LONG_CENTRO', color='NOMBRE_CENTRO', zoom=10, map_style='open-street-map', hover_name='NOMBRE_CENTRO', title="Distribución por Centro")
                            fig_map.update_traces(marker=dict(size=15))
                        else:
                            fig_map = px.scatter_map(df_map, lat='LAT_CENTRO', lon='LONG_CENTRO', size='COUNT_RUT', color='NOMBRE_CENTRO', zoom=10, map_style='open-street-map', hover_name='NOMBRE_CENTRO', title="Distribución por Centro")
                        st.plotly_chart(fig_map, use_container_width=True)
                    except Exception as e: st.error(f"Error mapa: {e}")
                else: st.warning("Sin datos geográficos válidos.")
        else:
            st.warning("No hay datos para los filtros seleccionados.")

try: footer()
except: pass