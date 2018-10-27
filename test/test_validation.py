import unittest as un
import word_generation as wn
import numpy as np
import validate_numbers as vn

class TestValidation(un.TestCase):

    def test_scrape_wiki(self):
        """Test getting page title"""
        val = vn.Validation('Ice', 'ice', np.arange(0,20))
        val.scrape_wiki()

    def test_process_wiki(self):
        """Test removing wiki markup"""
        val = vn.Validation('Ice', 'ice', np.arange(0,20))
        val.scrape_wiki()
        val.process_wiki()


if __name__ == '__main__':
    un.main()