import numpy.random as rn
import nltk
import pywikibot as pw
from pywikibot import pagegenerators as pg



def get_word_list(file_name):
    """Generate words from 10,000 most common words in english"""

    with open(file_name) as f:
        data = f.read()
        words_list = data.split(',')

    return words_list

class target_word:
    """
    Generate a target word and score range.
    """

    def __init__(self, word_list):
        """Initialise the parameters"""
        self.word = None
        self.range = None
        self.word_list = word_list

    def word_gen(self):
        """Generate word from dictionary"""

        selected_int = rn.randint(0, high=len(self.word_list)+1)
        selected_word = self.word_list[selected_int]

        if selected_word[-1] == 's':
            selected_word = selected_word[:-1]
            # Discard plurals.

        self.word = selected_word


    def range_gen(self):
        """Generate acceptable range for word"""

        word_len = len(self.word)
        # Adapt range based on length of word.
        range_size = rn.randint(5, high=30)
        # Range interval size.

        lower = int(1/word_len*10)
        if 1/word_len>0.3:
            lower = lower*rn.randint(1, high=3)
        # Longer words less common, so have lower limit proportional to word size.

        upper = int(1/word_len*10)*100