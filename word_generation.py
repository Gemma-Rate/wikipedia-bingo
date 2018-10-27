import numpy.random as rn
import numpy as np


def get_word_list(file_name):
    """Generate words from 10,000 most common words in english"""

    with open(file_name) as f:
        data = f.read()
        words_list = data.split(',')

    return words_list

class TargetWord:
    """
    Generate a target word and score range.
    """

    def __init__(self, word_list):
        """Initialise the parameters"""
        self.word = None
        self.upper = None
        self.word_list = word_list

    def word_gen(self):
        """Generate word from dictionary"""

        selected_int = rn.randint(0, high=len(self.word_list)+1)
        selected_word = self.word_list[selected_int]

        self.word = selected_word


    def range_gen(self, mode=0):
        """Generate acceptable range for word"""
        difficulty = [7, 5, 3]
        # First = easy, second = medium, third = hard.

        self.upper = difficulty[mode]