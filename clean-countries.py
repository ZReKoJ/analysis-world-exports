import pandas as pd
import os, sys

df1 = pd.read_csv('nodes.csv',sep=';')

COUNTRIES_TO_CLEAN = sys.argv[1:]
EXPORTS_TO_CLEAN = []

for i in COUNTRIES_TO_CLEAN:
    select = (df1.loc[df1['Label'] == i, 'Id']).get_values()[0]
    EXPORTS_TO_CLEAN.append(select)
    df1 = df1.loc[df1['Label'] != i]

dirs = os.listdir('edges')

print(EXPORTS_TO_CLEAN)
print(dirs)
# This would print all the files and directories
columns = ['export-product-share-percentage','revealed-comparative-advantage','world-growth','country-growth']
for file in dirs:
    if file != '.DS_Store':
        df2 = pd.read_csv('./edges/'+file,sep=';')
        df2 = df2.drop(columns, axis=1)
        df2 = df2.rename(index=str, columns={"export-thousand-dolar": "Weight"})
        for i in EXPORTS_TO_CLEAN:
            df2 = df2.loc[df2['Source'] != i]
            df2 = df2.loc[df2['Target'] != i]
            df2 = df2.loc[df2['Weight'] > 0]

        df2.to_csv('edges_clean/'+file, sep=';', encoding='utf-8', index=False)

df1.to_csv('nodes_clean.csv', sep=';', encoding='utf-8', index=False)
