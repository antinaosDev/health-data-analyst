from analisis_func import load_logo, normaliza_direcc
from servidor_fb import ingresar_registro_bd, leer_registro
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.title("🌍Consulta de Sector y Distrito")

# Crear dos columnas con proporciones: 1:2 (logo : info)
columna1, columna2 = st.columns(2)

with columna1:
    st.subheader("👩‍⚕️ Enfermería")

    components.html(
        """
        <div style="background-color:#f0f2f6; padding:15px; border-radius:10px;">
            <h4 style="margin:0; color:#2E86C1;">👩‍⚕️ Enfermería</h4>
            <ul style="margin-top:8px;">
                <li><b>Sector Sol (2 Distritos):</b> 3 Enfermeros/as</li>
                <li><b>Sector Luna (3 Distritos):</b> 2 Enfermeros/as</li>
            </ul>
            <h5 style="color:#2E86C1; margin-top:12px;">Prestaciones Sectorizadas:</h5>
            <ul>
                <li>Control de Salud Infantil: Seguimiento integral del desarrollo.</li>
                <li>Control de Salud Cardiovascular: Manejo y prevención de patologías.</li>
            </ul>
            <h5 style="color:#2E86C1; margin-top:12px;">Prestaciones Transversales:</h5>
            <ul>
                <li>EMPAM (Examen Médico Preventivo del Adulto Mayor)</li>
                <li>Curaciones</li>
                <li>Vacunatorio</li>
                <li>Procedimientos varios (inyecciones, toma de muestras, etc.)</li>
            </ul>
        </div>
        """,
        height=400,
        scrolling=True
    )

with columna2:
    st.subheader("🤰 Matronería")

    components.html(
        """
        <div style="background-color:#f0f2f6; padding:15px; border-radius:10px;">
            <h4 style="margin:0; color:#28B463;">🤰 Matronería</h4>
            <ul style="margin-top:8px;">
                <li><b>Sector Sol (2 Distritos):</b> 3 Matrones/as</li>
                <li><b>Sector Luna (3 Distritos):</b> 3 Matrones/as</li>
            </ul>
            <h5 style="color:#28B463; margin-top:12px;">Prestaciones Sectorizadas:</h5>
            <ul>
                <li>Consulta y Control de Matronería: Seguimiento periódico.</li>
                <li>Control de Embarazo e Ingreso: Acompañamiento desde el inicio.</li>
                <li>Control de Diada: Cuidado de la madre y el recién nacido.</li>
            </ul>
            <h5 style="color:#28B463; margin-top:12px;">Prestaciones Transversales:</h5>
            <ul>
                <li>Toma de PAP (Papanicolau)</li>
                <li>Ecografías</li>
                <li>Atención y urgencias gineco-obstétricas</li>
            </ul>
        </div>
        """,
        height=400,
        scrolling=True
    )

# Centrar el logo
tm1,tm2 = st.columns([3,4])
with tm1:
    st.image(load_logo("cartografia.png"))
with tm2:
    st.info(
        """
        ℹ️ **Información importante**

        Los datos disponibles provienen de información **previamente procesada**, por lo cual es posible que **no se encuentren todos los registros**.  
        En caso de que un RUT consultado no tenga información de *Sector* o *Distrito*, significa que no existe en la base consolidada actual.
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
