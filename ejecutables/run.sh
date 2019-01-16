#!/bin/bash

# Creamos las carpetas necesarias
mkdir edges
mkdir edges_clean

# Instalamos las librerias necesarias para python 3
pip3 install -r requirements.txt

# Descargamos los datos necesarios
python3 web-scraping.py product=["Textiles and Clothing"] year=[2000]
python3 web-scraping.py product=["Textiles and Clothing"] year=[2008]
python3 web-scraping.py product=["Textiles and Clothing"] year=[2016]

python3 web-scraping.py product=["Fuels"] year=[2000]
python3 web-scraping.py product=["Fuels"] year=[2008]
python3 web-scraping.py product=["Fuels"] year=[2016]

# Movemos los ficheros de aristas a una carpeta para que el script que limpia los paises que no necesitemos
# pueda utilizarlos facilmente
mv *-exports-*.csv ./edges

# Se ejecuta el script que filtra los paises en los archivos csv
python3 clean-countries.py Fr.\ So.\ Ant.\ Tr Special\ Categories United\ States\ Minor\ Outlying\ I Bunkers Occ.Pal.Terr Other\ Asia,\ nes Unspecified Br.\ Antr.\ Terr Us\ Msc.Pac.I Free\ Zones Neutral\ Zone Yugoslavia

