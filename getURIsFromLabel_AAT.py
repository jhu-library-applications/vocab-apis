import requests
import json

label_search = '"postcards"'

url = 'http://vocab.getty.edu/sparql'
query = """
select ?Subject ?Term {
    ?Subject a skos:Concept; rdfs:label """+label_search+"""@en;
        gvp:prefLabelGVP [xl:literalForm ?Term].}
"""

r = requests.get(url, params={'format': 'json', 'query': query})
data = r.json()
results = data.get('results')
bindings = results.get('bindings')
info = bindings[0]
subject = info.get('Subject')
uri = subject.get('value')
term = info.get('Term')
value = term.get('value')
print(uri, value)
with open('query.json', 'w') as json_file:
    json.dump(data, json_file)
