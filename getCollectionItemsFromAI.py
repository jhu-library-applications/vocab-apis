from internetarchive import search_items, get_item
import pandas as pd
from datetime import datetime

collection_name = 'example'

all_items = []
for item in search_items('collection:'+collection_name).iter_as_items():
    identifier = item.identifier
    print(identifier)
    item = get_item(identifier)
    item_metadata = item.item_metadata['metadata']
    all_items.append(item_metadata)

df = pd.DataFrame.from_dict(all_items)
print(df.columns)
print(df.head)
dt = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
df.to_csv('internetArchiveMetadata_'+dt+'.csv', index=False)