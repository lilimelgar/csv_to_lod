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
data_raw_directory = os.path.join(data_directory, 'raw') # this directory contains the files as downloaded from Dataverse
data_processed_directory = os.path.join(data_directory, 'processed')
data_temp_directory = os.path.join(data_directory, 'temp')

######## 2. READ RAW CSV ####################################################################
df_raw = pd.read_csv(f'{data_raw_directory}/lippe_brickmakers_database_sample_with_geodata.csv', sep=',', quotechar='"')
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
# however, the wkt values cannot be a string, the null is then replaced with "0.00000 0.00000"
df_raw['wohin_geowkt'] = df_raw['wohin_geowkt'].str.replace('null', 'MULTIPOINT (0.00000 0.00000)')

df = df_raw.reset_index(drop=True)
# print(df.head())
# print(df.columns)
# print(df.info())

######## 5. CREATE SLICE FOR COLUMNS OF INTEREST ####################################################################
# create a slice of the dataframe, with the Wohin-related columns and the person name 
df_wohin_all = df[['Signatur','Namen', 'Vornamen', 'Wohin', 'wohin_WHG_identifier', 'wohin_matches', 'wohin_geowkt', 'wohin_latitude', 'wohin_longitude', 'Fabrik', 'Jahr']].copy()
# convert 'wohin_WHG_identifier' to URL (note: ideally, there will be a proper URI using the API for calling the data for a specific place but, in order to do this, the dataset has to be made public in the World Historical Gazetteer)
df_wohin_all['wohin_WHG_url'] = 'https://whgazetteer.org/places/' + df_wohin_all['wohin_WHG_identifier'] + '/detail'


# # ######## 6. GROUP BY PLACE ID ####################################################################
# create a copy of the dataframe droping unnecessary columns
df_wohin = df_wohin_all[['Wohin', 'wohin_WHG_identifier', 'wohin_WHG_url', 'wohin_matches', 'wohin_geowkt', 'wohin_latitude', 'wohin_longitude', 'Namen', 'Vornamen', 'Fabrik', 'Jahr']].copy()
# group by place/wohin using the local unique placeId
df_wohin_grouped = df_wohin.groupby('wohin_WHG_identifier').agg(lambda x: ';'.join(x.unique()))
# create a copy of the df
df_wohin_per_place = df_wohin_grouped.reset_index(drop=False).copy()
# # test
# print(df_wohin_per_place.head(200))
# df_wohin_per_place.info(verbose=True)

# ######## 7. DEFINE A GRAPH 'G' AND NAMESPACES ###############################################
g = Graph()
sdo = Namespace('https://schema.org/')
iisgvoc = Namespace('https://iisg.amsterdam/vocab/')
lippevoc = Namespace('https://iisg.amsterdam/vocab/data/lippe/')
opengis = Namespace('http://www.opengis.net/ont/geosparql')

# # # ######## 8. CREATE THE TRIPLES AND ADD THEM TO GRAPH 'G' ####################################
for index, row in df_wohin_per_place.iterrows():
    # create the triples for the main types
    # type Place (this is the place of destination "Wohin")
    g.add((URIRef(lippevoc+'Place/'+row['wohin_WHG_identifier']), RDF.type, sdo.Place))
    ###
    # create the triples for the properties
    # create triple for local place_id
    g.add((URIRef(lippevoc+'Place/'+row['wohin_WHG_identifier']), URIRef(sdo.identifier), Literal(row['wohin_WHG_identifier'], datatype=XSD.string)))
    # create triple for place name
    g.add((URIRef(lippevoc+'Place/'+row['wohin_WHG_identifier']), URIRef(sdo.name), Literal(row['Wohin'], datatype=XSD.string)))
    # create triple for name string chosen as a way to represent the place's area --> it is good practice to select a common name to refer to a place in case it changes boundaries over time 
    g.add((URIRef(lippevoc+'Place/'+row['wohin_WHG_identifier']), URIRef(lippevoc+'representedBy'), Literal(row['Wohin'], datatype=XSD.string)))
    # generate a triple for the place's local unique identifier
    g.add((URIRef(lippevoc+'Place/'+row['wohin_WHG_identifier']), URIRef(opengis+'#asWKT'), Literal(row['wohin_geowkt'], datatype=opengis+'#wktLiteral')))
    # generate a triple for the equivalent identifiers recognized via the reconciliation in the World Historical Gazetteer
    g.add((URIRef(lippevoc+'Place/'+row['wohin_WHG_identifier']), URIRef(sdo.sameAs), Literal(row['wohin_matches'], datatype=XSD.string)))
    # generate a triple for the url in the World Historical Gazetteer (note: in order to use the proper API call for a place, the dataset has to be made public, thus, we use the detail page URL for this demo)
    g.add((URIRef(lippevoc+'Place/'+row['wohin_WHG_identifier']), URIRef(sdo.url), URIRef(row['wohin_WHG_url'])))
        
# Check the results
## print(g.serialize(format='nt', encoding='utf-8'))

# # Save the results to disk
# g.serialize('mycsv2rdf.ttl',format='turtle')
# g.serialize(f'{data_processed_directory}test20.nt',format='ntriples', encoding='UTF-8')
g.serialize(f'{data_processed_directory}/lippe_brickmakers_database_with_geodata_sample_as_lod.nt',format='turtle', encoding='UTF-8')
print("done")