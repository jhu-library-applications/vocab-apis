# vocab-apis

## API resources

Here's a quick summary of the endpoints I tend to use, and some of their documentation.

| vocabulary                               | endpoint                                     | API Documentation                                                                                                     |
|------------------------------------------|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| AAT                                      | http://vocab.getty.edu/sparql                | [Getty Vocabularies: SPARQL endpoint](http://vocab.getty.edu/)                                                        |
| Europeana                                | https://www.europeana.eu/api/                | [Europeana Record API](https://pro.europeana.eu/page/record)                                                          |
| FAST (read)                              | http://id.worldcat.org/fast                  | [FAST Linked Data API](https://www.oclc.org/developer/develop/web-services/fast-api/linked-data.en.html)              |
| FAST (Autosuggest)                       | http://fast.oclc.org/searchfast/fastsuggest  | [FAST Linked Data API](https://www.oclc.org/developer/develop/web-services/fast-api/linked-data.en.html)              |
| FAST (SRUSearch)                         | http://id.worldcat.org/fast/search           | [FAST Linked Data API](https://www.oclc.org/developer/develop/web-services/fast-api/linked-data.en.html)              |
| FAST (search, actually the best results) | http://experimental.worldcat.org/fast/search | not documented as an official endpoint idk?                                                                           |
| GeoNames                                 | https://sws.geonames.org/                    | [GeoNames Web Services Documentation](http://www.geonames.org/export/)                                                |
| Internet Archive                         | http://archive.org/metadata/                 | [Internet Archive Developer Portal](https://archive.org/services/docs/api/)                                           |
| Library of Congress Authorities          | http://id.loc.gov/authorities/               | [LOC Linked Data Service: Technical Center](https://id.loc.gov/techcenter/)                                           |
| VIAF                                     | http://www.viaf.org/viaf/                    | [VIAF Authority Cluster Resource](https://www.oclc.org/developer/develop/web-services/viaf/authority-cluster.en.html) |



## Python resources

| python library        | main purpose                               | docs                                                                                      |
|-----------------------|--------------------------------------------|-------------------------------------------------------------------------------------------|
| bs4                   | Parses  XML                                | https://www.crummy.com/software/BeautifulSoup/bs4/doc/                                    |
| pandas                | Everything tabular data                    | https://pandas.pydata.org/docs/user_guide/index.html                                      |
| requests              | Sends HTTP requests                        | https://docs.python-requests.org/en/master/                                               |
| rdflib                | Parses RDF/XML, N3, NTriples, Turtle, etc. | https://rdflib.readthedocs.io/en/stable/index.html                                        |
| xml.etree.ElementTree | Parses XML                                 | https://docs.python.org/3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree |



## Scripts

### searchForStringMatch

#### [authorizeFASTAndLCAuthorityHeadings.py](searchForStringMatch/authorizeFASTAndLCAuthorityHeadings.py)
**Starting data:** A spreadsheet that searches a string heading in LCNAF and FAST and produces a URI if there is an exact match.<br>
**APIs:** Library of Congress Authorities, FAST (SRUSearch)

Confirms the heading is authorized by retrieving the URIs and label from the APIs.

#### [searchForStringMatchInFAST.py](searchForStringMatch/searchForStringMatchInFAST.py)
**Starting data:** A spreadsheet with strings of possible FAST headings.<br>
**APIs:** FAST (Autosuggest), FAST (SRUSearch)

Finds exact and close matches to FAST subject headings.

### getItemMetadata

#### [getEuropeanaData.py](getItemMetadata/getEuropeanaData.py)
**Starting data**: Europeana item identifier as variable `item`.<br>
**APIs**: Europeana

Downloads item record in JSON-LD, and saves as file "query.json."

#### [getItemMetadataFromInternetArchive.py](getItemMetadata/getItemMetadataFromInternetArchive.py)
**Starting data**: Internet Archive item identifier as variable `internet_id`.<br>
**APIs**: Internet Archive

Downloads item record in JSON and saves metadata in CSV.

#### [getPropertiesWikiData.py](getItemMetadata/getPropertiesWikiData.py)
**Starting data**: Entity id from WikiData.<br>
**APIs**: Wikidata

Finds properties of entity and saves in CSV.


### Convert

#### [convertFASTAndVIAFIdentifiersToURI.py](convert/convertFASTAndVIAFIdentifiersToURI.py)
**Starting data**: A spreadsheet with FAST or VIAF identifiers.<br>
**APIs:** none

Converts FAST and VIAF identifiers to URIs.

#### [convertLCNAFToGeonames.py](convert/convertLCNAFToGeonames.py)
**Starting data**: A spreadsheet with geographic headers (from FAST or LCNAF).<br>
**APIs**: FAST (read), Library of Congress Authorities, GeoNames

Convert geographic names from LCNAF to geonames identifiers. Example: Baltimore County (Md.) n79018713 is converted to Baltimore County https://www.geonames.org/4347790. It also builds full hierarchical name: Baltimore County, Maryland, United States from GeoNames.

#### [convertLSCHToFAST.py](convert/convertLSCHToFAST.py)
**Starting data**: A spreadsheet with Library of Congress Subject Headings.<br>
**APIs**: FAST (read), Library of Congress Authorities

Converts LCSH to one or more FAST headings.

#### [convertYearsToFASTDecades.py](convert/convertYearsToFASTDecades.py)
**Starting data**: A spreadsheet with year dates from 1800s onwards.<br>
**APIs**: none

Converts years into written out decades as given in FAST.

### getAdditionalPropertiesFromIdentifiers

#### [getAlternativeIdentifiersFromFAST.py](getAdditionalPropertiesFromIdentifier/getAlternativeIdentifiersFromFAST.py)
**Starting data**: A spreadsheet with FAST identifiers.<br>
**APIs**: FAST (read)

Retrieves alternative identifiers from other authorities (VIAF, GeoNames, LCSH, etc.) given in FAST records.

#### [getFacetForTerms_FAST.py](getAdditionalPropertiesFromIdentifier/getFacetForTerms_FAST.py)
**Starting data**: A spreadsheet with FAST identifiers.<br>
**APIs**: FAST (read)

Converts the FAST identifier to a link, gets the rdf.xml record, and extracts the facet information (topical, geographical, corporate name, meeting or event, personal name, uniform title, form, period).

#### [getFacetForTerms_VIAF.py](getAdditionalPropertiesFromIdentifier/getFacetForTerms_VIAF.py)
**Starting data**: A spreadsheet of VIAF URIs formatted like https://viaf.org/viaf/149920363. The script won't work if there is an ending dash (ex: https://viaf.org/viaf/149920363/).<br>
**APIs**: VIAF, Library of Congress Authorities

Takes a list of VIAF URIs from a spreadsheet, finds the LCNAF authority record, and extracts the facet information from the rdf.xml record.

#### [getLabelFromURI.py](getAdditionalPropertiesFromIdentifier/getLabelFromURI.py)
**Starting data**: A spreadsheet with URIs from the FAST, Library of Congress Authorities, GeoNames, VIAF, or AAT vocabularies.<br>
**APIs:** FAST (read), Library of Congress Authorities, GeoNames, VIAF, AAT

Retrieves the authorized heading or label from the correct vocabulary using the URIs.

#### [getNameComponents_VIAF.py](getAdditionalPropertiesFromIdentifier/getNameComponents_VIAF.py)
**Starting data**: A spreadsheet of VIAF URIs formatted like https://viaf.org/viaf/149920363. The script won't work if there is an ending dash (ex: https://viaf.org/viaf/149920363/).<br>
**APIs:** VIAF, Library of Congress Authorities

Takes a list of VIAF URIs from a spreadsheet, finds the LCNAF authority record, and extracts the name components from the .marcxml.xml record.

### Get URIs from authorized headings or labels

#### [getURIsFromLabel_LCAuthoritiesAndVIAF.py](getURIsFromLabel/getURIsFromLabel_LCAuthoritiesAndVIAF.py)
**Starting data**: A spreadsheet with Library of Congress Names.<br>
**APIs**: Library of Congress Authorities   

Retrieves the LCNAF URI for the searched named and grabbed alternative identifiers from other authorities (FAST and LC Authorities (LCNAF, LCSH, LCGFT))  in the records.

#### [getURIsFromLabel_AAT.py](getURIsFromLabel/getURIsFromLabel_AAT.py)
**Starting data**: String in variable `label_search`.<br>
**APIs**: AAT

Retrieves AAT URI by searching for the label in the API.

#### [getURIsFromLabel_FAST.py](getURIsFromLabel/getURIsFromLabel_FAST.py)
**Starting data**: A spreadsheet with FAST string headings.<br>
**APIs**: FAST (read), FAST (search)

Retrieves FAST URIs by searching for the heading in the API.