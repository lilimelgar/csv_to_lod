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
# the file we are converting to LOD is a csv file deposited in Dataverse, where this dataset: https://hdl.handle.net/10622/1RNBFT contains both files (the original csv and the converted lod (output of this script))
df = pd.read_csv(f'{data_raw_directory}test_page-transcript.csv', sep=';', quotechar='"')
# print(df.head())
# # print(df.columns)
# # print(df.info())

######## 3. DEFINE A GRAPH 'G' AND NAMESPACES ###############################################
g = Graph()
iisgvoc = Namespace('https://iisg.amsterdam/id/lipperziegler/')
# schema = Namespace('')
schema = Namespace('https://schema.org/')
# urls = Namespace('http://schema.org/url')
# imId = Namespace('https://iisg.amsterdam/id/lipperziegler/vocab/')
# lippeSchema = Namespace('https://iisg.amsterdam/id/lipperziegler/')

# # # #from tutorial
# # # ppl = Namespace('http://example.org/people/')
# # # loc = Namespace('http://mylocations.org/addresses/')
# # # schema = Namespace('http://schema.org/')

######## 4. CREATE THE TRIPLES AND ADD THEM TO GRAPH 'G' ####################################
#It's a bit dense, but each g.add() consists of three parts: 
#subject, predicate, object. 
#For more info, check the really friendly rdflib documentation, section 1.1.3 onwards at https://buildmedia.readthedocs.org/media/pdf/rdflib/latest/rdflib.pdf
# Note that:
    # I borrow namespaces from rdflib and create some myself;
    # It is good practice to define the datatype whenever you can;
    # I create URI's from the addresses (example of string handling).
## From example
# for index, row in df.iterrows():
#     g.add((URIRef(ppl+row['Name']), RDF.type, FOAF.Person))
#     g.add((URIRef(ppl+row['Name']), URIRef(schema+'name'), Literal(row['Name'], datatype=XSD.string) ))
#     g.add((URIRef(ppl+row['Name']), FOAF.age, Literal(row['Age'], datatype=XSD.integer) ))
#     g.add((URIRef(ppl+row['Name']), URIRef(schema+'address'), Literal(row['Address'], datatype=XSD.string) ))
#     g.add((URIRef(loc+urllib.parse.quote(row['Address'])), URIRef(schema+'name'), Literal(row['Address'], datatype=XSD.string) ))

for index, row in df.iterrows():
    
    # add image Id: subject (it's what I am describing, with a URI in the namespace of iisg), predicate (it's the property in the namespace schema.org), object (it's the string of the Id)
    g.add((URIRef(iisgvoc+row['file_Id_old']), URIRef(iisgvoc+'vocab/id'), Literal(row['file_Id_old'], datatype=XSD.string)))

    # add transcript: subject (it's what I am describing: the image), predicate (it's the property transcription in the namespace schema.org), object (it's the string of the transcription)
    # g.add((URIRef(iisgvoc+row['imageId']), URIRef(schema+'transcript'), Literal(row['transcription'], datatype=XSD.string)))
    g.add((URIRef(iisgvoc+row['file_Id_old']), URIRef(iisgvoc+'transcribedAs'), Literal(row['content'], datatype=XSD.string)))

    # add url to the scan: subject (it's what I am describing: the image), predicate (it's the property url in the namespace schema.org), object (it's the url to the image)
    # g.add((URIRef(iisgvoc+row['imageId']), URIRef(iisgvoc+'vocab/cv'), URIRef(row['imageUrl'])))
    g.add((URIRef(iisgvoc+row['file_Id_old']), URIRef(iisgvoc+'vocab/cv'), URIRef(row['page_scan_url'])))

# # Check the results
# print(g.serialize(format='nt', encoding='utf-8'))

# # Save the results to disk
# g.serialize('mycsv2rdf.ttl',format='turtle') ##from tutorial
# g.serialize(f'{data_processed_directory}test20.nt',format='ntriples', encoding='UTF-8')
g.serialize(f'{data_processed_directory}csvtordf_ziegler_folia_interpretations_v1.nt',format='turtle', encoding='UTF-8')
print("done")
