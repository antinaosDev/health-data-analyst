import streamlit as st
import pandas as pd
import chardet
from datetime import datetime
import numpy as np
import time
import io
import gc   # <--- IMPORTANTE: Recolector de basura para liberar RAM
import warnings

# --- CONFIGURACIÓN ---
# Silenciar advertencias de Pandas para limpiar la consola
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- IMPORTACIONES LOCALES ---
try:
    from class_ges import *
    from analisis_func import *
except ImportError:
    pass # Si no están, el código intentará seguir, pero algunas funciones de carga fallarán.

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

# --- 1. MEJORA: FUNCIÓN DE OPTIMIZACIÓN DE MEMORIA ROBUSTA ---
def optimizar_dataframe(df):
    """
    1. Rellena nulos con 'SIN DATOS' en columnas de texto (evita error de categorías).
    2. Convierte a 'category' para ahorrar RAM.
    """
    for col in df.columns:
        # Detectar columnas de tipo objeto (texto)
        if df[col].dtype == 'object':
            # PASO 1: Rellenar Nulos ANTES de convertir.
            df[col] = df[col].fillna('SIN DATOS')
            
            # Cálculo para decidir si vale la pena usar categorías
            num_unique_values = len(df[col].unique())
            num_total_values = len(df[col])
            
            if num_total_values > 0:
                if num_unique_values / num_total_values < 0.5:
                    # PASO 2: Convertir a categoría (ahora es seguro)
                    df[col] = df[col].astype('category')
                    
    return df

# --- 2. MEJORA: FUNCIÓN DE NORMALIZACIÓN PARA GRÁFICOS ---
def normalizar_datos_visualizacion(df):
    """
    Normaliza Géneros y crea la lógica correcta de NSP vs ASISTIÓ.
    """
    df_viz = df.copy()
    
    # A) NORMALIZACIÓN DE GÉNERO
    if 'GENERO' in df_viz.columns:
        df_viz['GENERO'] = df_viz['GENERO'].astype(str).str.upper().str.strip()
        mapa_genero = {
            'M': 'MASCULINO', 'HOMBRE': 'MASCULINO',
            'F': 'FEMENINO', 'MUJER': 'FEMENINO', 
            'D': 'OTRO', 'INDETERMINADO': 'OTRO', 'DESCONOCIDO': 'OTRO',
            'I': 'OTRO', 'INTERSEXUAL': 'OTRO', 'INTERSEX': 'OTRO',
            'SIN DATOS': 'OTRO', 'NAN': 'OTRO'
        }
        df_viz['GENERO'] = df_viz['GENERO'].replace(mapa_genero)
        # Aseguramos que cualquier cosa rara vaya a OTRO
        df_viz.loc[~df_viz['GENERO'].isin(['MASCULINO', 'FEMENINO']), 'GENERO'] = 'OTRO'

    # B) LÓGICA DE AUSENTISMO (NSP)
    if 'ESTADO ATENCION' in df_viz.columns:
        estado_col = df_viz['ESTADO ATENCION'].astype(str).str.upper().str.strip()
        
        # Palabras que indican que FALTÓ
        palabras_nsp = ['NO SE PRESENTO', 'NO SE ATENDIO', 'NSP', 'PACIENTE NO ASISTE', 'AUSENTE']
        # Palabras que indican que la hora NO EXISTE (anulada)
        palabras_excluir = ['ELIMINADO', 'ANULADO', 'BORRADO', 'SIN DATOS', 'VACIO']

        cond_nsp = estado_col.isin(palabras_nsp)
        cond_excluir = estado_col.isin(palabras_excluir)
        
        opciones = [
            (cond_nsp, 'NSP'),
            (cond_excluir, 'IGNORAR')
        ]
        
        # Si no es NSP ni IGNORAR, asumimos que ASISTIÓ
        df_viz['ESTADO_SIMPLIFICADO'] = np.select(
            [c for c, v in opciones], 
            [v for c, v in opciones], 
            default='ASISTIÓ'
        )
    else:
        df_viz['ESTADO_SIMPLIFICADO'] = 'IGNORAR'
    
    return df_viz

#-------------------ENCABEZADO ORIGINAL----------------------------------

st.info("""
        **Agenda Médica 🩺**
        
        En esta sección podrás gestionar la agenda médica consolidando los datos de diferentes periodos. Se realizará un procesamiento exhaustivo para limpiar, estandarizar y enriquecer la información,
        incluyendo el cálculo de edad, clasificación etaria y análisis estadístico relevante para la caracterización de atenciones.""")

# ------------------ INICIALIZAR VARIABLES DE SESSION -------------------
if 'lista_dfs' not in st.session_state:
    st.session_state.lista_dfs = []

# Inicializar df_agenda si no existe
if 'df_agenda' not in st.session_state:
    st.session_state.df_agenda = pd.DataFrame()

col4, col5 = st.columns([3, 4])
with col4:
    st.image("https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExem1sNWpxaGh2dmN1djR0endibDQyZTFpMGJxOXVtamIxd3FpMTdnMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/S8TzUKzRPjepzJx37U/giphy.gif", use_container_width=True)
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
        
        # 1. Limpiar memoria antes de empezar
        st.session_state.lista_dfs = [] 
        gc.collect()

        for i, archivo in enumerate(archivos):
            try:
                # Procesar CSV
                df = proc_csv(archivo)
                
                # 2. OPTIMIZAR AL INSTANTE (Función corregida)
                df = optimizar_dataframe(df)
                
                st.session_state.lista_dfs.append(df)
            except Exception as e:
                st.error(f"Error en archivo {i+1}: {e}")

            my_bar.progress((i + 1) / total, text=f"{i + 1} de {total} archivos procesados")
            
            # 3. Limpiar residuos en cada vuelta
            gc.collect() 

        my_bar.empty()
        st.success("Todos los archivos han sido procesados ✅")


# ------------------ PROCESAMIENTO Y UNIÓN -------------------
if st.session_state.lista_dfs:

    try:
        # Generar consolidado
        df_con = procesamiento_agenda(st.session_state.lista_dfs)
        
        # 4. CRÍTICO: Vaciar la lista pesada INMEDIATAMENTE después de unir
        st.session_state.lista_dfs = [] 
        gc.collect()

        # --- 3. MEJORA: ELIMINAR DUPLICADOS ---
        filas_antes = len(df_con)
        df_con = df_con.drop_duplicates()
        filas_borradas = filas_antes - len(df_con)
        if filas_borradas > 0:
            st.toast(f"Se eliminaron {filas_borradas} registros duplicados.", icon="♻️")
        # --------------------------------------

        df_con = normaliza_direcc(df_con)
        
        # Columnas a eliminar para ahorrar espacio
        cols_to_drop = [
            "RUT PROFESIONAL", "ESPECIALIDAD", "SUBESPECIALIDAD", "ESTABLECIMIENTO", 
            "HORA GENERADA", "ESTADO HORA", "HORA ASIGNADA", "HORA EJECUTADA", 
            "FECHA ULT MOD", "HORA UTL MOD",
            "TIPO_DIAGNOSTICO 1", "TIPO DIAGNOSTICO 2", "TIPO DIAGNOSTICO 3",
            "DIAGNOSTICO 1", "DIAGNOSTICO 2", "DIAGNOSTICO 3"
        ]
        
        df_con_clean = df_con.drop(cols_to_drop, axis=1, errors='ignore')

        # 5. Optimizar el DataFrame final antes de guardarlo en session_state
        df_con_clean = optimizar_dataframe(df_con_clean)
        
        # Limpiar variables intermedias
        del df_con
        gc.collect()

        #Capturo mi dataframe en un sesion state
        st.session_state.df_agenda = df_con_clean

    except Exception as e:
        st.error(f"Error uniendo archivos: {e}")
        st.session_state.lista_dfs = [] # Limpiar si falla
        gc.collect()

# --- VISUALIZACIÓN ---
if not st.session_state.df_agenda.empty:
    
    # --- 4. APLICAMOS LA NORMALIZACIÓN DE DATOS AQUÍ ---
    # Usamos una variable local 'df_con_clean' que ahora tiene NSP y Género arreglado
    df_raw = st.session_state.df_agenda
    df_con_clean = normalizar_datos_visualizacion(df_raw)
    # ---------------------------------------------------

    tab1,tab2 = st.tabs(['Información del documento ℹ️','Análisis de datos 📈'])

    with tab1:
        st.subheader("Sobre el archivo generado 📄")

        #Se agrupa la info de el aechivo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Celdas totales',f"{df_con_clean.size:,.0f}",border=True)
        with col2:
            st.metric('N° de filas',f"{df_con_clean.shape[0]:,.0f}",border=True)
        with col3:
            st.metric('N° de columnas',f"{df_con_clean.shape[1]:,.0f}",border=True)
        

        #Se muestra el df
        st.markdown('#### Vista Previa de la tabla:')
        
        # Manejo seguro de la columna ANIO_ASIG_HR
        if 'ANIO_ASIG_HR' in df_con_clean.columns:
            # Aseguramos que sea numérico para ordenar, ignorando nulos
            años_raw = pd.to_numeric(df_con_clean['ANIO_ASIG_HR'], errors='coerce').dropna().unique()
            años = sorted(años_raw.astype(int).tolist())
        else:
            años = []
            
        export_to_csv_gen(df_con_clean,'Agenda_médica',años)
        st.dataframe(df_con_clean.iloc[:40, :], hide_index=True)
    
    with tab2:
        st.subheader("Análisis estadístico de su archivo 📊")
        
        # Recalcular años para el filtro si no existen
        if 'ANIO_ASIG_HR' in df_con_clean.columns:
            años_raw = pd.to_numeric(df_con_clean['ANIO_ASIG_HR'], errors='coerce').dropna().unique()
            años = sorted(años_raw.astype(int).tolist())
        else:
            años = [2024]

        # Meses ordenados cronológicamente
        orden_meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        if 'MES_ASIG_HR' in df_con_clean.columns:
            meses_disp = df_con_clean['MES_ASIG_HR'].dropna().unique().tolist()
            meses = sorted([m for m in meses_disp if m in orden_meses], key=lambda x: orden_meses.index(x))
        else:
            meses = ["Enero"] # Fallback

        #Obtención de categoria genero
        gen_ops = df_con_clean['GENERO'].dropna().unique().tolist()
        gen_ops.append('TODOS')
        
        #Obtención de categoria clase etaria
        et_ops = df_con_clean['CLAS_ETARIA'].dropna().unique().tolist()
        et_ops.append('TODOS')

    
        #Contendor de filtros
        with st.container(border=True):
            filt1,filt2,filt3,filt4 = st.columns(4)
            with filt1:
                #filtro años
                if len(años) >= 2:
                    ops_year = st.select_slider(
                        'Seleccione un rango anual 📆',
                        options=años,
                        value=(min(años), max(años))
                    )
                elif len(años) == 1:
                    ops_year = (años[0], años[0])
                    st.info(f'Año: {años[0]}')
                else:
                    ops_year = (2024, 2024)

            with filt2:
                #filtro mes
                if len(meses) >= 2:
                    ops_month = st.select_slider('Seleccione un rango mensual 📆',options=meses,value=(meses[0],meses[-1]),key='month_per')
                elif len(meses) == 1:
                    ops_month = (meses[0], meses[0])
                else:
                    ops_month = ("Enero", "Enero")

            with filt3:
                #filtro genero
                idx_gen = len(gen_ops)-1 if gen_ops else 0
                ops_gen = st.selectbox('Seleccione el género 📝',gen_ops,index=idx_gen)
            with filt4:
                #filtro clase etaria
                idx_et = len(et_ops)-1 if et_ops else 0
                ops_et = st.selectbox('Seleccione el grupo etario 👥',et_ops,index=idx_et)
        
        mult1,mult2 = st.columns(2)
        with mult1:
            mult_select = st.multiselect('Seleccione un policlínico', df_con_clean['POLICLINICO'].unique().tolist(),key='poli')
        with mult2:
            mult_estam = st.multiselect('Seleccione el estamento',df_con_clean['AGRUPACION'].unique().tolist(),key='agrup')

        #Selectcciones de sector,estado,etnia
        et,sect = st.columns(2)
        with et:
            df_con_ops = df_con_clean['ETNIA PERCEPCION'].unique().tolist()
            if 'SIN DATOS' in df_con_ops: df_con_ops.remove('SIN DATOS')
            df_con_ops.append('TODOS')

            # --- MEJORA: USAR LA COLUMNA DE ESTADO SIMPLIFICADO PARA FILTRO ---
            # Filtramos 'IGNORAR' (anulados) de la lista de opciones
            df_con_est = [x for x in df_con_clean['ESTADO_SIMPLIFICADO'].unique().tolist() if x != 'IGNORAR']
            df_con_est.append('TODOS')
            
            sel_est = st.selectbox('Seleccione estado (Simplificado)', df_con_est, key='sel_est', index=len(df_con_est)-1)
            sel_et = st.selectbox('Seleccione la etnia',df_con_ops,key='sel_et',index=len(df_con_ops)-1)
            
        with sect:
            df_con_sect = df_con_clean['SECTOR'].unique().tolist()
            if 'NO_ESPECIFICADO' in df_con_sect: df_con_sect.remove('NO_ESPECIFICADO')
            df_con_sect.append('TODOS')
            sel_sec = st.selectbox('Seleccione sector',df_con_sect,key='sel_sect',index=len(df_con_sect)-1)

            df_con_com = df_con_clean['COMUNIDAD'].unique().tolist()
            if 'NO_ESPECIFICADO' in df_con_com: df_con_com.remove('NO_ESPECIFICADO')
            df_con_com.append('TODOS')
            sel_com = st.selectbox('Seleccione comunidad',df_con_com,key='sel_com',index=len(df_con_com)-1)
        



        st.divider()
        # Meses filtrados
        if meses:
            idx_inicio = orden_meses.index(ops_month[0])
            idx_fin = orden_meses.index(ops_month[1])
            meses_filtrados = orden_meses[idx_inicio:idx_fin + 1]
        else:
            meses_filtrados = []

        # Base de condición
        cond_base = (
            (df_con_clean['ANIO_ASIG_HR'] >= ops_year[0]) &
            (df_con_clean['ANIO_ASIG_HR'] <= ops_year[1]) &
            (df_con_clean['MES_ASIG_HR'].isin(meses_filtrados))
        )

        # Agregar condición por policlínico si hay selección
        if mult_select:
            cond_base = cond_base & (df_con_clean['POLICLINICO'].isin(mult_select))

        # Agregar condición por estamento si hay selección
        if mult_estam:
            cond_base = cond_base & (df_con_clean['AGRUPACION'].isin(mult_estam))

        # Agregar condición para etnia si no es "TODOS"
        if sel_et != 'TODOS':
            cond_base = cond_base & (df_con_clean['ETNIA PERCEPCION'] == sel_et)

        # Agregar condición para sector si no es "TODOS"
        if sel_sec != 'TODOS':
            cond_base = cond_base & (df_con_clean['PROCEDENCIA'] == sel_sec)
        
        # Agregar condición para comiunidad si no es "TODOS"
        if sel_com != 'TODOS':
            cond_base = cond_base & (df_con_clean['COMUNIDAD'] == sel_com)

        # --- MEJORA: CONDICIÓN ESTADO USANDO ESTADO_SIMPLIFICADO ---
        if sel_est != 'TODOS':
            cond_base = cond_base & (df_con_clean['ESTADO_SIMPLIFICADO'] == sel_est)

        # Filtros combinados para género y clase etaria (igual que antes)
        if ops_gen == 'TODOS' and ops_et != 'TODOS':
            cond_final = cond_base & (df_con_clean['CLAS_ETARIA'] == ops_et)
        elif ops_gen != 'TODOS' and ops_et == 'TODOS':
            cond_final = cond_base & (df_con_clean['GENERO'] == ops_gen)
        elif ops_gen == 'TODOS' and ops_et == 'TODOS':
            cond_final = cond_base
        else:
            cond_final = cond_base & (df_con_clean['GENERO'] == ops_gen) & (df_con_clean['CLAS_ETARIA'] == ops_et)

        # Aplicar filtro final
        df_filtered = df_con_clean[cond_final]

        if not df_filtered.empty:

            #Se agrupa la info de el aechivo
            col1, col2, col3,col4 = st.columns(4)
            cant_muj_rut = df_filtered[df_filtered['GENERO'] == 'FEMENINO']['RUT'].nunique()
            cant_hom_rut = df_filtered[df_filtered['GENERO'] == 'MASCULINO']['RUT'].nunique()
            total_gen = cant_muj_rut + cant_hom_rut
            total_cholchol = len(df_filtered[df_filtered['COMUNA'] == 'CHOL CHOL'])
            total_general = len(df_filtered['RUT'].tolist())
            
            #Verificacion total genero para evitar division por cero
            total_corr = total_gen if total_gen > 0 else 1
            total_corr_gen = total_general if total_general > 0 else 1

            with col1:
                st.metric('Total Atenciones Globales',f"{len(df_filtered['RUT'].tolist()):,.0f}",delta=f'{(1 - (total_cholchol/total_corr_gen))*100:,.1f}%',border=True)
            with col2:
                st.metric('Total Usuarios de Cholchol',f'{total_cholchol:,.0f}',border=True)
            with col3:
                st.metric('Total Mujeres',f"{cant_muj_rut:,.0f}",delta=f'{(cant_muj_rut/total_corr)*100:,.1f}%',border=True)
            with col4:
                st.metric('Total Hombres',f"{cant_hom_rut:,.0f}",delta=f'{(cant_hom_rut/total_corr)*100:,.1f}%',border=True)



            #Distribución de graficos
            graf1,graf2,graf3 = st.columns(3)

            with graf1:
                df_rut = df_filtered.groupby(['RANGO_ETARIO','GENERO'])['RUT'].nunique().reset_index()
                df_rut = df_rut[df_rut['RANGO_ETARIO'] != 'SIN DATOS']
                # MEJORA VISUAL: Colores consistentes
                fig = px.funnel(df_rut, x = 'RUT', y = 'RANGO_ETARIO', color = 'GENERO',
                                title='Atenciones por Rango etario',labels={'RUT':'Total Atenciones','RANGO_ETARIO':'Distribución de edades'},
                                color_discrete_map={'MASCULINO': '#636EFA', 'FEMENINO': '#EF553B', 'OTRO': '#00CC96'})
                st.plotly_chart(fig, use_container_width=True)
            
            with graf2:
                df_rut = (
                    df_filtered.groupby('POLICLINICO')['RUT']
                    .count()
                    .reset_index(name='TOTAL_RUT')
                    .sort_values(by='TOTAL_RUT', ascending=False)
                    .head(5)  # Solo los 5 mayores
                )

                fig = px.bar(df_rut, x='TOTAL_RUT', y='POLICLINICO', orientation='h',title='Top 5 Policlinícos con más n° de atenciones',text_auto=True,labels={'TOTAL_RUT':'Usuarios Atendidos','POLICLINICO':'Policlínico'})
                st.plotly_chart(fig, use_container_width=True)

            with graf3:
                df_rut = (
                    df_filtered.groupby('RANGO_SALARIAL')['RUT']
                    .nunique()
                    .reset_index()
                )
                #Quitamos las opciones que son 'SIN DATOS'
                df_rut = df_rut[df_rut['RANGO_SALARIAL'] != 'SIN DATOS']

                fig = px.pie(
                    df_rut,
                    values='RUT',
                    names='RANGO_SALARIAL',
                    hole=0.5,
                )

                fig.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.3,  # Más abajo para evitar solapamiento
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(t=10, b=40),  # Ajusta márgenes
                    height=390  # Reduce altura del gráfico
                )

                st.plotly_chart(fig, use_container_width=True)

            
            #Distribución de graficos
            graf4,graf5 = st.columns(2)

            with graf4:
                df_rut = (
                    df_filtered.groupby('POLICLINICO')['DIAS_ATENCION']
                    .mean()
                    .reset_index()
                    .rename(columns={'DIAS_ATENCION': 'TOT_D'})
                    .sort_values(by='TOT_D', ascending=False)
                    .head(7)
                )

                # Redondear TOT_D a enteros para mostrar etiquetas sin decimales
                df_rut['TOT_D_int'] = df_rut['TOT_D'].round(0).astype(int)

                fig = px.bar(
                    df_rut,
                    x='POLICLINICO',
                    y='TOT_D',
                    text='TOT_D_int',  # Mostrar la versión entera en la etiqueta
                    title='Top 7 policlínicos según el promedio de sus dias de atención',
                    labels={'POLICLINICO': 'Policlínico', 'TOT_D': 'Días de la atención (prom)'}
                )
                st.plotly_chart(fig, use_container_width=True)

            with graf5:
                # Ordenar cronológicamente si es posible
                df_rut = (
                    df_filtered.groupby(["FECHA ASIGNADA",'GENERO'])['RUT'].count().reset_index()
                )
                # Intentamos convertir fecha para ordenar
                try:
                    df_rut['FECHA ASIGNADA'] = pd.to_datetime(df_rut['FECHA ASIGNADA'], dayfirst=True)
                    df_rut = df_rut.sort_values('FECHA ASIGNADA')
                except:
                    pass

                fig = px.histogram(df_rut,x='FECHA ASIGNADA',y='RUT',color='GENERO',
                                   title='Distribución del n° de atenciónes por periodo',labels={'FECHA ASIGNADA':'Periodo','RUT':'Total atenciones'},
                                   color_discrete_map={'MASCULINO': '#636EFA', 'FEMENINO': '#EF553B', 'OTRO': '#00CC96'})
                st.plotly_chart(fig,use_container_width=True)
            

            # --- MEJORA: TABLA SIN ERROR DE MATPLOTLIB ---
            df_etnia = (
                df_filtered.groupby(['ETNIA PERCEPCION', 'POLICLINICO'])['RUT']
                .nunique()
                .reset_index().sort_values(by='RUT',ascending=True)
            )

            if not df_etnia.empty:
                tabla_etnia = df_etnia.pivot(
                    index='ETNIA PERCEPCION',
                    columns='POLICLINICO',
                    values='RUT'
                ).fillna(0).astype(int)

                tabla_etnia = tabla_etnia.reset_index()
                
                # Convertir a string explícitamente para evitar error de ordenamiento
                if 'ETNIA PERCEPCION' in tabla_etnia.columns:
                    tabla_etnia['ETNIA PERCEPCION'] = tabla_etnia['ETNIA PERCEPCION'].astype(str)

                tabla_etnia = tabla_etnia[tabla_etnia['ETNIA PERCEPCION'] != 'SIN DATOS']
                
                st.markdown("#### Atenciones de acuerdo a la etnia del usuario" )
                # Se eliminó el .style.background_gradient para evitar el error
                st.dataframe(tabla_etnia, hide_index=True, use_container_width=True)


            graf6,graf7,graf8 = st.columns(3)
            with graf6:
                df_ges = df_filtered.groupby('ES_GES')['RUT'].nunique().reset_index()
                fig = px.pie(df_ges,values='RUT',names='ES_GES',title='% de Casos GES')
                st.plotly_chart(fig,use_container_width=True)

            with graf7:
                #Comunas que mas se atienden
                df_com = (
                    df_filtered.groupby('COMUNA')['RUT'].nunique().reset_index().sort_values(by='RUT',ascending=False).head(5)
                )
                fig = px.bar(df_com,x='RUT',y='COMUNA',text_auto=True,orientation='h',labels={'RUT':'Total Usuarios'},title='Top 5 Comunas que más se atendieron')
                st.plotly_chart(fig,use_container_width=True)
            
            with graf8:
                #Escolaridad
                df_esc = df_filtered.groupby(['ESCOLARIDAD','GENERO'])['RUT'].nunique().reset_index()
                df_esc = df_esc[df_esc['ESCOLARIDAD'] != 'SIN DATOS']
                fig = px.funnel(df_esc,x='ESCOLARIDAD',y='RUT',color='GENERO',title='Distribución según nivel de escolaridad',
                                color_discrete_map={'MASCULINO': '#636EFA', 'FEMENINO': '#EF553B', 'OTRO': '#00CC96'})
                st.plotly_chart(fig,use_container_width=True)

            # --- MEJORA: GRÁFICOS DE AUSENTISMO CON LÓGICA CORRECTA ---
            graf9,graf10 = st.columns([3,5])

            with graf9:
                # Porcentaje de ausentismo (NSP vs ASISTIÓ)
                # Filtramos solo lo válido (quitamos anulados)
                df_aus = df_filtered[df_filtered['ESTADO_SIMPLIFICADO'].isin(['NSP', 'ASISTIÓ'])]
                df_aus_agg = df_aus.groupby('ESTADO_SIMPLIFICADO')['RUT'].count().reset_index()

                fig = px.pie(df_aus_agg, values='RUT', names='ESTADO_SIMPLIFICADO', hole=0.5,
                             title='% de ausentismo Real (NSP)',
                             color='ESTADO_SIMPLIFICADO',
                             color_discrete_map={'NSP': '#FF4136', 'ASISTIÓ': '#2ECC40'})
                st.plotly_chart(fig,use_container_width=True)
            
            with graf10:
                # Periodos de ausentismo (Usando el ESTADO_SIMPLIFICADO == NSP)
                df_aus_time = df_filtered[df_filtered['ESTADO_SIMPLIFICADO'] == 'NSP']
                
                if not df_aus_time.empty:
                    df_aus_time_agg = df_aus_time.groupby(['FECHA ASIGNADA','GENERO'])['RUT'].count().reset_index()
                    
                    try:
                        df_aus_time_agg['FECHA ASIGNADA'] = pd.to_datetime(df_aus_time_agg['FECHA ASIGNADA'], dayfirst=True)
                        df_aus_time_agg = df_aus_time_agg.sort_values('FECHA ASIGNADA')
                    except:
                        pass

                    fig = px.bar(df_aus_time_agg, x='FECHA ASIGNADA', y='RUT', color='GENERO',
                                 title='Distribución temporal de las ausencias',
                                 labels = {'FECHA ASIGNADA':'Periodo de ejecución','RUT':'Ausentismos'},
                                 color_discrete_map={'MASCULINO': '#636EFA', 'FEMENINO': '#EF553B', 'OTRO': '#00CC96'})
                    st.plotly_chart(fig,use_container_width=True)
                else:
                    st.success("No hay NSP registrados.")
        
        else:
            st.warning("No hay datos para los filtros seleccionados.")

#PIE DE PAGINA
try:
    footer()
except:
    pass