from bs4 import BeautifulSoup
import unirest
import lxml
import sys
import getopt
import subprocess
import os

#Get parameters from program call
opts = getopt.getopt(sys.argv[1:] , '' , ['query=' , 'ofilepath=' , 'email=' , 'nerPath=' , 'threads='])

#Default parameters
nerPath = '/Users/russellstewart/Documents/NationalJewish/Seibold/neji'
threads = 4
ofilepath = '/Users/russellstewart/Documents/NationalJewish/Seibold/pmctextminer/results'
query = 'PTPRA'
email = 'russells98@gmail.com'

for opt , arg in opts[0]:
    if opt == '--query':
        query = arg
    if opt == '--ofilepath':
        ofilepath = arg
    if opt == '--email':
        email = arg
    if opt == '--nerPath':
        nerPath = arg
    if opt == '--threads':
        threads = arg

#Search PubMed (w/ user specifed query) and extract all resulting article IDs
print 'Finding relevant articles on PubMed...'
searchURL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
searchResponse = unirest.get(
    searchURL,
    params = {
        'db' : 'pmc',
        'term' : query,
        'tool' : 'pmcTextMiner',
        'email' : email
    }
)
ids = BeautifulSoup(searchResponse.body , 'lxml').get_text()
ids = [int(numeric_string) for numeric_string in ids[:ids.find(' ')].splitlines()]
print '  %d results found.' % len(ids)

#Retrieve the abstracts for all article ids obtained above
print 'Retrieving article abstracts...'
getRecordURL = 'https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi'
abstracts = ''
success = 0
fail = 0
for currentID in ids[1:]:
    identifier = 'oai:pubmedcentral.nih.gov:%d' % currentID
    getRecordResponse = unirest.get(
        getRecordURL,
        params = {
            'verb' : 'GetRecord',
            'identifier' : identifier,
            'metadataPrefix' : 'pmc'
        }
    )
    #fish the abstract out of the slop of xml returned by the API
    #and append it to the abstracts array
    try:
        abstracts += BeautifulSoup(getRecordResponse.body , 'lxml').find('abstract').get_text().strip()
        success += 1
    except:
        #catches any API response without an abstract
        fail += 1

print '  %d abstracts read successfully.' % success
if fail:
    print '  %d could not be read.' % fail

#write abstracts to files for use by the named entity
#recognition pipeline
abstractsPath = ofilepath + '/abstracts.txt'
abstractFile = open(abstractsPath , 'w')
abstractFile.write(abstracts.encode('utf8'))
abstractFile.close()

#run named entity recognition pipeline on titles and on abstracts
print 'Running NER on abstracts...'

os.chdir(nerPath)
print os.listdir('./')
command = './neji.sh -i %s -o %s -d ./resources/dictionaries -m ./resources/models -t %d -if RAW -of XML' %(ofilepath , ofilepath , threads)
print '  ' + command
returncode = subprocess.call(command)

#after pipeline finishes, import the Neji results and xml parse them.
#(I chose XML because I already had to import XML parsers to deal with PubMed.)
print 'NER done! Importing results...'
annotatedAbstracts = BeautifulSoup(open(ofilepath + '/results.xml' , 'r').read() , 'lxml')
