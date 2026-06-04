import sys
import pandas as pd

# Mock Streamlit cache_data BEFORE importing anything from analisis_func
import streamlit as st

# Crear mocks para todos los decoradores de caché que use analisis_func
def mock_decorator(*args, **kwargs):
    return lambda f: f

st.cache_data = mock_decorator
st.cache_resource = mock_decorator

# Añadir el directorio al path
sys.path.append('.')

# Importar la función que modificamos
from analisis_func import normaliza_direcc

print("Cargando datos de prueba...")
df = pd.read_csv('nuevas_ubicaciones.tsv', sep='\t')

# Simular que 'Nombre_ubicacion' es la 'DIRECCION'
df['DIRECCION'] = df['Nombre_ubicacion']

print("Ejecutando normaliza_direcc...")
df_resultado = normaliza_direcc(df)

print("\n--- RESULTADOS DE VERIFICACION ---")

# Verificar algunos casos
intentos = 0
fallas = 0

output = []
output.append("--- Detalle de Clasificacion ---")

for idx, row in df_resultado.iterrows():
    esperado_centro = row['Area_inf_centro']
    obtenido_centro = row['AREA_INF_CENTRO']
    nombre = row['Nombre_ubicacion']
    distrito = row['DISTRITO']
    comunidad = row['COMUNIDAD']

    if esperado_centro != obtenido_centro:
        fallas += 1
        output.append(f"❌ FALLA: {nombre} | Distrito: {distrito} | Comunidad: {comunidad} | Esperado: {esperado_centro} | Obtenido: {obtenido_centro}")
    else:
        intentos += 1

print(f"Total pruebas: {len(df_resultado)}")
print(f"Exitosos: {intentos}")
print(f"Fallas: {fallas}")

output.append(f"\nResumen: {intentos} Exitosos, {fallas} Fallas")

with open('reporte_verificacion.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

if fallas == 0:
    print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE.")
else:
    print(f"⚠️ {fallas} PRUEBAS FALLARON. Revisa reporte_verificacion.txt")
