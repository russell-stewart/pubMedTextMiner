#pmcTextMiner.py
#Russell O. Stewart
#8/9/2017
#A text miner for PubMed
#Mines PubMed's API for a query (eg. a couple of gene names, proteins, etc...)
#runs the resulting abstracts through Neji (a biomedical named entity
#recognizer), tallies the named entities into an .xlsx file, and creates pretty
#word clouds for found genes, anatomy features, and disorders/diseases.
#
#Usage:
#python pmcTextMiner.py --query --ofilepath [--email] [--nerPath] [--threads]
#--query: the query string to search in PubMed.
#--ofilepath: the directory to output results to. Mac users: don't use ~/
#--email: optional (if not given, uses value specified in this file).
#   email required for PubMed API access (idk why). Probably a good idea to
#   update this for your machine.
#--nerPath: optional (if not given, uses value specified in this file).
#   the path to Neji. Probably a good idea to update this for your machine.
#--threads: optional (if not given, uses value specified in this file).
#   the number of threads available for your task. more threads will speed up Neji named entity recognition.
#
#Dependencies
#
#Non-standard Python packages (all available from pip):
#BeautifulSoup: xml parsing
#unirest: api handling
#lxml: xml parsing (required by BeautifulSoup)
#wordcloud: for word cloud output
#xlsxwriter: for xlsx output
#
#Other Programs
#Neji: biomedical named entity recognition. For documentation and download, see:
#https://github.com/BMDSoftware/neji


from bs4 import BeautifulSoup
import unirest
import lxml
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import getopt
import os
from PIL import Image
from wordcloud import WordCloud
from xlsxwriter import Workbook
# -*- coding: utf-8-*-

#Default parameters
#It might be useful to update nerPath and threads, and email for your machine,
#as these likely won't change every time you run the script.
nerPath = '/Users/russellstewart/Documents/NationalJewish/Seibold/neji'
threads = 4
email = 'russells98@gmail.com'

#stores freqencies of all NamedEntities associated with one tag
class Tag:
    def __init__(self , classification , firstEntity):
        self.classification = classification
        self.entities = [NamedEntity(firstEntity)]
    def add(self , new):
        found = False
        for entity in self.entities:
            if new == entity.text:
                entity.increment()
                found = True
        if not found:
            self.entities.append(NamedEntity(new))
    def toString(self):
        self.sort()
        string = u'Classification: %s\n' % self.classification
        for entity in self.entities:
            string += '  %s\n' % entity.toString()
        string += '\n'
        return string
    def sort(self):
        self.entities.sort(key = lambda x: x.occurances , reverse = True)
    def EntityString(self):
        string = u''
        for entity in self.entities:
            for i in range(0 , len(self.entities)):
                string += entity.text + ' '
        return string

#stores a named entity's text and its number of occurances
class NamedEntity:
    def __init__(self , text):
        self.text = text
        self.occurances = 1
    def increment(self):
        self.occurances += 1
    def toString(self):
        return '%s: %d' % (self.text , self.occurances)


#Get parameters from program call
opts = getopt.getopt(sys.argv[1:] , '' , ['query=' , 'ofilepath=' , 'email=' , 'nerPath=' , 'threads='])

query = None
ofilepath = None
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
if query == None or ofilepath == None:
    raise Exception('Remember to specify --query and --ofilepath!!!!')

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
        results = BeautifulSoup(getRecordResponse.body , 'lxml').find_all('abstract')
        for abstract in results:
            abstracts += abstract.get_text().strip()
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
command = '%s/neji.sh -i %s -o %s -d %s/resources/dictionaries -m %s/resources/models -t %d -if RAW -of XML' %(nerPath , ofilepath , ofilepath , nerPath , nerPath , threads)
print '\n' + command + '\n'
returncode = os.system(command)

#after pipeline finishes, import the Neji results and xml parse them.
#(I chose XML because I already had to import XML parsers to deal with PubMed.)
print '\nNER done! Importing results...'
annotatedAbstracts = BeautifulSoup(open(ofilepath + '/abstracts.xml' , 'r').read().encode('UTF-8') , 'lxml')

#iterate over every named entity in every sentence, and parse the tag from
#the id. see if the tag exists in the tags database, add the entity to that Tag.
#if the tag is not found, create a new Tag in tags
tags = []
for sentence in annotatedAbstracts.find_all('s'):
    for annotation in sentence.find_all('e'):
        classification = annotation['id']
        i = 0
        while i < len(classification):
            if classification[i] == ':':
                classification = classification[(i + 1):]
                i = -1
            if classification[i] == '|' or classification[i] == ')':
                classification = classification[:i]
                i = len(classification)
            i+= 1
        found = False
        for currentTag in tags:
            if currentTag.classification == classification:
                currentTag.add(annotation.get_text())
                found = True
        if not found:
            tags.append(Tag(classification , annotation.get_text()))

#generate word clouds and output .xlsx file
print 'Writing output files...'
ofile = Workbook((ofilepath + '/' + query + '_' + 'results.xlsx'))
for tag in tags:
    if tag.classification == 'PRGE':
        tag.classification = 'genes'
    elif tag.classification == 'ANAT':
        tag.classification = 'anatomy'
    elif tag.classification == 'DISO':
        tag.classification = 'diseases'
    worksheet = ofile.add_worksheet(tag.classification.encode('UTF-8'))
    worksheet.write_string(0 , 0 , 'Named Entity')
    worksheet.write_string(0 , 1 , 'Occurances')
    i = 0
    tag.sort()
    for entity in tag.entities:
        worksheet.write_string(i , 0 , entity.text.encode('UTF-8'))
        worksheet.write_number(i , 1 , entity.occurances)
        i += 1
    image = WordCloud().generate(tag.EntityString()).to_image()
    image.save(ofilepath + '/' + query + '_' + tag.classification + '.bmp')
ofile.close()

#delete the temporary abstracts files used for communication with neji
print 'Cleaning up...'
os.remove(ofilepath + '/' + 'abstracts.txt')
os.remove(ofilepath + '/' + 'abstracts.xml')
