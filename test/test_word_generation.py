import unittest as un
import word_generation as wn

class TestGeneration(un.TestCase):

    def test_load(self):
        """Test all file load data"""
        w = wn.get_word_list('no_stop_g2.txt')
        self.assertEqual(len(w), 9368)
        self.assertTrue('germany' in w)

    def test_word_generate(self):
        """Test word generation with loaded file"""
        w = wn.get_word_list('no_stop_g2.txt')
        word = wn.TargetWord(w)
        word.word_gen()
        print(word.word)

    def test_range_generate(self):
        """Test range generation"""
        w = wn.get_word_list('no_stop_g2.txt')
        word = wn.TargetWord(w)
        word.word_gen()
        word.range_gen()
        print(word.range)

if __name__ == '__main__':
    un.main()