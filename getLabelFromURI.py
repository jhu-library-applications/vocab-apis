
import pandas as pd
import argparse
from datetime import datetime
from rdflib import Namespace, Graph, URIRef

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')


columnList = ['fast_id', 'geo_id']
df = pd.read_csv(filename, header=0)


# Configure namespaces.
headers = {'User-Agent': 'Custom user agent'}
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
gn = Namespace('http://www.geonames.org/ontology#')


def convertLinks(url):
    url = url.rstrip('/')
    if 'https://sws' in url:
        url = url+'/about.rdf'
        return url
    elif 'https://sws' not in url:
        if 'https:' not in url:
            url = url.replace('://www.', 's://sws.')
            url = url+'/about.rdf'
            return url
        else:
            url = url.replace('://www.', '://sws.')
            url = url+'/about.rdf'
            return url


all_items = []
for count, row in df.iterrows():
    tinyDict = {}
    for column in columnList:
        tinyDict['id'] = row['identifier']
        item = row[column]
        item = str(item)
        item = item.strip()
        if 'id.worldcat' in item:
            g = Graph()
            data = g.parse(item, timeout=30, headers=headers, format='xml')
            uri = URIRef(item)
            preflabel = g.value(uri, skos.prefLabel)
            print(preflabel)
            tinyDict['uri.worldcat'] = uri
            tinyDict['label.worldcat'] = preflabel
        elif 'geonames' in item:
            item = convertLinks(item)
            print(item)
            g = Graph()
            data = g.parse(item, timeout=30, headers=headers, format='xml')
            uri = URIRef(item.rstrip('about.rdf'))
            preflabel = g.value(uri, gn.name)
            print(preflabel)
            tinyDict['uri.geo'] = uri
            tinyDict['label.geo'] = preflabel
        elif 'viaf' in item:
            g = Graph()
            data = g.parse(item, timeout=30, headers=headers)
            print(data)
            tinyDict['uri.viaf'] = uri
            tinyDict['label.viaf'] = preflabel
        elif 'aat' in item:
            g = Graph()
            data = g.parse(item, timeout=30, headers=headers)
            print(data)
            tinyDict['uri.aat'] = uri
            tinyDict['label.aat'] = preflabel
        else:
            pass
    all_items.append(tinyDict)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
df.to_csv('labelsFromURI_'+dt+'.csv', index=False)
