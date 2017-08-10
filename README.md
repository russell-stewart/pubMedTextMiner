# pubMedTextMiner
*A text miner for PubMed abstracts*

Mines PubMed's API for a query (eg. a couple of gene names, proteins, etc...),
runs the resulting abstracts through Neji (a biomedical named entity
recognizer), tallies the named entities into an .xlsx file, and creates pretty
word clouds for found genes, anatomy features, and disorders/diseases.

## Setup:
1. Clone this repository
2. Run `sudo packagehelper.py`
3. Download and unzip [the latest version of neji](https://github.com/BMDSoftware/neji/releases/download/v2.0.0/neji-2.0.0.zip)
4. Update nerPath , threads, and email at the top of pmcTextMiner.py (to streamline command line interface)
5. Refer to Usage!

## Usage:
`python pmcTextMiner.py --query <string> --ofilepath <path>  [--mineBodies] [--retmax <int>] [--email <string>] [--nerPath <path>] [--threads <int>]`
- `--query`: the query string to search in PubMed.
- `--ofilepath`: the directory to output results to. Mac users: don't use ~/
- `--email`: optional (if not given, uses value specified in this file). email required for PubMed API access (idk why). Probably a good idea to update this for your machine.
- `--nerPath`: optional (if not given, uses value specified in this file). the path to Neji. Probably a good idea to update this for your machine.
- `--threads`: optional (if not given, uses value specified in this file). the number of threads available for your task. more threads will speed up Neji named entity recognition.
- `--mineBodies`: optional. if specified, program will mine full pubmed central article bodies instead of just pubmed abstracts
- `--retmax`: optional, default is 20 (PubMed API's default). Maximum number of articles to mine. Must be smaller than 10,000.

## Dependencies

### Non-standard Python packages:

If don't have any of these packages installed, just run `sudo python packagehelper.py`, and all of the needed packages will be installed using pip!

- beautifulsoup: xml parsing
- unirest: api handling
- lxml: xml parsing (required by BeautifulSoup)
- wordcloud: for word cloud output
- xlsxwriter: for xlsx output

### Other Programs
-Neji: biomedical named entity recognition. For documentation and download, see [https://github.com/BMDSoftware/neji]
