#pip install beautifulsoup4
from bs4 import BeautifulSoup
import urllib.request
import json
import re
import sys
import os.path

def getPage(url):
    page = urllib.request.urlopen(url).read()
    return BeautifulSoup(page, 'html.parser')

def webScrapingGetCountries(soup):
    # Storing all links
    countriesHref = {}

    # Getting the big section cointaining all href to countries
    section = soup.select("#singleCol > section")[1]
    # Getting lists sorted in alphabetical order
    lists = section.select("div.content > ul.bulleted")
    for alphabet in lists:
        # Getting an array of tag a containing hrefs to countries
        countries = alphabet.select("li > h3.countryHeading > a")
        for country in countries:
            # Storing country as key and link as value
            countriesHref[country.text] = country['href']

    return countriesHref

# _ports: "Exports" or "Imports"
def webScrapingGetProducts(soup, country, _ports):
    # Storing all links
    productsHref = {}

    # Getting the big section cointaining all href to sorts of products
    section = soup.select("#staticPageContent > div.content > div.row > div.col-lg-3 > section")[0]
    # Getting lists (second one) 
    list = section.select("div.content > div.row > div.col-md-12 ul.bulleted")[1]
    products = list.select("li > h3.countryHeading")
    for i in products:
        product = i.text
        product = product.replace(country, "")
        product = re.sub('Exports.*', '', product)
        product = re.sub('Imports.*', '', product)
        product = product.strip()
        for link in i.select("a"):
            if link.text == _ports:
                productsHref[product] = link['href']

    return productsHref

def webScrapingGetData(soup): 
    # Gets all scripts without src
    data = soup.findAll('script', attrs={'src':False})

    # Getting all useful data i donno why those data are stored in javascript instead of html
    parsedData = re.findall(r'var +col[0-5] += +(\["[^\]]+"\]);', str(data))
    if len(parsedData) == 6:
        parsedData[0] = json.loads(parsedData[0])
        parsedData[1] = json.loads(parsedData[1])
        parsedData[2] = json.loads(parsedData[2])
        parsedData[3] = json.loads(parsedData[3])
        parsedData[4] = json.loads(parsedData[4])
        parsedData[5] = json.loads(parsedData[5])
        arrayResult = []
        for i in range(len(parsedData[0])):
            result = {
                "partner-name": parsedData[0][i],
                "export-thousand-dolar": parsedData[1][i],
                "export-product-share-percentage": parsedData[2][i],
                "revealed-comparative-advantage": parsedData[3][i],
                "world-growth": parsedData[4][i],
                "country-growth": parsedData[5][i]
            }
            arrayResult.append(result)
        return arrayResult
    return None

def main(yearStart, yearEnd, countryStart, countryEnd, mode): 
    # page to start with scraping
    url = "https://wits.worldbank.org/countrystats.aspx?lang=en"

    delimiter = ";"
    node_title = ["Id", "Label"]
    edge_title = ["Source", "Target", "Type", "Product", "Year"]

    # more edge parameters
    edge_title.append("export-thousand-dolar")
    edge_title.append("export-product-share-percentage")
    edge_title.append("revealed-comparative-advantage")
    edge_title.append("world-growth")
    edge_title.append("country-growth")

    print("Scanning countries ...")
    soup = getPage(url)
    # Country names and their links
    countriesHref = webScrapingGetCountries(soup)
    
    # Country names and their ids as nodes
    countryDict = {}

    for i, country in enumerate(countriesHref.items()):
        countryDict[country[0]] = i + 1
    
    nodes = None
    # If exists nodes.csv, then edit, otherwise create
    if os.path.isfile("nodes.csv"):
        nodes = open("nodes.csv", "r")
        nodes.readline()
        for line in nodes.readlines():
            countryData = line.replace("\n", "").split(delimiter)
            countryDict[countryData[1]] = countryData[0]
        nodes.close()
    else:
        nodes = open("nodes.csv", "w")
        nodes.write(delimiter.join(node_title) + "\n")
        for key, value in countryDict.items():
            nodes.write(str(value) + delimiter + str(key) + "\n")
        nodes.close()
        
    #countryDict["Serbia, FR(Serbia/Montenegro)"] = 196

    # loop range year
    for year in range(yearStart, yearEnd + 1):
        print("Scanning year", year, mode.lower(), "...")

        title = str(year) + "-" + mode.lower()
        if len(product) > 0:
            title = title + "-" + "-".join(product)
        edges = open(title + ".csv", "w")
        edges.write(delimiter.join(edge_title) + "\n")

        # loop range country
        for countryKey, countryValue in countriesHref.items():
            if countryKey >= countryStart and countryKey <= countryEnd:
                print("Scanning year", year, countryKey, mode.lower(), "...")

                soup = getPage(countryValue)
                productsHref = webScrapingGetProducts(soup, countryKey, mode)

                # loop products
                for productKey, productValue in productsHref.items():

                    if productKey in product:
                        print("Scanning year", year, countryKey, productKey, mode.lower(), "...")

                        soup = getPage(productValue.replace("LTST", str(year)))
                        arrayResult = webScrapingGetData(soup)
                        if arrayResult is not None:
                            for result in arrayResult:
                                if result["partner-name"] not in countryDict:
                                    countryDict[result["partner-name"]] = len(countryDict) + 1
                                    nodes = open("nodes.csv", "a")
                                    nodes.write(str(len(countryDict)) + delimiter + str(result["partner-name"]) + "\n")
                                    nodes.close()

                                written = []
                                written.append(str(countryDict[countryKey]))
                                written.append(str(countryDict[result["partner-name"]]))
                                written.append("Directed")
                                written.append(str(productKey))
                                written.append(str(year))
                                written.append(str(result["export-thousand-dolar"]))
                                written.append(str(result["export-product-share-percentage"]))
                                written.append(str(result["revealed-comparative-advantage"]))
                                written.append(str(result["world-growth"]))
                                written.append(str(result["country-growth"]))
                                edges.write(delimiter.join(written) + "\n")
                
        edges.close()

    nodes.close()

############################################
# Problem cannot get year range cuz hidden #
############################################

#############################################################################################################
# USAGE:                                                                                                    #
#                                                                                                           #
# python web-scraping.py country=[countryStart,countryEnd] year=[yearStart,yearEnd] exports/imports         #
# python web-scraping.py country=[country] year=[year] exports                                              #
# python web-scraping.py country=[countryStart,countryEnd]                                                  #
# python web-scraping.py year=[yearStart,yearEnd] imports                                                   #
# python web-scraping.py product=[Animal] imports                                                   #
#                                                                                                           #
# args could be in any order                                                                                #
# between brackets [] must not have any empty space                                                         #
# what you have to set between brackets [] is a range, but also one value meaning range of length 1         #
# default values for those args are shown below so if you do not provide those args they are set by default #
# make sure that country names are identical to what is shown in the page to scripe                         #
#############################################################################################################

yearStart = 1950
yearEnd = 2020
countryStart = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
countryEnd = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
mode = "Exports"
product = []

# Managing args
if len(sys.argv) > 1:
    args = sys.argv
    args.pop(0)
    for arg in args:
        tags = arg.split("=")
        if len(tags) == 2:
            tags[1] = str(tags[1]).replace("[", "").replace("]", "").split(",")
        if str(tags[0]).lower() == "country":
            countryStart = tags[1][0]
            if len(tags[1]) == 1:
                countryEnd = countryStart
            else:
                countryEnd = tags[1][1]
        if str(tags[0]).lower() == "year":
            yearStart = int(tags[1][0])
            if len(tags[1]) == 1:
                yearEnd = yearStart
            else:
                yearEnd = int(tags[1][1])
        if str(tags[0]).lower() == "product":
            product = tags[1]
        if str(tags[0]).lower() == "exports":
            mode = "Exports"
        if str(tags[0]).lower() == "imports":
            mode = "Imports"

main(yearStart, yearEnd, countryStart, countryEnd, mode)

exit(0)