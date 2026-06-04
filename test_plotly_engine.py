import plotly.io as pio

try:
    print("Engine actual:", pio.json_engine)
    # Cambiar a 'json' para evitar orjson
    pio.json_engine = 'json'
    print("Engine cambiado:", pio.json_engine)
    
    # Crear un gráfico y convertirlo a json para ver si falla
    import plotly.express as px
    fig = px.bar(x=[1, 2], y=[3, 4])
    res = pio.to_json(fig)
    print("Transformación exitosa sin orjson.")
    
except Exception as e:
    print("Error:", e)
