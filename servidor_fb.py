import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

firebase_config = {
  "type": st.secrets['firebase']['type'],
  "project_id": st.secrets['firebase']['project_id'],
  "private_key_id": st.secrets['firebase']['private_key_id'],
  "private_key": st.secrets['firebase']['private_key'],
  "client_email": st.secrets['firebase']['client_email'],
  "client_id": st.secrets['firebase']['client_id'],
  "auth_uri": st.secrets['firebase']['auth_uri'],
  "token_uri": st.secrets['firebase']['token_uri'],
  "auth_provider_x509_cert_url": st.secrets['firebase']['auth_provider_x509_cert_url'],
  "client_x509_cert_url": st.secrets['firebase']['client_x509_cert_url'],
  "universe_domain": st.secrets['firebase']['universe_domain']
}

#Inicializacion
cred = credentials.Certificate(firebase_config)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets['firebase']['url_db']})

#--------------ACCIONES_DB------------------------
def ingresar_registro_bd(nom_tabla,datos):
    ref = db.reference(nom_tabla)
    ref.push(datos)

    print(f'Ingreso exitoso! {nom_tabla}:{datos}')

def leer_registro(nom_tab,id_reg = None):
    if id_reg:
        ref = db.reference(f"{nom_tab}/{id_reg}")
    else:
        ref = db.reference(nom_tab) #se necesita nombre de la tabla e id "documentos/abc123"
    registro = ref.get() or {}

    return registro


def actualizar_registro(tabla_nom,data,id_reg=None):
    if id_reg:
        ref = db.reference(f'{tabla_nom}/{id_reg}')
    else:
        ref = db.reference(tabla_nom)
    ref.update(data)

    print(f'Se realizó la actualización de {tabla_nom}')

def borrar_registro(tabla_nom, id_reg):
    try:
        ref = db.reference(f'{tabla_nom}/{id_reg}')
        ref.delete()
        print(f'Registro eliminado de {tabla_nom} con ID: {id_reg}')
    except Exception as e:
        print(f'Error al eliminar el registro: {e}')
