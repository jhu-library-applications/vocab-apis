import requests
import pandas as pd
import argparse
import re
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')

args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

df_1 = pd.read_csv(filename, header=0)

# FAST Converter
# Convert LSCH Subject Headings to FAST Subject Headings
url = "https://fast.oclc.org/lcsh2fast/Lcsh2FastSingle"

all_items = []
for count, row in df_1.iterrows():
    heading = row['heading']
    heading = heading.strip()
    textbox = heading
    response = requests.post(url, data={"textbox": textbox}).json()
    resultData = response.get('resultData')
    resultData = resultData.splitlines()
    for result in resultData:
        if result:
            newDict = {'heading': heading}
            result = re.split(r'\$\w', result)
            result = [s.strip() for s in result]
            newDict['marc'] = result[0]
            fastHeading = "--".join(result[1:-2])
            newDict['fastHeading'] = fastHeading
            fastID = result[-1].strip('(OCoLC)')
            newDict['fastID'] = fastID
            plainID = re.sub(r'fst0+', '', fastID)
            fastURI = 'http://id.worldcat.org/fast/'+plainID
            newDict['fastURI'] = fastURI
            print(newDict)
            all_items.append(newDict)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
df.to_csv('FASTConvertResults_'+dt+'.csv', index=False)
