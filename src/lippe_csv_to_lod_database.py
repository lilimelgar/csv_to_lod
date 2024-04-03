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
df_raw = pd.read_csv(f'{data_raw_directory}/lippe_brickmakers_database.csv', sep=',', quotechar='"', low_memory=False)
# print(df_raw.head())
# print(df_raw.columns)
# # print(df_raw.info())
# # print(df_raw.iloc[[1]])

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
# opengis = Namespace('http://www.opengis.net/ont/geosparql')

######## 8. CREATE THE TRIPLES AND ADD THEM TO GRAPH 'G' ####################################
# because we are converting all the database columns to triples in the namespace of a lippe vocabulary, and each row represents a "working event" of a person (in a certain period, place, factory, etc.),
# we create unique Ids for those events (i.e., for each row). It's important to keep in mind that there are no Ids for a person in the source data, only strings.
# unique id created using uuid library: uuid(4) for random Id
df['work_event_uuid'] = [uuid.uuid4() for _ in range(len(df.index))]
# print(df.head())
# make a copy of the dataframe
df_database = df.reset_index(drop=True).copy()
# capture column names as a variable
df_database_columns = df_database.columns
# print(df_database_columns)

for column_name in df_database_columns:
    for index, row in df.iterrows():
        # create triple for the other columns
        g.add((URIRef(lippevoc+'work_event_id/'+row['row']), URIRef(lippevoc+column_name), Literal(row[column_name], datatype=XSD.string)))
    
# # Check the results
# print(g.serialize(format='nt', encoding='utf-8'))

# # Save the results to disk
# g.serialize('mycsv2rdf.ttl',format='turtle')
# g.serialize(f'{data_processed_directory}test20.nt',format='ntriples', encoding='UTF-8')
g.serialize(f'{data_processed_directory}/lippe_brickmakers_database_as_LOD.nt',format='turtle', encoding='UTF-8')
print("done")