from bs4 import BeautifulSoup
import unirest
import lxml
import sys
import getopt

#Get parameters from program call
opts = getopt.getopt(sys.argv[1:] , '' , ['query=' , 'ofile=' , 'email='])

for opt , arg in opts[0]:
    if opt == '--query':
        query = arg
    if opt == '--ofile':
        oFilePath = arg
    if opt == '--email':
        email = arg

#Search PubMed (w/ user specifed query) and extract all resulting article IDs
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

#Retrieve the abstracts for all article ids obtained above
getRecordURL = 'https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi'
abstracts = []
for currentID in ids:
    identifier = 'oai:pubmedcentral.nih.gov:%d' % currentID
    getRecordResponse = unirest.get(
        getRecordURL,
        params = {
            'verb' : 'GetRecord',
            'identifier' : identifier,
            'metadataPrefix' : 'pmc'
        }
    )
    print getRecordResponse.code
    #fish the abstract out of the slop of xml returned by the API
    #and append it to the abstracts array
    xml = BeautifulSoup(getRecordResponse.body , 'lxml')
    print xml
    abstract = xml.find_all('abstract')
    abstract = abstract.get_text()
    abstracts.append(abstract)

    print abstract + '\n\n'
