import requests
import pandas as pd
import argparse
from datetime import datetime
from rdflib import Namespace, Graph, URIRef, exceptions

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')

args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

df_1 = pd.read_csv(filename, header=0)
searchTerms = df_1['name'].to_list()

# Configuration for requests.
headers = {'User-Agent': 'Custom user agent'}
lc = requests.Session()
ft = requests.Session()
baseURL = 'http://id.loc.gov/authorities/'
mads = Namespace('http://www.loc.gov/mads/rdf/v1#')
auth = URIRef('http://id.loc.gov/authorities/')


def get_graph(url):
    g = Graph()
    try:
        response = lc.get(url, timeout=30, headers=headers)
        text_data = response.text
        parsed_graph = g.parse(data=text_data)
    except requests.exceptions.Timeout:
        parsed_graph = None
    except exceptions.ParserError:
        parsed_graph = None
    return parsed_graph


all_items = []
for searchTerm in searchTerms:
    print(searchTerm)
    searchTerm = searchTerm.rstrip('.')
    result = {'term': searchTerm}
    label_url = baseURL+'names/label/'+searchTerm
    data = lc.get(label_url, timeout=30, headers=headers)
    foundName = data.ok
    newURL = data.url
    if foundName:
        newURL = data.url
        newURL = newURL.replace('-781', '')
        newURL = newURL.replace('https', 'http')
        newURL = newURL.replace('.html', '.nt')
        print(newURL)
        graph = get_graph(newURL)
        if graph:
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
            for item in graph.objects(subject=URIRef(uri), predicate=mads.hasExactExternalAuthority):
                if 'viaf' in item:
                    response = requests.get(item)
                    viaf_url = response.url
                    viaf_url = viaf_url.replace('/#skos:Concept', '')
                    result['viaf_URI'] = viaf_url
            for item in graph.objects(subject=URIRef(uri), predicate=mads.useFor):
                print(item)
                if 'subjects' in item:
                    result['lcsh_URI'] = item
    all_items.append(result)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
df.to_csv('authorizedNamesResults_'+dt+'.csv', index=False)