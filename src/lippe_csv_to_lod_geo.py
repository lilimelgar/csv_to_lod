# this script is made based on the instructions given in this
# tutorial: https://stackoverflow.com/questions/43524943/creating-rdf-file-using-csv-file-as-input/61445967#61445967
# this script converts a csv file to RDF using rdflib library

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
df_raw = pd.read_csv(f'{data_raw_directory}/lippe_brickmakers_database_with_geodata_sample.csv', sep=',', quotechar='"')
# print(df.head())
# print(df.columns)
# # print(df.info())
# # print(df.iloc[[1]])

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
# create column for person name
df_wohin_all['person_name'] = df_wohin_all['Namen'] + ' ' + df_wohin_all['Vornamen']
# replace 'null' with ''
df_wohin_all['person_name'] = df_wohin_all['person_name'].str.replace(' null', '')
# create column for placeId, generating a local unique Id for a place in the context of the data concatenating the 'signature' and the column name with its value
df_wohin_all['place_id'] = df_wohin_all['Signatur'] + '/wohin/' + df_wohin_all['Wohin']
# convert 'wohin_WHG_identifier' to URL (note: ideally, there will be a proper URI using the API for calling the data for a specific place but, in order to do this, the dataset has to be made public in the World Historical Gazetteer)
df_wohin_all['wohin_WHG_identifier'] = 'https://whgazetteer.org/places/' + df_wohin_all['wohin_WHG_identifier'] + 'detail'


# # ######## 6. GROUP BY PLACE ID ####################################################################
# create a copy of the dataframe droping unnecessary columns
df_wohin = df_wohin_all[['place_id', 'Wohin', 'wohin_WHG_identifier', 'wohin_matches', 'wohin_geowkt', 'wohin_latitude', 'wohin_longitude', 'person_name', 'Fabrik', 'Jahr']].copy()
# group by place/wohin using the local unique placeId
df_wohin_grouped = df_wohin.groupby('place_id').agg(lambda x: ';'.join(x.unique()))
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
    # create triple for local place_id
    g.add((URIRef(lippevoc+'id/'+row['place_id']), URIRef(lippevoc+'identifier'), Literal(row['place_id'], datatype=XSD.string)))
    # create triple for place name
    g.add((URIRef(lippevoc+'id/'+row['place_id']), URIRef(sdo+'name'), Literal(row['Wohin'], datatype=XSD.string)))
    # create triple for name string chosen as a way to represent the place's area
    g.add((URIRef(lippevoc+'id/'+row['place_id']), URIRef(lippevoc+'representedBy'), Literal(row['Wohin'], datatype=XSD.string)))
    # generate a triple for the place's local unique identifier
    g.add((URIRef(lippevoc+'id/'+row['place_id']), URIRef(opengis+'#asWKT'), Literal(row['wohin_geowkt'], datatype=opengis+'#wktLiteral')))
    # generate a triple for the equivalent identifier in the World Historical Gazetteer (note: in order to use the proper API call for a place, the dataset has to be made public, thus, we use the detail page URL for this demo)
    g.add((URIRef(lippevoc+'id/'+row['place_id']), URIRef(sdo+'sameAs'), URIRef(row['wohin_WHG_identifier'])))

# # Check the results
# print(g.serialize(format='nt', encoding='utf-8'))

# # Save the results to disk
# g.serialize('mycsv2rdf.ttl',format='turtle')
# g.serialize(f'{data_processed_directory}test20.nt',format='ntriples', encoding='UTF-8')
g.serialize(f'{data_processed_directory}/lippe_brickmakers_database_with_geodata_sample_as_LOD.nt',format='turtle', encoding='UTF-8')
print("done")