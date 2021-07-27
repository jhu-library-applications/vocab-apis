
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


columnList = ['lc_id']
df = pd.read_csv(filename)


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
    row = row
    item = row['lc_id']
    item = str(item)
    item = item.strip()
    print(item)
    if 'id.loc' in item:
        print('hi')
        g = Graph()
        data = g.parse(item+'.rdf.xml', timeout=0.001, headers=headers)
        uri = URIRef(item)
        preflabel = g.value(uri, skos.prefLabel)
        print(preflabel)
        row['uri.worldcat'] = uri
        row['label.worldcat'] = preflabel
    elif 'geonames' in item:
        item = convertLinks(item)
        print(item)
        g = Graph()
        data = g.parse(item, timeout=30, headers=headers, format='xml')
        uri = URIRef(item.rstrip('about.rdf'))
        preflabel = g.value(uri, gn.name)
        print(preflabel)
        row['uri.geo'] = uri
        row['label.geo'] = preflabel
    elif 'viaf' in item:
        g = Graph()
        data = g.parse(item, timeout=30, headers=headers)
        print(data)
        row['uri.viaf'] = uri
        row['label.viaf'] = preflabel
    elif 'aat' in item:
        g = Graph()
        data = g.parse(item, timeout=30, headers=headers)
        print(data)
        row['uri.aat'] = uri
        row['label.aat'] = preflabel
    else:
        pass
    all_items.append(row)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
df.to_csv('labelsFromURI_'+dt+'.csv', index=False)
