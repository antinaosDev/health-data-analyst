import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime
import io
import time
import gc

from analisis_func import *

# Configuración de página
st.set_page_config(layout="wide")


col1, col2, col3 = st.columns(3)

# Botón Tabla agenda Médica
with col1:
    st.markdown("##### Tabla agenda médica 🖱️")
    if "df_agenda" in st.session_state and st.session_state.df_agenda is not None:
        st.info("Información disponible ✔️")
    else:
        st.warning("Primero debe cargar información en Análisis agenda Médica")

# Botón Inscritos Percápita
with col2:
    st.markdown("##### Inscritos percápita 📊")
    if "df_autorizados" in st.session_state and st.session_state.df_autorizados is not None:
        st.info("Información disponible ✔️")
    else:
        st.warning("Primero debe cargar información en Análisis Percápita")

# Botón Clasificación GES
with col3:
    st.markdown("##### Clasificación GES 🩺")
    if "df_ges" in st.session_state and st.session_state.df_ges is not None:
        st.info("Información disponible ✔️")
    else:
        st.warning("Primero debe cargar información en Preclasificador GES")


lista_opciones = []
if "df_agenda" in st.session_state and "df_autorizados" in st.session_state and "df_ges" in st.session_state:
    lista_opciones.append((st.session_state.df_agenda,'Tabla agenda'))
    lista_opciones.append((st.session_state.df_autorizados,'Tabla percápita'))
    lista_opciones.append((st.session_state.df_ges,'Tabla ges'))
elif "df_agenda" in st.session_state and "df_autorizados" in st.session_state:
    lista_opciones.append((st.session_state.df_agenda,'Tabla agenda'))
    lista_opciones.append((st.session_state.df_autorizados,'Tabla percápita'))
elif "df_agenda" in st.session_state and "df_ges" in st.session_state:
    lista_opciones.append((st.session_state.df_agenda,'Tabla agenda'))
    lista_opciones.append((st.session_state.df_ges,'Tabla ges'))
elif "df_autorizados" in st.session_state and "df_ges" in st.session_state:
    lista_opciones.append((st.session_state.df_autorizados,'Tabla percápita'))
    lista_opciones.append((st.session_state.df_ges,'Tabla ges'))

lista_nombres = [i[1] for i in lista_opciones]


if lista_nombres:
    tablas_select = []
    opciones_nom = st.multiselect('Seleccione una tabla',lista_nombres)
    for i in lista_opciones:
       if i[1] in opciones_nom:
           tablas_select.append(i[0])
    
    if opciones_nom:
        base = opciones_nom[0]
        otras = opciones_nom[1:]

        if otras:
            texto_otras = " 🖇️ ".join(otras)
            st.info(
                f"📊 **Tabla base:** {base}\n\n"
                f"Se combinará con: {texto_otras}"
            )
        else:
            st.info(
                f"📊 **Tabla base:** {base}\n\n"
                "No hay otras tablas seleccionadas para combinar."
            )
        col1,col2,col3 = st.columns(3)
        @st.cache_data(ttl=600)
        def df_merge(tabla,cols):
            df_comb = tabla[0].merge(tabla[1][cols + ['RUT']],on = 'RUT',how='left')
            return df_comb
        
        with col2: 
            btn_comb = st.button('🖇️Combinar Tablas',use_container_width=True) 
            if btn_comb: 
                if len(tablas_select) == 2: 
                    #Evitamos que se copien columnas repetidas
                    cols1 = tablas_select[0].columns.tolist() 
                    cols2 = [col for col in tablas_select[1].columns.tolist() 
                             if col not in cols1] 
                    df_comb = pd.merge(tablas_select[0][cols1],tablas_select[1][cols2 + ['RUT']],on = 'RUT',how='left')
                    df_comb['NOMBRE_CENTRO'] = df_comb['NOMBRE_CENTRO'].fillna('Sin registro Percápita') 
                    df_comb.drop_duplicates(inplace=True)
                    export_to_csv_gen(df_comb,'df_comb','2025') 
                    st.markdown('##### Vista Previa Tabla combinada') 
                    st.dataframe(df_comb.head(50)) 
                elif len(tablas_select) > 2: #Evitamos que se copien columnas repetidas 
                    cols1 = tablas_select[0].columns.tolist() 
                    cols2 = [col for col in tablas_select[1].columns.tolist() if col not in cols1]
                    df_comb = pd.merge(tablas_select[0][cols1],tablas_select[1][cols2 + ['RUT']],on = 'RUT',how='left')
                    df_comb.drop_duplicates(inplace=True) 
                    #Evitamos columnas repetidas 
                    cols3 = df_comb.columns.tolist() 
                    cols4 = [col for col in tablas_select[2].columns.tolist() if col not in cols3]
                    df_comb_def = pd.merge(df_comb[cols3],tablas_select[2][cols4 + ['RUT']],on = 'RUT',how='left') 
                    df_comb_def['NOMBRE_CENTRO'] = df_comb_def['NOMBRE_CENTRO'].fillna('Sin registro Percápita') 
                    df_comb_def.drop_duplicates(inplace=True)
                    export_to_csv_gen(df_comb_def,'df_comb','2025') 
                    st.markdown('##### Vista Previa Tabla combinada') 
                    st.dataframe(df_comb.head(50))


           
    else:
        st.warning("⚠️ No se han seleccionado tablas para la unión.")


else:
    st.warning('Seleccione al menos dos tablas para combinar')



#PIE DE PAGINA        
footer()
