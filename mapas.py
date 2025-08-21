import geopandas as gpd
import plotly.graph_objects as go

# Cargar primer GeoJSON
gdf1 = gpd.read_file(r"D:\DESARROLLO PROGRAMACION\data_health\COMUNA_CHOLCHOL.geojson")

# Cargar segundo GeoJSON
gdf2 = gpd.read_file(r"D:\DESARROLLO PROGRAMACION\data_health\d_carirriñe.geojson")

# Crear figura base
fig = go.Figure()

# Función para agregar polígonos a la figura
def add_polygons(gdf, line_color="black"):
    for geom in gdf.geometry:
        if geom.geom_type == "Polygon":
            x, y = geom.exterior.coords.xy
            fig.add_trace(go.Scattermapbox(
                lon=list(x),
                lat=list(y),
                mode="lines",
                line=dict(width=2, color=line_color),
                fill=None
            ))
        elif geom.geom_type == "MultiPolygon":
            for poly in geom.geoms:
                x, y = poly.exterior.coords.xy
                fig.add_trace(go.Scattermapbox(
                    lon=list(x),
                    lat=list(y),
                    mode="lines",
                    line=dict(width=2, color=line_color),
                    fill=None
                ))

# Agregar polígonos de ambos GeoJSON
add_polygons(gdf1, line_color="black")     # Primer geojson en negro
add_polygons(gdf2, line_color="red")       # Segundo geojson en rojo

# Configuración de mapa
fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        center={"lat": gdf1.geometry.centroid.y.mean(),
                "lon": gdf1.geometry.centroid.x.mean()},
        zoom=10
    ),
    height=600,
    margin={"r":0,"t":0,"l":0,"b":0}
)

fig.show()
