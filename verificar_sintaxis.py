import traceback

try:
    with open('analisis_func.py', 'r', encoding='utf-8') as f:
        compile(f.read(), 'analisis_func.py', 'exec')
    print("✅ Sintaxis OK")
except SyntaxError as e:
    print("❌ ERROR DE SINTAXIS:")
    print(f"  Archivo: {e.filename}")
    print(f"  Línea: {e.lineno}")
    print(f"  Columna: {e.offset}")
    print(f"  Texto: {e.text.strip() if e.text else 'None'}")
    print(f"  Mensaje: {e.msg}")
except Exception as e:
    print(f"Otro error: {e}")
