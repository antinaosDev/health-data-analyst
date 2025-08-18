

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

#-------------------ENCABEZADO----------------------------------

st.info("""
        **Agenda Médica 🩺**
        
        En esta sección podrás gestionar la agenda médica consolidando los datos de diferentes periodos. Se realizará un procesamiento exhaustivo para limpiar, estandarizar y enriquecer la información,
        incluyendo el cálculo de edad, clasificación etaria y análisis estadístico relevante para la caracterización de atenciones.""")

# ------------------ INICIALIZAR VARIABLES DE SESSION -------------------
if 'lista_dfs' not in st.session_state:
    st.session_state.lista_dfs = []

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

    df_con = procesamiento_agenda(st.session_state.lista_dfs)
    df_con_clean = df_con.drop([
    "SITUACION CALLE", "ES DISCAPACITADA", "ES SENAME", "ES EMBARAZADA", "RUT PROFESIONAL",
    "ESPECIALIDAD", "SUBESPECIALIDAD", "ESTABLECIMIENTO", "HORA GENERADA", "ESTADO HORA", 
    "HORA ASIGNADA", "HORA EJECUTADA", "FECHA ULT MOD", "HORA UTL MOD",
    "TIPO_DIAGNOSTICO 1", "TIPO DIAGNOSTICO 2", "TIPO DIAGNOSTICO 3",
    "DIAGNOSTICO 1", "DIAGNOSTICO 2", "DIAGNOSTICO 3"
    ], axis=1, errors='ignore')

    #Capturo mi dataframe en un sesion state
    st.session_state.df_agenda = df_con_clean

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
        años = df_con_clean['ANIO_ASIG_HR'].dropna().unique().tolist()
        años = sorted(años)
        export_to_csv_gen(df_con_clean,'Agenda_médica',años)
        st.dataframe(df_con_clean.iloc[:40, 2:-6],hide_index=True)
    
    with tab2:
        st.subheader("Análisis estadístico de su archivo 📊")
        #Años ordenados cronológicamente
        años = df_con['ANIO_ASIG_HR'].dropna().unique().tolist()
        años = sorted(años)
        # Meses ordenados cronológicamente
        orden_meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        meses = df_con['MES_ASIG_HR'].dropna().unique().tolist()
        meses = sorted([m for m in meses if m in orden_meses], key=lambda x: orden_meses.index(x))
        #Obtención de categoria genero
        gen_ops = df_con['GENERO'].dropna().unique().tolist()
        gen_ops.append('TODOS')
        #Obtención de categoria clase etaria
        et_ops = df_con['CLAS_ETARIA'].dropna().unique().tolist()
        et_ops.append('TODOS')
        et_ops.remove('SIN DATOS')

    
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
                else:
                    # Usa el año disponible dos veces, o el actual si está vacío
                    año_unico = años[0] if años else años[1]
                    ops_year = (año_unico, año_unico)
                    st.info(f'Año evaluado 📆: {año_unico}')
            with filt2:
                #filtro mes
                ops_month = st.select_slider('Seleccione un rango mensual 📆',options=meses,value=(meses[0],meses[len(meses)-1]),key='month_per')
            with filt3:
                #filtro genero
                ops_gen = st.selectbox('Seleccione el género 📝',gen_ops,index=len(gen_ops)-1)
            with filt4:
                #filtro clase etaria
                ops_et = st.selectbox('Seleccione el grupo etario 👥',et_ops,index=len(et_ops)-1)
        
        mult1,mult2 = st.columns(2)
        with mult1:
            mult_select = st.multiselect('Seleccione un policlínico', df_con['POLICLINICO'].unique().tolist(),key='poli')
        with mult2:
            mult_estam = st.multiselect('Seleccione el estamento',df_con['AGRUPACION'].unique().tolist(),key='agrup')

        #Selectcciones de sector,estado,etnia
        et,sect,est = st.columns(3)
        with et:
            df_con_ops = df_con['ETNIA PERCEPCION'].unique().tolist()
            df_con_ops.append('TODOS')
            df_con_ops.remove('SIN DATOS')
            sel_et = st.selectbox('Seleccione la etnia',df_con_ops,key='sel_et',index=len(df_con_ops)-1)
        with sect:
            df_con_sect = df_con['PROCEDENCIA'].unique().tolist()
            df_con_sect.append('TODOS')
            sel_sec = st.selectbox('Seleccione sector',df_con_sect,key='sel_sect',index=len(df_con_sect)-1)
        with est:
            df_con_est = df_con['ACCION A TOMAR'].unique().tolist()
            df_con_est.append('TODOS')
            df_con_est.remove('SIN DATOS')
            sel_est = st.selectbox('Seleccione estado',df_con_est,key='sel_est',index=len(df_con_est)-1)

        st.divider()
        # Meses filtrados
        idx_inicio = orden_meses.index(ops_month[0])
        idx_fin = orden_meses.index(ops_month[1])
        meses_filtrados = orden_meses[idx_inicio:idx_fin + 1]

        # Base de condición
        cond_base = (
            (df_con['ANIO_ASIG_HR'] >= ops_year[0]) &
            (df_con['ANIO_ASIG_HR'] <= ops_year[1]) &
            (df_con['MES_ASIG_HR'].isin(meses_filtrados))
        )

        # Agregar condición por policlínico si hay selección
        if mult_select:
            cond_base = cond_base & (df_con['POLICLINICO'].isin(mult_select))

        # Agregar condición por estamento si hay selección
        if mult_estam:
            cond_base = cond_base & (df_con['AGRUPACION'].isin(mult_estam))

        # Agregar condición para etnia si no es "TODOS"
        if sel_et != 'TODOS':
            cond_base = cond_base & (df_con['ETNIA PERCEPCION'] == sel_et)

        # Agregar condición para sector si no es "TODOS"
        if sel_sec != 'TODOS':
            cond_base = cond_base & (df_con['PROCEDENCIA'] == sel_sec)

        # Agregar condición para estado si no es "TODOS"
        if sel_est != 'TODOS':
            cond_base = cond_base & (df_con['ACCION A TOMAR'] == sel_est)

        # Filtros combinados para género y clase etaria (igual que antes)
        if ops_gen == 'TODOS' and ops_et != 'TODOS':
            cond_final = cond_base & (df_con['CLAS_ETARIA'] == ops_et)
        elif ops_gen != 'TODOS' and ops_et == 'TODOS':
            cond_final = cond_base & (df_con['GENERO'] == ops_gen)
        elif ops_gen == 'TODOS' and ops_et == 'TODOS':
            cond_final = cond_base
        else:
            cond_final = cond_base & (df_con['GENERO'] == ops_gen) & (df_con['CLAS_ETARIA'] == ops_et)

        # Aplicar filtro final
        df_filtered = df_con[cond_final]

        

        #Se agrupa la info de el aechivo
        col1, col2, col3,col4 = st.columns(4)
        cant_muj_rut = df_filtered[df_filtered['GENERO'] == 'FEMENINO']['RUT'].nunique()
        cant_hom_rut = df_filtered[df_filtered['GENERO'] == 'MASCULINO']['RUT'].nunique()
        total_gen = cant_muj_rut + cant_hom_rut
        total_cholchol = len(df_filtered[df_filtered['COMUNA'] == 'CHOL CHOL'])
        total_general = len(df_filtered['RUT'].tolist())
        #Verificacion total genero
        if total_gen <= 0:
            total_corr =1
        else:
            total_corr = total_gen
        #Verificacion toatal atenciones
        if total_general <= 0:
            total_corr_gen = 1
        else:
            total_corr_gen = total_general
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
            fig = px.funnel(df_rut, x = 'RUT', y = 'RANGO_ETARIO', color = 'GENERO',title='Atenciones por Rango etario',labels={'RUT':'Total Atenciones','RANGO_ETARIO':'Distribución de edades'})
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
            df_rut = (
                df_filtered.groupby(["FECHA ASIGNADA",'GENERO'])['RUT'].count().reset_index()
            )
            fig = px.histogram(df_rut,x='FECHA ASIGNADA',y='RUT',color='GENERO',
                               title='Distribución del n° de atenciónes por periodo',labels={'FECHA ASIGNADA':'Periodo','RUT':'Total atenciones'})
            st.plotly_chart(fig,use_container_width=True)
        

        #Data Frame para evaluacion de atención por policlinico y por etnia
        df_etnia = (
            df_filtered.groupby(['ETNIA PERCEPCION', 'POLICLINICO'])['RUT']
            .nunique()
            .reset_index().sort_values(by='RUT',ascending=True)
        )

        # Convertir a tabla dinámica
        tabla_etnia = df_etnia.pivot(
            index='ETNIA PERCEPCION',
            columns='POLICLINICO',
            values='RUT'
        ).fillna(0).astype(int)

        # Si quieres que el índice vuelva a ser columna
        tabla_etnia = tabla_etnia.reset_index()
        tabla_etnia = tabla_etnia[tabla_etnia['ETNIA PERCEPCION'] != 'SIN DATOS']
        # Aplicar estilo para resaltar los valores más altos por columna
        styled_table = tabla_etnia.style.highlight_max(axis=0, color='lightcoral')

        # Mostrar en Streamlit con estilos
        st.markdown("#### Atenciones de acuerdo a la etnia del usuario" )
        st.dataframe(styled_table,hide_index=True)


        graf6,graf7,graf8 = st.columns(3)
        with graf6:
            df_ges = df_filtered.groupby('GES')['RUT'].nunique().reset_index()
            fig = px.pie(df_ges,values='RUT',names='GES',title='% de Casos GES')
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
            fig = px.funnel(df_esc,x='ESCOLARIDAD',y='RUT',color='GENERO',title='Distribución según nivel de escolaridad')
            st.plotly_chart(fig,use_container_width=True)

        graf9,graf10 = st.columns([3,5])

        with graf9:
            #Porcentaje de ausentismo
            df_aus = df_filtered.groupby('ESTADO ATENCION')['RUT'].count().reset_index()
            df_aus = df_aus[df_aus['ESTADO ATENCION'] != 'SIN DATOS']

            fig = px.pie(df_aus,values='RUT',names='ESTADO ATENCION',hole=0.5,title='% de ausentismo en las atenciones')
            st.plotly_chart(fig,use_container_width=True)
        
        with graf10:
            #Peridos de ausentismo
            df_aus = df_filtered.groupby(['ESTADO ATENCION','FECHA EJECUTADA','GENERO'])['RUT'].count().reset_index()
            df_aus = df_aus[(df_aus['ESTADO ATENCION'] != 'SIN DATOS') & (df_aus['ESTADO ATENCION'] == 'NO SE PRESENTO') & (df_aus['FECHA EJECUTADA'] != 'SIN DATOS')]

            fig = px.histogram(df_aus,x='FECHA EJECUTADA',y='RUT',color='GENERO',title='Distribución temporal de las ausencias',
                               labels = {'FECHA EJECUTADA':'Periodo de ejecución','RUT':'Ausentismos'})
            st.plotly_chart(fig,use_container_width=True)


#PIE DE PAGINA
footer()
            





