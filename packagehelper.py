#packagehelper.py
#Russell O. Stewart
#8/10/2017
#Imports all packages needed for use with pmcTextMiner.py using pip
#Make sure to sudo if you're using a mac!

import os , sys , getopt

helpMenu = False
opts = getopt.getopt(sys.argv[1:] , '-h' , 'help')
for opt , arg in opts[0]:
    if opt == '-h' or opt == '--help':
        print 'sudo python packagehelper.py [--help]\nThis helper will install all needed python packages using pip.\nThis does not install neji!\n'
        helpMenu = True

if not helpMenu:
    try:
        import unirest
    except ImportError:
        os.system('pip install unirest')

    try:
        import lxml
    except ImportError:
        os.system('pip install lxml')

    try:
        import wordcloud
    except ImportError:
        os.system('pip install wordcloud')

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        os.system('pip install beautifulsoup4')

    try:
        import xlsxwriter
    except ImportError:
        os.system('pip install xlsxwriter')

print 'All packages ready to go!'
