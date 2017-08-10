# pmcTextMiner
*A text miner for PubMed abstracts*

Mines PubMed's API for a query (eg. a couple of gene names, proteins, etc...),
runs the resulting abstracts through Neji (a biomedical named entity
recognizer), tallies the named entities into an .xlsx file, and creates pretty
word clouds for found genes, anatomy features, and disorders/diseases.

## Usage:
`python pmcTextMiner.py --query <string> --ofilepath <path>  [--mineBodies] [--email <string>] [--nerPath <path>] [--threads <int>]`
- `--query`: the query string to search in PubMed.
- `--ofilepath`: the directory to output results to. Mac users: don't use ~/
- `--email`: optional (if not given, uses value specified in this file). email required for PubMed API access (idk why). Probably a good idea to update this for your machine.
- `--nerPath`: optional (if not given, uses value specified in this file). the path to Neji. Probably a good idea to update this for your machine.
- `--threads`: optional (if not given, uses value specified in this file). the number of threads available for your task. more threads will speed up Neji named entity recognition.
- `--mineBodies`: optional. if specified, program will mine full pubmed central article bodies instead of just pubmed abstracts

## Dependencies

### Non-standard Python packages (all available from pip):
-beautifulsoup: xml parsing
-unirest: api handling
-lxml: xml parsing (required by BeautifulSoup)
-wordcloud: for word cloud output
-xlsxwriter: for xlsx output

### Other Programs
-Neji: biomedical named entity recognition. For documentation and download, see [https://github.com/BMDSoftware/neji]
