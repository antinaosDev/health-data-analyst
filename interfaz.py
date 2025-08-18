import streamlit as st
from servidor_fb import *

# ---------- Configuración de página ----------
st.set_page_config(page_title="Análisis y Gestión de datos Salud", page_icon="🩺", layout="wide")

# ---------- Inicializa el estado ----------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""
if "rol" not in st.session_state:
    st.session_state["rol"] = ""

# ---------- Estilos personalizados globales ----------
st.markdown("""
<style>
html, body, .stApp {
    background-color: #F4F7FA;
    margin: 0;
    padding: 0;
}

/* --- TÍTULO --- */
.title {
    font-size: 28px;
    font-weight: bold;
    color: #003366;
    margin-top: 10px;
    margin-bottom: 30px;
}

/* --- INPUTS --- */
.stTextInput > div > input,
.stPassword > div > input {
    background-color: #ffffff;
    color: #003366;
    border-radius: 5px;
    border: 1px solid #cccccc;
    padding: 10px;
    font-size: 14px;
}

/* --- BOTÓN --- */
.stButton > button {
    background-color: #003366 !important;
    color: white !important;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 15px;
    border: none;
    cursor: pointer;
}
.stButton > button:hover {
    background-color: #002244 !important;
    color: white !important;
}

/* --- LABELS --- */
label {
    color: #003366 !important;
    font-weight: 600;
}

/* --- CONTACTO --- */
.contact-link {
    margin-top: 25px;
    font-size: 14px;
    color: #555;
    text-align: center;
}
.contact-link a {
    color: #4A90E2;
    text-decoration: none;
    font-weight: 600;
}
.contact-link a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# ---------- Verificación de login con base de datos ----------
def verificar_login(usuario, password):
    data_login = leer_registro('login')
    if data_login:
        for key, data in data_login.items():
            if data.get("USER") == usuario and data.get("PASS") == password:
                st.session_state["usuario"] = data.get("USER")
                st.session_state["rol"] = data.get("ROL")
                return True
    return False

# ---------- Página de login ----------
def pagina_login():
    with st.container():
        with st.form("form_login"):
            st.markdown('<div class="login-container">', unsafe_allow_html=True)

            # Logo
            st.image(r"D:\DESARROLLO PROGRAMACION\STREAMLIT\proyecto_gastos\logo_nuevo.png", width=100)

            st.markdown('<div class="title">Iniciar Sesión</div>', unsafe_allow_html=True)
            usuario_input = st.text_input("Nombre de usuario", max_chars=30)
            password_input = st.text_input("Contraseña", type="password")
            submit_button = st.form_submit_button("Ingresar")

            st.markdown('</div>', unsafe_allow_html=True)

            if submit_button:
                if verificar_login(usuario_input, password_input):
                    st.session_state["logged_in"] = True
                    st.success("¡Inicio de sesión exitoso!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos. Intenta nuevamente.")

    # Enlace de contacto
    st.markdown("""
    <div class="contact-link">
        ¿Tienes problemas para iniciar sesión? <br>
        <a href="https://alain-antinao-s.notion.site/Alain-C-sar-Antinao-Sep-lveda-1d20a081d9a980ca9d43e283a278053e?pvs=74" target="_blank">
        Contacta al administrador</a>
    </div>
    """, unsafe_allow_html=True)

# ---------- Lógica principal ----------
if not st.session_state["logged_in"]:
    pagina_login()
else:
    st.success(f"Bienvenido, {st.session_state['usuario']} 👋 (Rol: {st.session_state['rol']})")

    # ------------------ ENCABEZADO -------------------
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 5, 1])
        with col1:
            st.image("D:/DESARROLLO PROGRAMACION/data_health/logo_data_s.png", width=90)
        with col2:
            st.markdown("<h1 style='margin: 0; color: #0072B2;text-align: center ;'>Análisis de Datos Salud</h1>", unsafe_allow_html=True)
        with col3:
            st.image("D:/DESARROLLO PROGRAMACION/data_health/logo_alain.png", width=120)

    # ------------------ DEFINICIÓN DE PÁGINAS -------------------
    pages = {
        'Análisis y estadística📊': [
            st.Page("analisis_agenda.py", title="Análisis Agenda Médica", icon="🖱️"),
            st.Page("analisis_percapita.py", title="Análisis Percápita", icon="📈")
        ],
        'Categorización Diagnóstico🩺': [
            st.Page("categorizacion_ges.py", title="Preclasificador GES", icon="🏥")
        ],
        'Utilidades🛠️': [
            st.Page("sub_ut1.py", title="Combinador de documentos🖇️"),
        ]
    }

    # ------------------ NAVEGACIÓN -------------------
    page = st.navigation(pages)
    page.run()
