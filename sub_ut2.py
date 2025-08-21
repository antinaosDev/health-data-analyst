from analisis_func import load_logo, normaliza_direcc
from servidor_fb import ingresar_registro_bd, leer_registro
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

st.title("🌍Consulta de Sector y Distrito")

st.info(
    """
    ℹ️ **Información importante**

    Los datos disponibles provienen de información **previamente trabajada**, por lo cual es posible que **no se encuentren todos los registros**.  
    En caso de que un RUT consultado no tenga información de *Sector*, *Distrito* o *Nombre*, significa que no existe en la base consolidada actual.
    """
)


# Leer datos desde la BD
data = leer_registro('consulta')  # Esto devuelve un dict con IDs de Firebase

# Convertir a DataFrame correctamente
if isinstance(data, dict):
    # Cada valor es un registro
    df = pd.DataFrame(list(data.values()))
else:
    df = pd.DataFrame()

if df.empty:
    st.warning("No se encontraron datos en la base de datos.")
else:

    # Input para ingresar un RUT
    # Extraer lista única de RUTs
    if "RUT" in df.columns:
        df = df[(df["DISTRITO"] != "NO_ESPECIFICADO") & (df["DISTRITO"] != "")]
        ruts = df["RUT"].dropna().unique().tolist()
    else:
        ruts = []

    ruts = ["Seleccione un RUT..."] + ruts
    # Input para elegir RUT
    rut_ingresado = st.selectbox("", ruts, index=0)

    if rut_ingresado and "RUT" in df.columns:
        registro = df[df["RUT"] == rut_ingresado]

        if not registro.empty:
            st.subheader(f"Información del RUT {rut_ingresado}")

            # Extraer valores seguros
            sector = registro["SECTOR"].values[0] if "SECTOR" in df.columns else "No disponible"
            distrito = registro["DISTRITO"].values[0] if "DISTRITO" in df.columns else "No disponible"
            lat = registro["LAT_SEC"].values[0] if "LAT_SEC" in df.columns else "No disponible"
            lon = registro["LON_SEC"].values[0] if "LON_SEC" in df.columns else "No disponible"

            col1, col2 = st.columns([5,4])

            # Mostrar imagen según el sector
            with col1:
                if sector.upper() == "SOL":
                    st.image(load_logo("sector sol.png"))
                elif sector.upper() == "LUNA":
                    st.image(load_logo("sector luna.png"))
                

            # Mostrar métricas
            with col2:
                st.metric("Distrito", distrito.upper())
            
                # Creamos el gráfico SOLO para el RUT encontrado
                if lat != "No disponible" and lon != "No disponible":
                    df_map = pd.DataFrame([{
                        "LAT_SEC": lat,
                        "LON_SEC": lon,
                        "SECTOR": sector,
                        "DISTRITO": distrito,
                        "RUT": rut_ingresado
                    }])

                    # 🔹 Convertir a float (necesario para Plotly)
                    df_map["LAT_SEC"] = pd.to_numeric(df_map["LAT_SEC"], errors="coerce")
                    df_map["LON_SEC"] = pd.to_numeric(df_map["LON_SEC"], errors="coerce")

                    fig = px.scatter_mapbox(
                        df_map,
                        lat="LAT_SEC",
                        lon="LON_SEC",
                        color="SECTOR",
                        size_max=15,
                        zoom=9,
                        mapbox_style="open-street-map",
                    )

                    fig.update_layout(
                        height=200,
                        width=100,  # <--- controla el ancho en píxeles
                        margin={"r":0,"t":0,"l":0,"b":0}
                    )

                    st.plotly_chart(fig)

                else:
                    st.warning("No hay coordenadas disponibles para este RUT")



        else:
            st.warning("No se encontró información para este RUT")
    elif rut_ingresado and "RUT" not in df.columns:
        st.error("No se encontró la columna 'RUT' en los datos")

st.divider()

st.subheader('Consulte el sector mediante la dirección del usuario')
st.warning(
    """
    **⚠️** Si el RUT ingresado no se encuentra en la base de datos, por favor ingrese la dirección correspondiente
    para poder determinar el posible **sector** al que pertenece.
    """
)

import pandas as pd
import streamlit as st
import plotly.express as px

# Función para simular load_logo
def load_logo(filename):
    return filename  # Reemplaza con tu código real para cargar imágenes

# Input de dirección
direccion = st.text_input("Por favor ingrese la dirección o sector")

if direccion:  # Solo ejecuta si hay algo escrito
    # Crear DataFrame temporal
    df_temp = pd.DataFrame({
        "DIRECCION": [direccion],
        "COMUNA": ["CHOL CHOL"]  # Para pasar el filtro dentro de la función
    })

    # Normalizar direcciones
    df_resultado = normaliza_direcc(df_temp)  # tu función existente

    # Guardar en session_state para que persista y se actualice dinámicamente
    st.session_state["df_resultado"] = df_resultado

# Recuperar el DataFrame de session_state
registro = st.session_state.get("df_resultado", pd.DataFrame())

# Mostrar información si existe
if not registro.empty:
    st.subheader(f"Información de la dirección ingresada")

    # Extraer valores seguros
    sector = registro["SECTOR"].values[0] if "SECTOR" in registro.columns else "No disponible"
    distrito = registro["DISTRITO"].values[0] if "DISTRITO" in registro.columns else "No disponible"
    lat = registro["LAT_SEC"].values[0] if "LAT_SEC" in registro.columns else "No disponible"
    lon = registro["LON_SEC"].values[0] if "LON_SEC" in registro.columns else "No disponible"

    col1, col2 = st.columns([5,4])

    # Mostrar imagen según el sector
    with col1:
        if sector.upper() == "SOL":
            st.image(load_logo("sector sol.png"))
        elif sector.upper() == "LUNA":
            st.image(load_logo("sector luna.png"))

    # Mostrar métricas y mapa
    with col2:
        st.metric("Distrito", distrito.upper())

        if lat != "No disponible" and lon != "No disponible":
            df_map = pd.DataFrame([{
                "LAT_SEC": lat,
                "LON_SEC": lon,
                "SECTOR": sector,
                "DISTRITO": distrito
            }])

            df_map["LAT_SEC"] = pd.to_numeric(df_map["LAT_SEC"], errors="coerce")
            df_map["LON_SEC"] = pd.to_numeric(df_map["LON_SEC"], errors="coerce")

            fig = px.scatter_mapbox(
                df_map,
                lat="LAT_SEC",
                lon="LON_SEC",
                color="SECTOR",
                size_max=15,
                zoom=9,
                mapbox_style="open-street-map",
            )

            fig.update_layout(
                height=200,
                width=100,
                margin={"r":0,"t":0,"l":0,"b":0}
            )

            # 🔹 Key único basado en dirección
            st.plotly_chart(fig, key=f"map_{direccion}")
