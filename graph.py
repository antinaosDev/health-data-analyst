import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Mapa de Centros de Atención en Cholchol (Araucanía)")

# Cargar datos
df = pd.read_csv(r"C:\Users\alain\Downloads\DATA_REV (1).csv")

# Convertir latitud y longitud a numérico y eliminar filas con valores inválidos
df['LAT_CENTRO'] = pd.to_numeric(df['LAT_CENTRO'], errors='coerce')
df['LONG_CENTRO'] = pd.to_numeric(df['LONG_CENTRO'], errors='coerce')
df = df.dropna(subset=['LAT_CENTRO', 'LONG_CENTRO'])

# Agrupar por centro para contar RUT únicos
df_agg = df.groupby(['NOMBRE_CENTRO', 'LAT_CENTRO', 'LONG_CENTRO']).agg({
    'RUT': pd.Series.nunique
}).reset_index().rename(columns={'RUT': 'CANT_RUT_UNICOS'})

# Opcional: filtro para solo centros en Cholchol (si tienes una columna de comuna o similar)
# Por ejemplo: df_agg = df_agg[df_agg['COMUNA'] == 'Cholchol']

# Crear mapa con plotly express, centrado en Cholchol
fig = px.scatter_geo(
    df_agg,
    lat='LAT_CENTRO',
    lon='LONG_CENTRO',
    size='CANT_RUT_UNICOS',
    hover_name='NOMBRE_CENTRO',
    projection='natural earth',
    scope='south america',
    center={'lat': -38.667, 'lon': -72.533},  # Coordenadas aproximadas de Cholchol
    title='Centros en Cholchol con tamaño por cantidad de RUT únicos'
)

fig.update_geos(
    lataxis_range=[-39, -38],  # Ajusta según el zoom que quieras
    lonaxis_range=[-73, -72],
    projection_scale=20
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)
