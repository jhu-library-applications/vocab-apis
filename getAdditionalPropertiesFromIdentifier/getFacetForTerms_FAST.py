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

dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

df_1 = pd.read_csv(filename, header=0)
fast_ids = df_1.URI.to_list()

headers = {'User-Agent': 'Custom user agent'}
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
schema = Namespace('http://schema.org/')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
baseURL = 'http://id.worldcat.org/fast/'
ext = '.rdf.xml'

all_items = []
for link in fast_ids:
    tinyDict = {'fastID': link}
    g = Graph()
    # id = fast_id[3:].strip()
    # print(id)
    full_link = link+ext
    data = g.parse(full_link, timeout=30, headers=headers, format='xml')
    uri = URIRef(link)
    pref_label = g.value(uri, skos.prefLabel)
    print(pref_label)
    tinyDict['label.worldcat'] = pref_label
    facets = g.objects(uri, skos.inScheme)
    for facet in facets:
        if 'facet' in facet:
            facet = facet.replace(baseURL+"ontology/1.0/#facet-", "")
            print(facet)
            tinyDict['facet'] = facet
    for externalID in g.objects(None, schema.sameAs):
        print(externalID)
        if 'viaf' in externalID:
            tinyDict['viaf'] = externalID
    all_items.append(tinyDict)


df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
df.to_csv('fastFacets_'+dt+'.csv', header='column_names', index=False)