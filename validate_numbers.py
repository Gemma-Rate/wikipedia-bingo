import urllib.request as un
from bs4 import BeautifulSoup as bs
import re
import nltk

class Validation:
    """Validate word lengths"""

    def __init__(self, page_title):
        """Initialise the parameters"""
        self.page_text = None
        self.stripped_text = None
        self.title = page_title
        self.token = None

    def scrape_wiki(self):
        """Get text from Wikipedia page"""

        self.title = self.title.replace(' ', '_')
        # Add underscore for page search.

        url = 'https://en.wikipedia.org/wiki/'+self.title
        web_data = un.urlopen(url)
        read_page = bs(web_data.read(), 'html.parser')
        text = read_page.get_text()
        # Get parsed text in html.

        self.page_text = text

    def process_wiki(self):
        """Process wiki text to remove [] and {} and tokenise words"""
        stripped = self.page_text.replace('[edit]', '')
        # Get rid of random [edit].

        stripped = re.sub(r'\[(\d+)\]', '', stripped)
        # Get rid of reference numbers.
        #m = re.search(r'(\d+).', stripped)
        stripped = re.sub(r'\d.+(\w+)', '', stripped)
        stripped = stripped.replace('Contents', '')
        # Exclude contents.

        #stripped =
        # Exclude references.

        # Exclude Main article: links.

        self.stripped_text = stripped
        tokens = nltk.word_tokenize(self.stripped_text)
        self.token = tokens


