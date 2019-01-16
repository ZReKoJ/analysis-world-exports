import pandas as pd
import os
import sys

nodes_csv = pd.read_csv('nodes.csv', sep=';')

countries_to_clean = sys.argv[1:]
exports_to_clean = []

# Buscamos los paises en el archivo csv de nodos para quitarlos
for country in countries_to_clean:
    select = (nodes_csv.loc[nodes_csv['Label'] == country, 'Id']).get_values()
    # Si existe el pais, guardamos su id para borrar las aristas
    # y borramos la fila de nodes.csv
    if len(select) > 0:
        exports_to_clean.append(select[0])
        nodes_csv = nodes_csv.loc[nodes_csv['Label'] != country]


# Buscamos todos los nombres de archivos de la carpeta edges donde
# estan los archivos csv con las aristas
dirs = os.listdir('edges')

# columnas que vamos a borrar de edges.csv
columns = ['export-product-share-percentage', 'revealed-comparative-advantage',
           'world-growth', 'country-growth']

# Procesamos cada csv dentro de edges/
for file in dirs:
    # Evitamos problemas con archivos de MacOS
    if file != '.DS_Store':
        edges_csv = pd.read_csv('./edges/' + file, sep=';')
        # Quitamos las columnas que no vamos a utilizar
        edges_csv = edges_csv.drop(columns, axis=1)
        # Cambiamos export-thousand-dolar por Weight
        edges_csv = edges_csv.rename(
                                     index=str,
                                     columns={
                                        "export-thousand-dolar": "Weight"
                                             }
                                     )
        for i in exports_to_clean:
            # Quitamos las filas de cada pais requerido y de los que
            # su peso sea 0
            edges_csv = edges_csv.loc[edges_csv['Source'] != i]
            edges_csv = edges_csv.loc[edges_csv['Target'] != i]
            edges_csv = edges_csv.loc[edges_csv['Weight'] > 0]

        # Guardamos los ficheros de arista modificados
        edges_csv.to_csv('edges_clean/'+file, sep=';', encoding='utf-8',
                         index=False)

# Guardamos el fichero de nodos filtrado
nodes_csv.to_csv('nodes_clean.csv', sep=';', encoding='utf-8', index=False)
