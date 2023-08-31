# this script is made based on the instructions given in this
# website: https://stackoverflow.com/questions/43524943/creating-rdf-file-using-csv-file-as-input/61445967#61445967
# this script converts a csv file to RDF

import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import os # to work with paths

## Read the csv file
## with local paths: this is the local path to the raw data in your own computer to where you downloaded/cloned the repository"
data_directory = os.path.abspath(os.path.join('..', 'data'))
data_raw_directory = os.path.join(data_directory, 'raw')
data_processed_directory = os.path.join(data_directory, 'processed')
data_temp_directory = os.path.join(data_directory, 'temp')
raw_file_path = os.path.join(data_raw_directory, 'test_page-transcript.csv') 
df = pd.read_csv(raw_file_path, sep=';', quotechar='"')
# print(df.head())
# print(df.columns)
# print(df.info())

# # ## fetching data from url
# # # url='https://raw.githubusercontent.com/KRontheWeb/csv2rdf-tutorial/master/example.csv'
# # raw_df_ = pd.read_csv(raw_file_path)
# # print(raw_df_)

# Define a graph 'g' and namespaces
g = Graph()
iisgvoc = Namespace('https://iisg.amsterdam/id/lipperziegler/')
# schema = Namespace('')
schema = Namespace('https://schema.org/')
# urls = Namespace('http://schema.org/url')
# imId = Namespace('https://iisg.amsterdam/id/lipperziegler/vocab/')
# lippeSchema = Namespace('https://iisg.amsterdam/id/lipperziegler/')

# #from tutorial
# ppl = Namespace('http://example.org/people/')
# loc = Namespace('http://mylocations.org/addresses/')
# schema = Namespace('http://schema.org/')

## Create the triples and add them to graph 'g'
# #It's a bit dense, but each g.add() consists of three parts: 
# #subject, predicate, object. 
# #For more info, check the really friendly rdflib documentation, section 1.1.3 onwards at https://buildmedia.readthedocs.org/media/pdf/rdflib/latest/rdflib.pdf
# # Note that:
#     # I borrow namespaces from rdflib and create some myself;
#     # It is good practice to define the datatype whenever you can;
#     # I create URI's from the addresses (example of string handling).
## From example
# for index, row in df.iterrows():
#     g.add((URIRef(ppl+row['Name']), RDF.type, FOAF.Person))
#     g.add((URIRef(ppl+row['Name']), URIRef(schema+'name'), Literal(row['Name'], datatype=XSD.string) ))
#     g.add((URIRef(ppl+row['Name']), FOAF.age, Literal(row['Age'], datatype=XSD.integer) ))
#     g.add((URIRef(ppl+row['Name']), URIRef(schema+'address'), Literal(row['Address'], datatype=XSD.string) ))
#     g.add((URIRef(loc+urllib.parse.quote(row['Address'])), URIRef(schema+'name'), Literal(row['Address'], datatype=XSD.string) ))

for index, row in df.iterrows():
    
    # add image Id: subject (it's what I am describing, with a URI in the namespace of iisg), predicate (it's the property in the namespace schema.org), object (it's the string of the Id)
    g.add((URIRef(iisgvoc+row['imageId']), URIRef(schema+'identifier'), Literal(row['imageId'], datatype=XSD.string) ))

    # add transcript: subject (it's what I am describing: the image), predicate (it's the property transcription in the namespace schema.org), object (it's the string of the transcription)
    g.add((URIRef(iisgvoc+row['imageId']), URIRef(schema+'transcript'), Literal(row['transcription'], datatype=XSD.string) ))

    # add url to the scan: subject (it's what I am describing: the image), predicate (it's the property url in the namespace schema.org), object (it's the url to the image)
    g.add((URIRef(iisgvoc+row['imageId']), URIRef(schema+'url'), Literal(row['imageUrl'], datatype=XSD.string) ))

# Check the results
print(g.serialize(format='nt'))

# # Save the results to disk
# g.serialize('mycsv2rdf.ttl',format='turtle') ##from tutorial
g.serialize('csvlippe2rdf_test5.nt',format='ntriples')
