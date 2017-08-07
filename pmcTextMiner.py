from bs4 import BeautifulSoup
import unirest
import lxml
import sys
import getopt
from collections import Counter
import subprocess

#Update this with the path to NER Tagger!!
nerPath = '~/Documents/NationalJewish/Seibold/NERTagger/taggers'

#Get parameters from program call
opts = getopt.getopt(sys.argv[1:] , '' , ['query=' , 'ofilepath=' , 'email='])

for opt , arg in opts[0]:
    if opt == '--query':
        query = arg
    if opt == '--ofilepath':
        oFilePath = arg
    if opt == '--email':
        email = arg

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
print 'Retrieving article titles and abstracts...'
getRecordURL = 'https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi'
titles = ''
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
        xml = BeautifulSoup(getRecordResponse.body , 'lxml')
        title = xml.find('title').get_text()
        abstract = xml.find('abstract').get_text()
        titles += title + '\n'
        abstracts += abstract + '\n'
        success += 1
    except:
        #catches any API response without an abstract
        fail += 1

print '  %d title/abstract pairs read successfully.' % success
if fail:
    print '  %d could not be read.' % fail

#write titles and abstracts to files for use by the named entity
#recognition pipeline

titlesPath = oFilePath + '/titles.txt'
titleFile = open(titlesPath , 'w')
titleFile.write(titles.encode('utf8'))
titleFile.close()
abstractsPath = oFilePath + '/abstracts.txt'
abstractFile = open(abstractsPath , 'w')
abstractFile.write(abstracts.encode('utf8'))
abstractFile.close()

#run named entity recognition pipeline on titles and on abstracts
# print 'Running NER on abstracts...'
# command = '%s/tagger.py --model models/english/ --input %s --output %s' % (nerPath , abstractsPath , oFilePath + '/titlesOut.txt')
# returncode = subprocess.call(command)
# print 'Running NER on titles...'
# command = '%s/tagger.py --model models/english/ --input %s --output %s' % (nerPath , titlesPath , oFilePath + '/titlesOut.txt')
# returncode = subprocess.call(command)
# print 'Done!!'
