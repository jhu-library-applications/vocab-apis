import requests
import pandas as pd
import argparse
from datetime import datetime
from bs4 import BeautifulSoup as Soup
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
searchTerms = df_1.to_dict('records')


# Configuration for requests.
headers = {'User-Agent': 'Custom user agent'}
lc = requests.Session()
ft = requests.Session()
baseURL = 'http://id.loc.gov/authorities/'
mads = Namespace('http://www.loc.gov/mads/rdf/v1#')
auth = URIRef('http://id.loc.gov/authorities/')



def getGraph(url, format):
    g = Graph()
    try:
        data = lc.get(url, timeout=30, headers=headers)
        data = data.text
        graph = g.parse(data=data, format=format)
    except requests.exceptions.Timeout:
        graph = None
    return graph


all_items = []
for item in searchTerms:
    vocab = item.get('vocab')
    searchTerm = item.get('term')
    print(vocab, searchTerm)
    searchTerm = searchTerm.rstrip('.')
    result = {'term': searchTerm}
    url = baseURL+'names/label/'+searchTerm
    data = lc.get(url, timeout=30, headers=headers)
    foundName = data.ok
    newURL = data.url
    if foundName:
        newURL = data.url
        newURL = newURL.replace('-781', '')
        newURL = newURL.replace('.html', '')
        print(newURL)
        graph = getGraph(newURL+'.nt', 'nt')
        for item in graph.subject_objects(mads.authoritativeLabel):
            if 'authorities/names' in item[0]:
                if item[1].value == searchTerm:
                    print('Heading validated')
                    uri = item[0]
                    result['lcnaf_URI'] = item[0]
                    result['lcnaf_Label'] = item[1].value
        for item in graph.objects(subject=URIRef(uri), predicate=mads.hasCloseExternalAuthority):
            if 'fast' in item:
                result['fast_URI'] = item
        for item in graph.objects(subject=URIRef(uri), predicate=mads.useFor):
            print(item)
            if 'subjects' in item:
                result['lcsh_URI'] = item
    all_items.append(result)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
df.to_csv('authorizedHeadingResults_'+dt+'.csv', index=False)
