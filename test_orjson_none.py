import sys
# Forzar a orjson como no disponible
sys.modules['orjson'] = None

try:
    import plotly.io as pio
    import plotly.express as px

    fig = px.bar(x=[1, 2], y=[3, 4])
    res = pio.to_json(fig)
    print("Éxito! Conversión a JSON realizada sin orjson.")
    
except Exception as e:
    print("Error:", e)
