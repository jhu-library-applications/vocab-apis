import pandas as pd
import argparse
from datetime import datetime
from rdflib import Namespace, Graph

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')

args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

df_1 = pd.read_csv(filename, header=0)
fast_ids = df_1.fast_id.to_list()

skos = Namespace('http://www.w3.org/2004/02/skos/core#')
schema = Namespace('http://schema.org/')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
baseURL = 'http://id.worldcat.org/fast/'
ext = '.rdf.xml'

all_items = []
for link in fast_ids:
    tinyDict = {}
    tinyDict['fastID'] = link
    g = Graph()
    # id = fast_id[3:].strip()
    # print(id)
    link = link+ext
    graph = g.parse(link, format='xml')
    objects = graph.objects(subject=None, predicate=skos.inScheme)
    for object in objects:
        if 'facet' in object:
            facet = object.replace(baseURL+"ontology/1.0/#facet-", "")
            print(facet)
            tinyDict['facet'] = facet
            all_items.append(tinyDict)
    for externalID in g.objects(None, schema.sameAs):
        print(externalID)
        if 'viaf' in externalID:
            tinyDict['viaf'] = externalID
    all_items.append(tinyDict)


df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
df.to_csv('fastFacets_'+dt+'.csv', header='column_names', index=False)
