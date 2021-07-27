import pandas as pd
import argparse
from datetime import datetime
import requests
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')


df_1 = pd.read_csv(filename, header=0, dtype={'viaf_id':'object'})

headers = {'User-Agent': 'Custom user agent'}
baseURL = 'http://www.viaf.org/viaf/'
lc_base = 'http://id.loc.gov/authorities/names/'
json = '/justlinks.json'

name_fields = ['100', '110', '111', '147']
titles = {'f': 'date', 'h': 'medium', 'k': 'form', 'l': 'lang', 'm': 'medium',
          'n': 'num', 'o': 'arrange', 'p': 'part', 'r': 'key', 's': 'version',
          't': 'title'}
personal = {'type': 'personal', 'a': 'personal_name', 'b': 'numeration',
            'c': 'titles', 'd': 'dates', 'e': 'relator', 'j': 'attribution',
            'q': 'fuller_form'}
personal.update(titles)
corporate = {'type': 'corporate', 'a': 'corporate', 'b': 'subordinate',
             'c': 'location', 'e': 'realtor', 'd': 'dates', 'g': 'misc',
             'n': 'number', 'q': 'name of meeting'}
corporate.update(titles)
event = {'type': 'event', 'a': 'event', 'c': 'location', 'd': 'date',
         'g': 'misc'}
event.update(titles)
facetDict = {'100': personal, '110': corporate, '111': corporate,
             '147': event}


def findfacet(marctags):
    facet = facetDict.get(marctags)
    return facet


def convertSubfield(subfield, facet):
    subfield = facet.get(subfield)
    return subfield


all_items = []
for count, row in df_1.iterrows():
    row = row
    link = row['viaf_id']
    print(link)
    if pd.notna(link):
        links = requests.get(baseURL+link+json, timeout=2, headers=headers).json()
        if isinstance(links, dict):
            lc_id = links.get('LC')
            if lc_id:
                lc_id = lc_id[0]
                link = lc_base+lc_id
                row['lc_link'] = link
                print(link)
                data = requests.get(link+'.marcxml.xml', timeout=2, headers=headers)
                data = data.text
                root = ET.fromstring(data)
                for child in root:
                    fields = child.attrib
                    marctags = fields.get('tag')
                    if marctags in name_fields:
                        facet = findfacet(marctags)
                        row['facet'] = facet.get('type')
                        for c in child:
                            component = c.text
                            component = component.rstrip(',')
                            subdict = c.attrib
                            subfield = subdict.get('code')
                            subfield = convertSubfield(subfield, facet)
                            if row.get(subfield) is None:
                                row[subfield] = component
                            else:
                                oldComponent = row.get(subfield)
                                newComponent = oldComponent+'|'+component
                                row[subfield] = newComponent
    all_items.append(row)


df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
df.to_csv('_'+dt+'.csv', header='column_names', index=False)
