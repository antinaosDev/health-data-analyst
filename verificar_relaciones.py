import pandas as pd

df = pd.read_csv('nuevas_ubicaciones.tsv', sep='\t')

output = []
output.append("--- Distribucion de Centros por Distrito ---")
for distrito in df['Distrito'].unique():
    centros = df[df['Distrito'] == distrito]['Area_inf_centro'].unique()
    output.append(f"Distrito: {distrito} -> Centros: {list(centros)}")

output.append("\n--- Comunidades en Repocura por Centro ---")
repocura_df = df[df['Distrito'] == 'Repocura']
for centro in repocura_df['Area_inf_centro'].unique():
    comunidades = repocura_df[repocura_df['Area_inf_centro'] == centro]['Nombre_ubicacion'].unique()
    output.append(f"\nCentro: {centro} (Total {len(comunidades)} communities)")
    # Incluir las comunidades para guardarlas
    for c in comunidades:
        output.append(f"  - {c}")

with open('relaciones_centros.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Verificacion completada.")
