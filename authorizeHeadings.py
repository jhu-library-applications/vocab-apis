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
fastURL = 'http://id.worldcat.org/fast/search?query=cql.any+all+%22'
fastPara = '%22&fl=oclc.heading&recordSchema=info:srw/schema/1/rdf-v2.0'
mads = Namespace('http://www.loc.gov/mads/rdf/v1#')
auth = URIRef('http://id.loc.gov/authorities/')
authorities = {'lcnaf': 'names',
               'lcsh': 'subjects',
               'genre': 'genreForms'}


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
    type = authorities.get(vocab)
    if vocab != 'fast':
        url = baseURL+type+'/label/'+searchTerm
        data = lc.get(url, timeout=30, headers=headers)
        foundName = data.ok
        newURL = data.url
        if foundName:
            newURL = data.url
            newURL = newURL.replace('.html', '')
            print(newURL)
            graph = getGraph(newURL+'.nt', 'nt')
            for item in graph.subject_objects((mads.authoritativeLabel)):
                if auth+type in item[0]:
                    if item[1].value == searchTerm:
                        print('Heading validated')
                        result['authURI'] = item[0]
                        result['authLabel'] = item[1].value
    else:
        data = ft.get(fastURL+searchTerm+fastPara)
        data = data.content
        soup = Soup(data, features='lxml')
        record = soup.find('record')
        identifier = record.find('dct:identifier')
        identifier = identifier.string
        authLabel = record.find('skos:preflabel')
        authLabel = authLabel.string
        print(authLabel)
        if authLabel == searchTerm:
            print('Heading validated')
            result['authLabel'] = authLabel
            result['authURI'] = identifier
    all_items.append(result)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
df.to_csv('authorizedHeadingResults_'+dt+'.csv', index=False)
