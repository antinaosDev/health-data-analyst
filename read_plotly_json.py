import sys
import os

filepath = r"C:\Users\alain\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\plotly\io\_json.py"

if not os.path.exists(filepath):
    print("Archivo no encontrado en la ruta por defecto. Intentando dinámico.")
    import plotly
    filepath = os.path.join(os.path.dirname(plotly.__file__), 'io', '_json.py')

print(f"Leyendo: {filepath}")

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Mostrar cabecera y imports de modulo
    print("=== CABECERA (Imports) ===")
    for l in lines[:30]:
        print(l.rstrip())
        
    print("\n=== ALREDEDOR DE LINEA 146 ===")
    start_line = max(0, 130)
    end_line = min(len(lines), 160)
    for i in range(start_line, end_line):
        print(f"{i+1}: {lines[i].rstrip()}")
        
except Exception as e:
    print("Error:", e)
