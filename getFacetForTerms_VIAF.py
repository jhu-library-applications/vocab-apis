import pandas as pd
import argparse
from datetime import datetime
from rdflib import Namespace, Graph, URIRef
import requests

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')

args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

df_1 = pd.read_csv(filename, header=0)
viaf_ids = df_1.viaf_id.to_list()

headers = {'User-Agent': 'Custom user agent'}
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
schema = Namespace('http://schema.org/')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
baseURL = 'http://www.viaf.org/viaf/'
lc_base = 'http://id.loc.gov/authorities/names/'
ext = '.rdf.xml'
json = '/justlinks.json'

facets = ['PersonalName', 'CorporateName', 'FamilyName', 'Geographic', 'Title',
          'ConferenceName']

all_items = []
for link in viaf_ids:
    tinyDict = {}
    tinyDict['viaf_id'] = link
    links = requests.get(link+json, timeout=30, headers=headers).json()
    lc_id = links.get('LC')
    lc_id = lc_id[0]
    link = lc_base+lc_id
    g = Graph()
    data = g.parse(link+ext, timeout=30, headers=headers, format='xml')
    uri = URIRef(link)
    preflabel = g.value(uri, skos.prefLabel)
    print(preflabel)
    tinyDict['label.loc'] = preflabel
    types = g.objects(uri, rdf.type)
    for type in types:
        for facet in facets:
            if facet in type:
                tinyDict['facet'] = facet
    all_items.append(tinyDict)


df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
df.to_csv('viafFacets_'+dt+'.csv', header='column_names', index=False)
