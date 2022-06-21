import requests
import pandas as pd
import argparse
from datetime import datetime
from bs4 import BeautifulSoup as Soup
from rdflib import Namespace

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-c', '--column')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.column:
    columnName = args.column
else:
    columnName = input('name of column: ')

dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

df_1 = pd.read_csv(filename, header=0)
searchTerms = df_1[columnName].to_list()


# Configuration for requests.
headers = {'User-Agent': 'Custom user agent'}
ft = requests.Session()
baseURL = 'http://id.worldcat.org/fast/'
fastURL = 'http://experimental.worldcat.org/fast/search?query=cql.any+all+%22'
fastPara = '%22&httpAccept=application/xml&sortKeys=usage&maximumRecords=10&recordSchema=info:srw/schema/1/rdf-v2.0'
mads = Namespace('http://www.loc.gov/mads/rdf/v1#')


all_items = []
for label in searchTerms:
    result = {}
    label = label.strip()
    data = ft.get(fastURL+label+fastPara)
    data = data.content
    data = data.decode('utf-8')
    soup = Soup(data, features='lxml')
    records = soup.find('records')
    for record in records:
        if bool(result) is False:
            identifier = record.find('dct:identifier')
            identifier = identifier.string
            authLabel = record.find('skos:preflabel')
            authLabel = authLabel.string
            if authLabel == label:
                print(authLabel)
                result['authLabel'] = authLabel
                result['authURI'] = baseURL+identifier
    result['original_label'] = label
    all_items.append(result)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
df.to_csv('authorizedHeadingResults_'+dt+'.csv', index=False)
