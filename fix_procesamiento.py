import codecs

with codecs.open('analisis_func.py', 'r', 'utf-8') as f:
    contenido = f.read()

target = """@st.cache_data(ttl=600)
def procesamiento_agenda(lista_dfs):

    # 1. Concatenar los DataFrames
    df_concat = pd.concat(lista_dfs, ignore_index=True)"""

replacement = """@st.cache_data(ttl=600)
def procesamiento_agenda(_lista_dfs):

    # 1. Concatenar los DataFrames
    df_concat = pd.concat(_lista_dfs, ignore_index=True)"""

if target in contenido:
    contenido = contenido.replace(target, replacement)
    print("Corregido procesamiento_agenda con exito.")
else:
    print("No se encontro el target EXACTO. Intentando búsqueda flexible...")
    import re
    pattern = r'@st\.cache_data\(ttl=600\)\s*def procesamiento_agenda\(lista_dfs\):\s*(# 1\. Concatenar los DataFrames\s*df_concat = pd\.concat\()lista_dfs'
    match = re.search(pattern, contenido, re.DOTALL)
    if match:
        contenido = re.sub(r'def procesamiento_agenda\(lista_dfs\):', 'def procesamiento_agenda(_lista_dfs):', contenido)
        contenido = re.sub(r'df_concat = pd\.concat\(lista_dfs', 'df_concat = pd.concat(_lista_dfs', contenido)
        print("Corregido con regex.")
    else:
        print("Tampoco se encontro con regex.")

with codecs.open('analisis_func.py', 'w', 'utf-8') as f:
    f.write(contenido)
