import unittest as un
import word_generation as wn

class TestGeneration(un.TestCase):

    def test_load(self):
        w = wn.get_word_list('no_stop_g2.txt')
        self.assertEqual(len(w), 9368)
        self.assertTrue('germany' in w)

    def test_word_generate(self):
        """Test word generation with json loaded file"""
        w = wn.get_word_list('no_stop_g2.txt')
        word = wn.target_word(w)
        word.word_gen()
        print(word.word)

if __name__ == '__main__':
    un.main()