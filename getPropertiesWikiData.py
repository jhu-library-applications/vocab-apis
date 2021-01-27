import pandas as pd
import argparse
import requests
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')

args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

# Some config for requests.
headers = {'User-Agent': 'Custom user agent'}
wd = requests.Session()

dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

df_1 = pd.read_csv(filename, header=0)
id_list = df_1.ID.to_list()


wiki = 'https://www.wikidata.org/wiki/Special:EntityData/'
ext = '.json'


wiki = ('https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&\
        assert=anon&uselang=user&errorformat=plaintext&errorlang=uselang&ids=')
ext = '&redirects=yes&props=claims&languages=en&languagefallback=1&utf8=1'

properties = ['P527', 'P279', 'P361']
all_items = []
for id in id_list:
    newInfo = {}
    newInfo['id'] = id
    link = wiki+id+ext
    data = wd.get(link, timeout=30, headers=headers).json()
    entity = data.get('entities')
    item = entity.get(id)
    claims = item.get('claims')
    for claim in claims:
        print(claim)
        if claim in properties:
            claimInfo = claims.get(claim)
            for item in claimInfo:
                mainsnak = item.get('mainsnak')
                datavalue = mainsnak.get('datavalue')
                value = datavalue.get('value')
                id = value.get('id')
                print(claim, id)
                newInfo[claim] = id
    all_items.append(newInfo)


df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
df.to_csv('wikidata_'+dt+'.csv', header='column_names', index=False)
