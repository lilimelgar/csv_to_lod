# this script is made based on the instructions given in this
# website: https://stackoverflow.com/questions/43524943/creating-rdf-file-using-csv-file-as-input/61445967#61445967
# this script converts a csv file to RDF

import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import os # to work with paths
import uuid

######## 1. DEFINE PATHS TO DATA ###########################
# ## enter path to my local data folder:
# sprintNo = input('sprintNo\n')
# data_directory = f'/Users/lme/Library/CloudStorage/Dropbox/docs_work_latest/SPRINTS/{sprintNo}/data'
# data_raw_directory = f'{data_directory}/raw/'
# data_processed_directory = f'{data_directory}/output/'
# data_temp_directory = f'{data_directory}/temp'

## with local paths: this is the local path to the raw data in your own computer to where you downloaded/cloned the repository"
data_directory = os.path.abspath(os.path.join('..', 'data'))
data_raw_directory = os.path.join(data_directory, 'raw')
data_processed_directory = os.path.join(data_directory, 'processed')
data_temp_directory = os.path.join(data_directory, 'temp')

## fetching data from url
## url='https://raw.githubusercontent.com/KRontheWeb/csv2rdf-tutorial/master/example.csv'
## raw_df_ = pd.read_csv(url)

######## 2. READ RAW CSV ####################################################################
# df = pd.read_csv(f'{data_raw_directory}lippische_ziegler_folia_interpretations_aggregated_all_signaturen.csv', sep=',', quotechar='"')
# df = pd.read_csv(f'{data_raw_directory}/test_with_coordinates_j144_j259_lipper_ziegler_database_folia_links_added.csv', sep=',', quotechar='"')
df = pd.read_csv(f'{data_raw_directory}/simple_test.csv', sep=',', quotechar='"')
# print(df.head())
# # print(df.columns)
# print(df.info())
# print(df.iloc[[1]])

# # ######## 3. DEFINE A GRAPH 'G' AND NAMESPACES ###############################################
g = Graph()
# iisgvoc = Namespace('https://iisg.amsterdam/id/lipperziegler/')
# # schema = Namespace('')
schema = Namespace('https://schema.org/')
iisgvoc = Namespace('https://iisg.amsterdam/')
opengis = Namespace('http://www.opengis.net/ont/geosparql')
# # urls = Namespace('http://schema.org/url')
# # imId = Namespace('https://iisg.amsterdam/id/lipperziegler/vocab/')
# # lippeSchema = Namespace('https://iisg.amsterdam/id/lipperziegler/')

# # # # # #from tutorial
# # # # # ppl = Namespace('http://example.org/people/')
# # # # # loc = Namespace('http://mylocations.org/addresses/')
# # # # # schema = Namespace('http://schema.org/')

# ######## 4. CREATE THE TRIPLES AND ADD THEM TO GRAPH 'G' ####################################
# #It's a bit dense, but each g.add() consists of three parts: 
# #subject, predicate, object. 
# #For more info, check the really friendly rdflib documentation, section 1.1.3 onwards at https://buildmedia.readthedocs.org/media/pdf/rdflib/latest/rdflib.pdf
# # Note that:
#     # I borrow namespaces from rdflib and create some myself;
#     # It is good practice to define the datatype whenever you can;
#     # I create URI's from the addresses (example of string handling).
# ## From example
# # for index, row in df.iterrows():
# # #     g.add((URIRef(ppl+row['ID']), RDF.type, schema.Person))
# # #     g.add((URIRef(ppl+row['Name']), URIRef(schema+'name'), Literal(row['Name'], datatype=XSD.string) ))
# # #     g.add((URIRef(ppl+row['Name']), FOAF.age, Literal(row['Age'], datatype=XSD.integer) ))
# # #     g.add((URIRef(ppl+row['Name']), URIRef(schema+'address'), Literal(row['Address'], datatype=XSD.string) ))
# # #     g.add((URIRef(loc+urllib.parse.quote(row['Address'])), URIRef(schema+'name'), Literal(row['Address'], datatype=XSD.string) ))



# add triples iterating through the rows
for index, row in df.iterrows():
    # create the node first (this will be the location)
    g.add((URIRef(iisgvoc+row['location']), RDF.type, schema.Location))
    g.add((URIRef(iisgvoc+row['location']), opengis.hasGeometry, row['coordinates'] ))



    # # add image Id: subject (it's what I am describing, with a URI in the namespace of iisg), predicate (it's the property in the namespace schema.org), object (it's the string of the Id)
    # g.add((URIRef(iisgvoc+row['_test_PERSON_NAME']), RDF.type, schema.Person))

#     # # add transcript: subject (it's what I am describing: the image), predicate (it's the property transcription in the namespace schema.org), object (it's the string of the transcription)
#     # # g.add((URIRef(iisgvoc+row['imageId']), URIRef(schema+'transcript'), Literal(row['transcription'], datatype=XSD.string)))
#     # g.add((URIRef(iisgvoc+row['file_Id_old']), URIRef(iisgvoc+'transcribedAs'), Literal(row['content'], datatype=XSD.string)))

#     # add url to the scan: subject (it's what I am describing: the image), predicate (it's the property url in the namespace schema.org), object (it's the url to the image)
#     # g.add((URIRef(iisgvoc+row['imageId']), URIRef(iisgvoc+'vocab/cv'), URIRef(row['imageUrl'])))
#     # g.add((URIRef(iisgvoc+row['original_source']), URIRef(iisgvoc+'vocab/cv'), URIRef(row['page_scan_url'])))

#     # TEST adding triple for places
#     g.add((URIRef(iisgvoc+row['Wohin']), URIRef(iisgvoc+'vocab/cv'), Literal(row['wohin-lat-lon'])))

# Check the results
print(g.serialize(format='nt', encoding='utf-8'))

# # # # Save the results to disk
# # # g.serialize('mycsv2rdf.ttl',format='turtle') ##from tutorial
# # # g.serialize(f'{data_processed_directory}test20.nt',format='ntriples', encoding='UTF-8')
# # g.serialize(f'{data_processed_directory}csvtordf_ziegler_folia_interpretations_v1.nt',format='turtle', encoding='UTF-8')
# # print("done")
