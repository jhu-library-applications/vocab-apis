import requests
import esecrets
import json

wskey = esecrets.API_key
item = '15514/BI_8770_11'

baseURL = 'https://www.europeana.eu/api/v2/record/'
ext = '.json-ld'

url = baseURL+item+ext+'?wskey='+wskey

r = requests.get(url)

data = r.json()

with open('query.json', 'w') as json_file:
    json.dump(data, json_file)
