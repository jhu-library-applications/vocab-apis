import pandas as pd
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')

args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

aat = 'someurl'
fast = 'someurl'
geonames = 'someurl'
lcnaf = 'someurl'
lcgft = 'someurl'
viaf = 'someurl'

taxonomies = {'corporate_body': ['lcnaf', 'viaf'],
              'family': ['lcnaf', 'viaf'],
              'geo_location': ['fast', 'geonames'],
              'genre': ['aat', 'lcgft'],
              'person': ['lcnaf', 'viaf'],
              'subject': ['fast']
              }

df = pd.read_csv(filename, header=0)
for count, row in df.iterrows():
    name = row.get('name')
    taxonomy = row.get('taxonomy')
    vocabularies = taxonomies.get(taxonomy)
    for vocabulary in vocabularies:
        if vocabulary == 'aat':
            # Get URI from AAT
        elif vocabulary == 'fast':
            # Get URI from FAST and facet
            # Check for geoname alt id
        elif vocabulary == 'geonames':
            # Get geoname URI
        elif vocabulary == 'lcnaf':
            # Get URI from LCNAF
            # Get alt VIAF ID
            # Get name co
        elif vocabulary == 'lcgft':
            # Get URI
        elif vocabulary == 'viaf':
            #
        else:
            pass