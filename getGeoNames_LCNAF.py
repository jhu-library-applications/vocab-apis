import requests
import argparse
from rdflib import Namespace, Graph, URIRef
import pandas as pd
from datetime import datetime

# Convert geographic names from LCNAF to geonames identifiers.
# Example: Baltimore County (Md.) n79018713
# --> Baltimore County https://www.geonames.org/4347790
# Also builds full hierarchal name: Baltimore County, Maryland, United States

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='Enter filename with csv.')
parser.add_argument('-p', '--parents')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.parents:
    parents = args.parents
else:
    parents = input('Enter yes if you want parent information: ')

# Some config for requests.
headers = {'User-Agent': 'Custom user agent'}
lc = requests.Session()
ft = requests.Session()
geo = requests.Session()

# Some config for loc APIs.
labelBase = 'http://id.loc.gov/authorities/names/label/'
ext = '.rdf.xml'

# Some config for linked data namespaces.
schema = Namespace('http://schema.org/')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
gn = Namespace('http://www.geonames.org/ontology#')
mads = Namespace('http://www.loc.gov/mads/rdf/v1#')


def getGraph(url, format, host):
    g = Graph()
    try:
        if host == 'geo':
            data = geo.get(url, timeout=30, headers=headers)
        elif host == 'ft':
            data = ft.get(url, timeout=30, headers=headers)
        elif host == 'lc':
            data = lc.get(url, timeout=30, headers=headers)
        data = data.text
        graph = g.parse(data=data, format=format)
    except requests.exceptions.Timeout:
        graph = None
    return graph


def getlabel(g):
    for s, p, o in g.triples((None, gn.name, None)):
        name = o
        return(name)


def convertLinks(type, url):
    if type == 'sws':
        url = url.replace('s://sws.', '://www.')
        url = url+'about.rdf'
        print(url)
        return url
    else:
        url = url.replace('://www.', 's://sws.')
        url = url.replace('about.rdf', '')
        return url


def findParent(parent):
    url = convertLinks('sws', parent)
    graph = getGraph(url, 'xml', 'geo')
    name = getlabel(graph)
    return name


def addFullName():
    name0 = result.get('name0')
    name1 = result.get('name1')
    name2 = result.get('name2')
    if name1 and name2:
        fullName = name0+', '+name1+', '+name2
        result['fullName'] = fullName
    elif name2:
        fullName = name0+', '+name2
        result['fullName'] = fullName
    elif name1:
        fullName = name0+', '+name1
        result['fullName'] = fullName
    else:
        pass


def getParents(parents):
    if parents == 'yes':
        if result.get('geoname0'):
            geo = result.get('geoname0')
            # Get linked data for geonames
            gLink = geo+'/about.rdf'
            mgraph = getGraph(gLink, 'xml', 'geo')
            # Find parents
            for s, p, o in mgraph.triples((None, gn.parentADM1, None)):
                parent1 = o
                print(parent1)
                if parent1:
                    name1 = findParent(parent1)
                    result['geoname1'] = parent1
                    result['name1'] = name1
            for s, p, o in mgraph.triples((None, gn.parentCountry, None)):
                parent2 = o
                print(parent2)
                if parent2:
                    name2 = findParent(parent2)
                    result['geoname2'] = parent2
                    result['name2'] = name2
            # Create full name
            addFullName()
        all_items.append(result)
    else:
        all_items.append(result)


df = pd.read_csv(filename)
searchTerms = df.geosubjects2.str.split('|')
search = searchTerms.explode()
searchTerms = list(search.unique())
for count, term in enumerate(searchTerms):
    if pd.isna(term):
        searchTerms.pop(count)
searchTerms = searchTerms[:500]
print(len(searchTerms))
print(searchTerms)

all_items = []
for count, searchTerm in enumerate(searchTerms):
    # Get results from FAST API
    print(count, searchTerm)
    searchTerm.rstrip('.')
    result = {'term': searchTerm}
    url = labelBase+searchTerm
    data = lc.get(url, timeout=30, headers=headers)
    foundName = data.ok
    newURL = data.url
    if foundName:
        newURL = data.url
        newURL = newURL.replace('.html', '')
        print(newURL)
        graph = getGraph(newURL+'.nt', 'nt', 'lc')
        if graph is None:
            continue
        for s, p, o in graph.triples((None, mads.hasCloseExternalAuthority,
                                      None)):
            if 'http://id.worldcat.org/fast/' in o:
                if result.get('geoname0') is None:
                    # Get linked data of FAST results
                    fastId = o
                    fLink = fastId+ext
                    print(fLink)
                    graph = getGraph(fLink, 'xml', 'ft')
                    if graph is None:
                        continue
                    nameAuth = URIRef(newURL)
                    if (None, schema.sameAs, nameAuth) in graph:
                        result['nameAuth'] = nameAuth
                        result['fast'] = fastId
                        objects = graph.objects(subject=None,
                                                predicate=schema.sameAs)
                        for object in objects:
                            print(object)
                            if 'http://www.geonames.org/' in object:
                                print('hooray')
                                label = graph.value(subject=object,
                                                    predicate=rdfs.label)
                                result['geoname0'] = object
                                result['name0'] = label
                                print(object, label)
                            else:
                                pass
                    else:
                        pass

    # Get parent info from geonames
    getParents(parents)

df_1 = pd.DataFrame.from_dict(all_items)
print(df_1.columns)
print(df_1.head)
dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
newFile = 'geonamesFound_'+dt+'.csv'
df_1.to_csv(newFile, header='column_names', index=False)
