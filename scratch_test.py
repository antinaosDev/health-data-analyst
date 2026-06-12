import pandas as pd
import chardet

archivos = [
    r"C:\Users\alain\Downloads\Detalle_Establecimineto.txt",
    r"C:\Users\alain\Downloads\Detalle_Establecimineto (1).txt",
    r"C:\Users\alain\Downloads\Detalle_Establecimineto (2).txt",
    r"C:\Users\alain\Downloads\Detalle_Establecimineto (3).txt"
]

def analyze_files(archivos):
    dfs = []
    for archivo in archivos:
        try:
            with open(archivo, 'rb') as f:
                rawdata = f.read(10000)
                result = chardet.detect(rawdata)
                encoding = result['encoding'] or 'latin1'
                
                try:
                    primera_linea = rawdata.decode(encoding).splitlines()[0]
                    if '\t' in primera_linea:
                        sep = '\t'
                    elif ';' in primera_linea:
                        sep = ';'
                    elif '|' in primera_linea:
                        sep = '|'
                    else:
                        sep = ','
                except:
                    sep = None
            
            df = pd.read_csv(archivo, encoding=encoding, sep=sep, engine='python', on_bad_lines='skip')
            df.columns = df.columns.str.strip().str.upper()
            dfs.append(df)
            print(f"Cargado {archivo}: {len(df)} registros.")
        except Exception as e:
            print(f"Error cargando {archivo}: {e}")

    df_full = pd.concat(dfs, ignore_index=True)
    if 'FECHA_NACIMIENTO' in df_full.columns:
        # Save original column to show what it looked like before conversion
        df_full['FECHA_NACIMIENTO_ORIGINAL'] = df_full['FECHA_NACIMIENTO']
        
        # Apply conversion
        df_full['FECHA_NACIMIENTO'] = pd.to_datetime(df_full['FECHA_NACIMIENTO'], errors='coerce', dayfirst=True)
        
        # Find nulls
        nulls = df_full[df_full['FECHA_NACIMIENTO'].isnull()]
        if not nulls.empty:
            print(f"\nSe encontraron {len(nulls)} registros con FECHA_NACIMIENTO nula:")
            cols_to_print = [c for c in ['RUT', 'RUN', 'NOMBRES', 'APELLIDO_PATERNO', 'FECHA_NACIMIENTO_ORIGINAL'] if c in nulls.columns]
            print(nulls[cols_to_print].to_string())
        else:
            print("\nTodos los registros tienen una FECHA_NACIMIENTO válida.")
    else:
        print("La columna FECHA_NACIMIENTO no existe en los archivos.")

analyze_files(archivos)
