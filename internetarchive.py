import requests
import argparse
import pandas as pd
from datetime import datetime

baseURL = 'http://archive.org/metadata/'

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='Enter filename with csv.')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

df = pd.read_csv(filename)

all_items = []
for index, row in df.iterrows():
    print(index)
    internet_id = row.get('internet_id')
    url = baseURL+internet_id
    data = requests.get(url, timeout=30).json()
    metadata = data.get('metadata')
    little_dict = {}
    if metadata:
        for key, value in metadata.items():
            little_dict[key] = value
    else:
        print(internet_id)
    all_items.append(little_dict)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
df.to_csv('internetArchiveMetadata_'+dt+'.csv', index=False)
