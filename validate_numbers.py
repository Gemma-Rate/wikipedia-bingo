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
        self.raw_title = page_title
        self.token = None

    def scrape_wiki(self, mode_choice=0):
        """Get text from Wikipedia page"""

        self.title = self.title.replace(' ', '_')
        # Add underscore for page search.

        modes = ['https://en.wikipedia.org/wiki/',
                 'https://simple.wikipedia.org/wiki/']
        # Simple english and normal mode.

        url = modes[mode_choice]+self.title
        web_data = un.urlopen(url)
        read_page = bs(web_data.read(), 'html.parser')
        text = read_page.get_text()
        # Get parsed text in html.

        self.page_text = text

    def process_wiki(self):
        """Process wiki text to tokenise words"""
        stripped = self.page_text.replace('[edit]', '')
        # Get rid of random [edit].

        stripped = re.sub(r'\[(\d+)\]', '', stripped)
        # Get rid of reference numbers.

        self.stripped_text = stripped
        tokens = nltk.word_tokenize(self.stripped_text)
        self.token = tokens


