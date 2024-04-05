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
# make sure that the 'wohin_WHG_identifier' is not a float (just removing the .0 here)
df_raw['wohin_WHG_identifier'] = df_raw['wohin_WHG_identifier'].str.replace('.0', '')

df = df_raw.reset_index(drop=True)
# print(df.head())
# print(df.columns)
# print(df.info(verbose=True))
# print(df['wohin_WHG_identifier'].value_counts())

######### 4. CLEAN AND CREATE SOME IMPORTANT COLUMNS #################
# create column for person name
df['person_name'] = df['Namen'] + ' ' + df['Vornamen']
# replace 'null' with ''
df['person_name'] = df['person_name'].str.replace(' null', '')
# create "person name redundant" to solve the problem that, some times, the last name is the name and viceversa (example: Hermann Sieckmann is in inverse columns, which will result in Sieckmann Hermann; to facilitate search, we add the name again, thus: Sieckmann Hermann Sieckmann)
df['person_name_redundant'] = df['person_name'] + ' ' + df['Namen']
# because we are converting all the database columns to triples in the namespace of a lippe vocabulary, and each row represents a "working event" of a person (in a certain period, place, factory, etc.),
# we create unique Ids for those work events (i.e., for each row). It's important to keep in mind that there are no Ids for a person in the source data, only strings.. We use uuid for those work events
# unique id created using uuid library: uuid(4) for random Id
df['work_event_uuid'] = [uuid.uuid4() for _ in range(len(df.index))]
# convert the uuid to string
df['work_event_uuid'] = df['work_event_uuid'].astype(str)

# make a copy of the dataframe
df_database = df.reset_index(drop=True).copy()
# print(df_database.head())
# print(df_database.info(verbose=True))

######## 4. DEFINE A GRAPH 'G' AND NAMESPACES ###############################################
g = Graph()
sdo = Namespace('https://schema.org/')
# iisgvoc = Namespace('https://iisg.amsterdam/vocab/')
lippevoc = Namespace('https://iisg.amsterdam/vocab/data/lippe/')
# opengis = Namespace('http://www.opengis.net/ont/geosparql')

######## 8. CREATE THE TRIPLES AND ADD THEM TO GRAPH 'G' ####################################
# check column names as a variable
# df_database_columns = df_database.columns
# print(df_database_columns)
# decide which columns will be aligned with the other dataset(s)
columns_align = ['file_Id', 'Signatur', 'work_event_uuid', 'wohin_WHG_identifier']
columns_not_align = ['row', 'ID', 'original_source', 'original_ID',
       'inventory_number', 'Folio_original', 'Folio', 'Jahr', 'Bezirk',
       'Namen', 'Vornamen', 'Amt', 'Ortschaft', 'Kataster', 'Beziehung',
       'Colon', 'Kotter', 'Enrolliert', 'Alter', 'Wohin', 'wohin_matches', 'wohin_geowkt',
       'wohin_latitude', 'wohin_longitude', 'Nachste_Stadt', 'Land',
       'Wie_lange', 'Datum', 'Fabrik', 'Arbeit', 'Arbeit_q', 'Betragen',
       'Gruppe', 'Grosse', 'Grosse_q', 'Stellung', 'Notiz',
       'person_name_redundant']

# make first the triples for the columns to align
for column_name in columns_align:
    for index, row in df.iterrows():
        # create the triples for the main types
        # type File (this is the scanned page)
        g.add((URIRef(lippevoc+'File/'+row['file_Id']), RDF.type, sdo.ImageObject))
        # type MoveAction (used for the work event, since each row represents a migration event of one worker)
        g.add((URIRef(lippevoc+'WorkEvent/'+row['work_event_uuid']), RDF.type, sdo.MoveAction))
        # create the triples for the properties
        # create a triple for the relation between the work event and the work event Id
        g.add((URIRef(lippevoc+'WorkEvent/'+row['work_event_uuid']), URIRef(sdo.identifier), Literal(row['work_event_uuid'])))
        # create a triple for the relation between the file (scan) and the "work event"
        g.add((URIRef(lippevoc+'File/'+row['file_Id']), URIRef(sdo.mentions), URIRef(lippevoc+'WorkEvent/'+row['work_event_uuid'])))
        # create a triple for the relation between the "work event" and the place of destination, using the standard identifier from the World Historical Gazetteer (WHG)
        g.add((URIRef(lippevoc+'WorkEvent/'+row['work_event_uuid']), URIRef(sdo.location), URIRef(lippevoc+'Place/'+row['wohin_WHG_identifier'])))
        

# make triples for all the other columns using the column name
for column_name in columns_not_align:
    for index, row in df.iterrows():
        # create triple for the other columns
        g.add((URIRef(lippevoc+'WorkEvent/'+row['work_event_uuid']), URIRef(lippevoc+column_name), Literal(row[column_name], datatype=XSD.string)))
    
# # Check the results
# print(g.serialize(format='nt', encoding='utf-8'))

# # Save the results to disk
# g.serialize('mycsv2rdf.ttl',format='turtle')
# g.serialize(f'{data_processed_directory}test20.nt',format='ntriples', encoding='UTF-8')
g.serialize(f'{data_processed_directory}/lippe_brickmakers_database_as_lod.nt',format='turtle', encoding='UTF-8')
print("done")