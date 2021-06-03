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


df_1 = pd.read_csv(filename, header=0)
viaf_ids = df_1.viaf_id.to_list()

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
for link in viaf_ids:
    tinyDict = {}
    tinyDict['viaf_id'] = link
    print(link)
    if pd.notna(link):
        links = requests.get(link+json, timeout=30, headers=headers).json()
        if isinstance(links, dict):
            lc_id = links.get('LC')
            if lc_id:
                lc_id = lc_id[0]
                link = lc_base+lc_id
                tinyDict['lc_link'] = link
                print(link)
                data = requests.get(link+'.marcxml.xml', timeout=30, headers=headers)
                data = data.text
                root = ET.fromstring(data)
                for child in root:
                    fields = child.attrib
                    marctags = fields.get('tag')
                    if marctags in name_fields:
                        facet = findfacet(marctags)
                        tinyDict['facet'] = facet.get('type')
                        for c in child:
                            component = c.text
                            component = component.rstrip(',')
                            subdict = c.attrib
                            subfield = subdict.get('code')
                            subfield = convertSubfield(subfield, facet)
                            if tinyDict.get(subfield) is None:
                                tinyDict[subfield] = component
                            else:
                                oldComponent = tinyDict.get(subfield)
                                newComponent = oldComponent+'|'+component
                                tinyDict[subfield] = newComponent
    all_items.append(tinyDict)


df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
df.to_csv('nameComponents_'+dt+'.csv', header='column_names', index=False)
