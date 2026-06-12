import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Importamos la configuración y funciones de la db
from servidor_fb import leer_registro, actualizar_registro

def main():
    try:
        # Leer la tabla completa de login
        usuarios = leer_registro('login')
        if not usuarios:
            print("No se encontraron usuarios en la tabla 'login'.")
            return

        for user_key, data in usuarios.items():
            username = data.get("USER")
            
            if username == "alain_adm1":
                print(f"Actualizando a {username} ({user_key}) con Nombre_completo: 'Alain Antinao S.'")
                actualizar_registro('login', {"Nombre_completo": "Alain Antinao S."}, id_reg=user_key)
                
            elif username == "grechen_p01":
                print(f"Actualizando a {username} ({user_key}) con Nombre_completo: 'Grechen Painemal'")
                actualizar_registro('login', {"Nombre_completo": "Grechen Painemal"}, id_reg=user_key)
                
        print("Actualización completada en Firebase.")
    except Exception as e:
        print(f"Error al conectar con Firebase o actualizar datos: {e}")

if __name__ == "__main__":
    main()
