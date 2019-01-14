import pandas as pd
import os, sys

nodes_csv = pd.read_csv('nodes.csv',sep=';')

countries_to_clean = sys.argv[1:]
exports_to_clean = []

for country in countries_to_clean:
    select = (nodes_csv.loc[nodes_csv['Label'] == country, 'Id']).get_values()
    if len(select) > 0:
        exports_to_clean.append(select[0])
        nodes_csv = nodes_csv.loc[nodes_csv['Label'] != country]

dirs = os.listdir('edges')

columns = ['export-product-share-percentage','revealed-comparative-advantage','world-growth','country-growth']
for file in dirs:
    if file != '.DS_Store':
        edges_csv = pd.read_csv('./edges/'+file,sep=';')
        edges_csv = edges_csv.drop(columns, axis=1)
        edges_csv = edges_csv.rename(index=str, columns={"export-thousand-dolar": "Weight"})
        for i in exports_to_clean:
            edges_csv = edges_csv.loc[edges_csv['Source'] != i]
            edges_csv = edges_csv.loc[edges_csv['Target'] != i]
            edges_csv = edges_csv.loc[edges_csv['Weight'] > 0]

        edges_csv.to_csv('edges_clean/'+file, sep=';', encoding='utf-8', index=False)

nodes_csv.to_csv('nodes_clean.csv', sep=';', encoding='utf-8', index=False)
