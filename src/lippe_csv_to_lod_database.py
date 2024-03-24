# this script is made based on the instructions given in this
# website: https://stackoverflow.com/questions/43524943/creating-rdf-file-using-csv-file-as-input/61445967#61445967
# this script converts a csv file to RDF

import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import os # to work with paths

######## 1. DEFINE PATHS TO DATA ###########################
## enter path to repository:
data_directory = os.path.abspath(os.path.join('..', 'data'))
data_raw_directory = os.path.join(data_directory, 'raw')
data_processed_directory = os.path.join(data_directory, 'processed')
data_temp_directory = os.path.join(data_directory, 'temp')

######## 2. READ RAW CSV ####################################################################
df_raw = pd.read_csv(f'{data_raw_directory}/lippe-archival-pages-transcriptions_test.csv', sep=',', quotechar='"')
# print(df_raw.head())
# print(df_raw.columns)
# print(df_raw.info())

######## 3. CONVERT DATA TYPES AND FILL IN EMPTY VALUES ####################################################################
# note: only expected data type is string
df_columns = df_raw.columns
for column in df_columns:
    dataType = df_raw.dtypes[column]
    df_raw[column] = df_raw[column].fillna('null')
    df_raw[column] = df_raw[column].astype(str)

df = df_raw.reset_index(drop=True)
# print(df.head())
# print(df.columns)
# print(df.info())

# # ######## 3. DEFINE A GRAPH 'G' AND NAMESPACES ###############################################
g = Graph()
lippeSchema = Namespace('https://iisg.amsterdam/vocab/data/lippe/')

######## 4. CREATE THE TRIPLES AND ADD THEM TO GRAPH 'G' ####################################
# following examples from tutorial: https://stackoverflow.com/questions/43524943/creating-rdf-file-using-csv-file-as-input/61445967#61445967
# for index, row in df.iterrows():
# # #     g.add((URIRef(ppl+row['Name']), RDF.type, FOAF.Person))
# # #     g.add((URIRef(ppl+row['Name']), URIRef(schema+'name'), Literal(row['Name'], datatype=XSD.string) ))
# # #     g.add((URIRef(ppl+row['Name']), FOAF.age, Literal(row['Age'], datatype=XSD.integer) ))
# # #     g.add((URIRef(ppl+row['Name']), URIRef(schema+'address'), Literal(row['Address'], datatype=XSD.string) ))
# # #     g.add((URIRef(loc+urllib.parse.quote(row['Address'])), URIRef(schema+'name'), Literal(row['Address'], datatype=XSD.string) ))

for index, row in df.iterrows():
    # add image Id
    g.add((URIRef(lippeSchema+row['file_id']), URIRef(lippeSchema+'id'), Literal(row['file_id'], datatype=XSD.string)))
    
    # # add signatur
    # g.add((URIRef(lippeSchema+row['signatur']), URIRef(lippeSchema+'/signatur'), Literal(row['signatur'], datatype=XSD.string)))

    # # add transcript
    # g.add((URIRef(lippeSchema+row['content']), URIRef(lippeSchema+'/transcribedAs'), Literal(row['content'], datatype=XSD.string)))

    # # add url to the scan: subject (it's what I am describing: the image), predicate (it's the property url in the namespace schema.org), object (it's the url to the image)
    # # g.add((URIRef(iisgvoc+row['imageId']), URIRef(iisgvoc+'vocab/cv'), URIRef(row['imageUrl'])))
    # g.add((URIRef(iisgvoc+row['file_Id_old']), URIRef(iisgvoc+'vocab/cv'), URIRef(row['page_scan_url'])))

# # # # Check the results
print(g.serialize(format='nt', encoding='utf-8'))

# # # # Save the results to disk
# # # g.serialize('mycsv2rdf.ttl',format='turtle') ##from tutorial
# # # g.serialize(f'{data_processed_directory}test20.nt',format='ntriples', encoding='UTF-8')
# # g.serialize(f'{data_processed_directory}csvtordf_ziegler_folia_interpretations_v1.nt',format='turtle', encoding='UTF-8')
# # print("done")
