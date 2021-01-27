import pandas as pd
import argparse
from datetime import datetime
from rdflib import Namespace, Graph
from urllib.parse import urlparse

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
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
baseURL = 'http://id.worldcat.org/fast/'
ext = '.rdf.xml'

all_items = []
for fast_id in fast_ids:
    g = Graph()
    id = fast_id[3:].strip()
    link = baseURL+id+ext
    graph = g.parse(link, format='xml')
    objects = graph.objects(subject=None, predicate=schema.sameAs)
    tinyDict = {'fast_id': fast_id}
    for object in objects:
        label = graph.value(subject=object, predicate=rdfs.label)
        print(object, label)
        results = urlparse(object)
        authority = results.netloc
        print(authority)
        tinyDict[authority] = object
        tinyDict[authority+'_label'] = label
    all_items.append(tinyDict)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
df.to_csv('fastFacets'+dt+'.csv', header='column_names', index=False)
