import streamlit as st
import pandas as pd
import chardet
from datetime import datetime
import numpy as np
import time
import io
from class_ges import *
from analisis_func import *
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

#config pagina
st.set_page_config(layout="wide")

#-------------------ENCABEZADO----------------------------------
st.info(
        """
        **Análisis Percápita 📊**

        Esta sección permite cargar, consolidar y analizar el reporte per cápita además de geolocalizar los distintos centros de la comuna,
        para la identificación por usuario facilitando un seguimiento detallado y una mejor planificación de recursos.
        """
    )


col1,col2 = st.columns([2,5])
with col1:
    st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeDl4a2pzZjUyaDVpdXYwZzBjdTNibjU5NDFkZmZhdHU2Ymo1djBqOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/nNOAPjUdo4mpZFkDf8/giphy.gif")
with col2:
    st.subheader('Cargar reporte percapita')
    archivos = st.file_uploader('Selecciona los archivos', type=['csv','txt'], accept_multiple_files=True)


if archivos:
    df_global, df_auth, df_fall = reporte_percapita(archivos)
    st.markdown("#### Vista previa tabla:")
    st.dataframe(df_global,hide_index=True)

    #Capturo mi dataframe en un sesion state
    columnas_sesion = [
        "RUT","NOMBRE_CENTRO","NOMBRE_CENTRO_PROCEDENCIA","NOMBRE_COMUNA_PROCEDENCIA","NOMBRE_CENTRO_DESTINO","NOMBRE_COMUNA_DESTINO"
        ,"ANIO_CORTE","MES_CORTE","LAT_CENTRO","LONG_CENTRO"

    ]
    st.session_state.df_autorizados = df_auth[columnas_sesion]
    

    #---------------------Se divide en Tabs para mejor visualización-------------------------------------------------
    tab1,tab2,tab3 = st.tabs(['📈Inscritos Percápita','📉Registro Fallecidos','📊Análisis de datos'],width='stretch')

    #Definición de perido de extraccion de datos
    año_export_insc = df_auth['ANIO_CORTE'].astype(int).unique().tolist()
    año_export_insc.sort()#Se ordenan los valores

    año_export_fall = df_fall['ANIO_CORTE'].unique().astype(int).tolist()
    año_export_fall.sort()#Se ordenan los valores

    with tab1:
        #Se define un container para mejor visualización
        with st.container(border=True):
            opcion_año =st.select_slider('Seleccione un rango de años 📆',options= año_export_insc,value=(min(año_export_insc),max(año_export_insc)),key='opcion1')
            anio_inicio, anio_fin = opcion_año
            if not df_auth.empty:
                # Filtrar DataFrame por año
                df_filtrado = df_auth[
                    (df_auth['ANIO_CORTE'] >= anio_inicio) &
                    (df_auth['ANIO_CORTE'] <= anio_fin)
                ]
                # Agrupar datos
                df_grouped = df_filtrado.groupby('ANIO_CORTE')['RUT'].count().reset_index()
                df_grouped.columns = ['Año', 'Inscritos']

                #Lista meses
                lista_meses_insc = df_filtrado['MES_CORTE'].unique().tolist()
                    
                fig = px.bar(df_grouped,x='Año',y='Inscritos',text_auto=True,color='Año')
                st.plotly_chart(fig,use_container_width=True)

                with st.container():
                    col1,col2,col3,col4 = st.columns([4,4,4,4])
                    with col2:
                        export_to_csv(df_auth,'Inscritos_percapita',list(set(list(opcion_año))),opcion_año)
                    with col3:
                        export_to_excel(df_auth,'Inscritos_percapita',list(set(list(opcion_año))),list(set(lista_meses_insc)),opcion_año)
    with tab2:
        with st.container(border=True):
            opcion_año =st.select_slider('Seleccione un rango de años 📆',options= año_export_fall,value=(min(año_export_fall),max(año_export_fall)),key='opcion2')
            anio_inicio, anio_fin = opcion_año
            if not df_fall.empty:
                # Filtrar DataFrame por año
                df_filtrado = df_fall[
                    (df_fall['ANIO_CORTE'] >= anio_inicio) &
                    (df_fall['ANIO_CORTE'] <= anio_fin)
                ]
                lista_meses_fall = df_filtrado['MES_CORTE'].unique().tolist()

                # Agrupar datos
                df_grouped = df_filtrado.groupby('ANIO_CORTE')['RUT'].count().reset_index()
                df_grouped.columns = ['Año', 'Fallecidos']

                fig = px.bar(df_grouped,x='Año',y='Fallecidos',text_auto=True,color='Año')
                st.plotly_chart(fig,use_container_width=True)
                with st.container():
                    col1,col2,col3,col4 = st.columns([4,4,4,4])
                    with col2:
                        export_to_csv(df_fall,'Nomina_Fallecidos',list(set(list(opcion_año))),opcion_año)
                    with col3:
                        export_to_excel(df_fall,'Nomina_Fallecidos',list(set(list(opcion_año))),list(set(lista_meses_fall)),opcion_año)
                    

    with tab3:
        st.subheader("Análisis estadístico de su archivo 📊")
        # Usar el DataFrame global (índice 0 de la tupla)

        # Años ordenados cronológicamente
        años = df_global['ANIO_CORTE'].dropna().unique().tolist()
        años = sorted(años)

        # Meses ordenados cronológicamente
        orden_meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        meses = df_global['MES_CORTE'].dropna().unique().tolist()
        meses = sorted([m for m in meses if m in orden_meses], key=lambda x: orden_meses.index(x))

        #OPCIONES
        with st.container(border=True):
            col1,col2,col3 = st.columns(3)
            with col1:
                if len(años) >= 2:
                    año_slider = st.select_slider('Seleccione el rango de años 📆',años,value=(min(años),max(años)))
                else:
                    # Usa el año disponible dos veces, o el actual si está vacío
                    año_unico = años[0] if años else años[1]
                    año_slider = (año_unico, año_unico)
                    st.info(f'Año evaluado 📆: {año_unico}')
            with col2:
                if len(meses) >= 2:
                    meses_slider = st.select_slider('Seleccione un rango de meses 📆',meses,value=(meses[0],meses[len(meses)-1]))
                else:
                    mes_unico = meses[0] if meses else meses[1]
                    meses_slider = (mes_unico,mes_unico)
                    st.info(f'Mes evaluado 📆: {mes_unico}')
            with col3:
                opciones_gender = df_global['GENERO'].unique().tolist()
                opciones_gender.append('TODOS')
                select_gender = st.selectbox('Seleccione el género:',opciones_gender,index=len(opciones_gender)-1)
            
            opciones_estab = df_global['NOMBRE_CENTRO'].unique().tolist()
            select_estab = st.multiselect('Seleccione el establecimiento:',opciones_estab)
        

        # Meses filtrados
        idx_inicio = orden_meses.index(meses_slider[0])
        idx_fin = orden_meses.index(meses_slider[1])
        meses_filtrados = orden_meses[idx_inicio:idx_fin + 1]
        # --- Máscara base ---
        mask = (
            (df_global['ANIO_CORTE'] >= año_slider[0]) &
            (df_global['ANIO_CORTE'] <= año_slider[1]) &
            (df_global['MES_CORTE'].isin(meses_filtrados)) 
        )

        # --- Filtros adicionales ---
        if select_gender != 'TODOS':
            mask &= (df_global['GENERO'] == select_gender)
        if select_estab:
            mask &= (df_global['NOMBRE_CENTRO'].isin(select_estab))

        # --- DataFrame filtrado ---
        df_filtered = df_global[mask]

        # --- Gráfico de embudo por rango etario ---
        graf1, graf2, graf3 = st.columns(3)
        with graf1:
            df_et = df_filtered.groupby(['RANGO_ETARIO','GENERO'])['RUT'].nunique().reset_index()
            fig = px.funnel(df_et, x='RUT', y='RANGO_ETARIO',color='GENERO',
                            title='Clasificación etaria',labels={'RUT':'Total usuarios','RANGO_ETARIO':'Rango etario'})
            st.plotly_chart(fig, use_container_width=True)
        with graf2:
            df_tramo = df_filtered.groupby(['TRAMO','GENERO'])['RUT'].nunique().reset_index()
            fig = px.bar(
                df_tramo,
                x='TRAMO',
                y='RUT',
                text_auto=True,
                labels={'TRAMO': 'Tramo', 'RUT': 'Total usuarios'},
                title='Usuarios por tramo',
                color='GENERO',
                barmode='group'#Para que no queden apiladas
            )

            # Ocultar eje Y
            fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, title=None)

            st.plotly_chart(fig, use_container_width=True)
        with graf3:
            df_estab = df_filtered.groupby(['NOMBRE_CENTRO','GENERO'])['RUT'].nunique().reset_index()
            fig = px.bar(
                df_estab,
                x='NOMBRE_CENTRO',
                y='RUT',
                text_auto=True,
                labels={'NOMBRE_CENTRO': 'Centro de Salud', 'RUT': 'Total usuarios'},
                title='Usuarios por Centro de Salud',
                color='GENERO',
                barmode='group',#Para que no queden apiladas,
              
            )

            # Ocultar eje Y
            fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, title=None)
            st.plotly_chart(fig, use_container_width=True)
        
        graf4,graf5,graf6 = st.columns(3)
        with graf4:
            # Filtrar positivos con 'X'
            df_pos = df_filtered[df_filtered['TRASLADO_POSITIVO'] == 'X']
            count_pos = df_pos['RUT'].count()

            # Filtrar negativos con 'X'
            df_neg = df_filtered[df_filtered['TRASLADO_NEGATIVO'] == 'X']
            count_neg = df_neg['RUT'].count()

            # Crear DataFrame para comparar
            df_comp = pd.DataFrame({
                'Tipo': ['Traslado +', 'Traslado -'],
                'Cantidad': [count_pos, count_neg]
            })

            # Gráfico de barras usando plotly express
            fig = px.bar(
                df_comp,
                x='Tipo',
                y='Cantidad',
                text='Cantidad',
                title='Traslado + vs Traslado -',
                labels={'Cantidad': 'Total Usuarios', 'Tipo': 'Tipo de Traslado'}
                )
            fig.update_traces(textposition='outside')

            st.plotly_chart(fig, use_container_width=True)
        with graf5:
            #Grafico de pie
            df_insc = df_filtered[df_filtered['NUEVO_INSCRITO'] == 'X']
            count_ing = df_insc['RUT'].count()

            df_acept = df_filtered[df_filtered['ACEPTADO_RECHAZADO'] == 'ACEPTADO']
            count_acept = df_acept['RUT'].count()

            #dataframe comparativo
            df_comp2 = pd.DataFrame({
                'Tipo':['Nuevo','Aceptado'],
                'Cantidad':[count_ing,count_acept]
            })

            # Gráfico de barras usando plotly express
            fig = px.bar(
                df_comp2,
                x='Tipo',
                y='Cantidad',
                text='Cantidad',
                title='Nuevo ingreso vs aceptado',
                labels={'Cantidad': 'Total Usuarios', 'Tipo': 'Ingresos'}
                )
            fig.update_traces(textposition='outside')

            st.plotly_chart(fig, use_container_width=True)
        with graf6:
            df_mot = df_filtered.groupby('MOTIVO')['RUT'].nunique().reset_index()
            fig = px.bar(df_mot,x='RUT',y='MOTIVO',text_auto=True,orientation='h',labels={'RUT':'Total Usuarios','MOTIVO':'Motivo'})
            st.plotly_chart(fig, use_container_width=True)

        
        with st.container(border=True):
            df_map = df_filtered.groupby(['NOMBRE_CENTRO', 'LAT_CENTRO', 'LONG_CENTRO'])['RUT'].nunique().reset_index()

            # Limpiamos las columnas LAT_CENTRO y LONG_CENTRO para extraer solo el primer número válido y convertir a float
            df_map['LAT_CENTRO'] = df_map['LAT_CENTRO'].astype(str).str.extract(r'(-?\d+\.\d+)')[0].astype(float)
            df_map['LONG_CENTRO'] = df_map['LONG_CENTRO'].astype(str).str.extract(r'(-?\d+\.\d+)')[0].astype(float)

            # Creamos el gráfico
            fig = px.scatter_mapbox(
                df_map,
                lat='LAT_CENTRO',
                lon='LONG_CENTRO',
                size='RUT',
                color='NOMBRE_CENTRO',
                zoom=10,
                mapbox_style='open-street-map',
            )

            # Mostrar figura en Streamlit
            st.plotly_chart(fig)
            

#PIE DE PAGINA        
footer()

                