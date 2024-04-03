# This script is made based on the instructions given in this
# tutorial by Richard Zijdeman: https://stackoverflow.com/questions/43524943/creating-rdf-file-using-csv-file-as-input/61445967#61445967
# this script converts a csv file to RDF using rdflib library
# written by Liliana Melgar, also available in this Github repository: https://github.com/lilimelgar/csv_to_lod. 
# Latest update: April 2, 2024.

import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import os # to work with paths
import uuid

######## 1. DEFINE PATHS TO DATA ###########################
data_directory = os.path.abspath(os.path.join('..', 'data'))
data_raw_directory = os.path.join(data_directory, 'raw')
data_processed_directory = os.path.join(data_directory, 'processed')
data_temp_directory = os.path.join(data_directory, 'temp')

######## 2. READ RAW CSV ####################################################################
# the file we are converting to LOD is a csv file deposited in Dataverse, where this dataset: https://hdl.handle.net/10622/1RNBFT contains both files (the original csv and the converted lod (output of this script))
df_raw = pd.read_csv(f'{data_raw_directory}/lippe-archival-pages-transcriptions.csv', sep=',', quotechar='"')
# print(df.head())
# # print(df.columns)
# # print(df.info())

######## 3. CONVERT DATA TYPES AND FILL IN EMPTY VALUES ####################################################################
# note: only expected data type is string
df_columns = df_raw.columns
for column in df_columns:
    dataType = df_raw.dtypes[column]
    df_raw[column] = df_raw[column].fillna('null')
    df_raw[column] = df_raw[column].astype(str)

df = df_raw.reset_index(drop=True)
# print(df.head())
# # print(df.columns)
# print(df.info(verbose=True))

######## 4. DEFINE A GRAPH 'G' AND NAMESPACES ###############################################
g = Graph()
sdo = Namespace('https://schema.org/')
# iisgvoc = Namespace('https://iisg.amsterdam/vocab/')
lippevoc = Namespace('https://iisg.amsterdam/vocab/data/lippe/')
schema = Namespace('https://schema.org/')
# opengis = Namespace('http://www.opengis.net/ont/geosparql')

######## 5. CREATE THE TRIPLES AND ADD THEM TO GRAPH 'G' ####################################
for index, row in df.iterrows():
    # create a triple for the image/scan Id
    g.add((URIRef(lippevoc+row['file_Id']), URIRef(lippevoc+'file_Id'), Literal(row['file_Id'], datatype=XSD.string)))
    # create a triple for the "signatur"
    g.add((URIRef(lippevoc+row['file_Id']), URIRef(lippevoc+'is_part_of'), URIRef(lippevoc+row['signatur'])))
    # create a triple for the "signatur" to connect to the page scans
    g.add((URIRef(lippevoc+row['signatur']), URIRef(lippevoc+'has_file'), URIRef(lippevoc+row['file_Id'])))
    # create a triple for the "signatur" as literal
    g.add((URIRef(lippevoc+row['signatur']), URIRef(lippevoc+'has_signatur'), Literal(row['signatur'])))
    # create a triple for the "inventory number"
    g.add((URIRef(lippevoc+row['signatur']), URIRef(lippevoc+'has_inventory_number'), Literal(row['inventory_number'])))
    # create a triple for the string of the transcription
    g.add((URIRef(lippevoc+row['file_Id']), URIRef(lippevoc+'transcribedAs'), Literal(row['transcription'], datatype=XSD.string)))
    # add url to the scan: subject (it's what I am describing: the image), predicate (it's the property url in the namespace schema.org), object (it's the url to the image)
    g.add((URIRef(lippevoc+row['file_Id']), URIRef(lippevoc+'page_scan_url'), URIRef(row['page_scan_url'])))

# # Check the results
# print(g.serialize(format='nt', encoding='utf-8'))

# # Save the results to disk
# g.serialize('mycsv2rdf.ttl',format='turtle') ##from tutorial
# g.serialize(f'{data_processed_directory}test20.nt',format='ntriples', encoding='UTF-8')
g.serialize(f'{data_processed_directory}/lippe-archival-pages-transcriptions_as_lod.nt',format='turtle', encoding='UTF-8')
print("done")
