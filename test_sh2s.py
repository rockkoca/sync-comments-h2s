from unittest import TestCase
from sync_comment_h2s import *

sh2s = Sh2s('/')


class TestSh2s(TestCase):
    def test_unify_function_name(self):
        result = 'ostream &operator<<(ostream &, const WordTree &)'
        test = 'ostream &operator<<(ostream &,' \
               ' const WordTree &wordTree)'

        self.assertEqual(result, Sh2s.unify_function_name(test))

    def test_extract_function_name(self):
        result = 'WordTree(const WordTree &)'
        test = 'WordTree(const WordTree &wordTree);'
        self.assertEqual(result, Sh2s.unify_function_name(test))

        result = 'WordTree::WordNode *AddHelper(const string, WordNode *)'
        test = 'WordTree::WordNode *AddHelper(const string word, WordNode *)'
        self.assertEqual(result, Sh2s.unify_function_name(test))

        result = 'int getHelper(const string, const WordNode *) const'
        test = 'int getHelper(const string word, const WordNode *curr) const;'
        self.assertEqual(result, Sh2s.unify_function_name(test))

    def test_format_asterisk_ampersand(self):
        result = 'int getHelper(const string &, const WordNode *&) const'
        test = 'int getHelper(const string&, const WordNode*&) const'
        self.assertEqual(result, Sh2s.format_asterisk_ampersand(test))

        result = 'int getHelper(const string *, const WordNode *&) const'
        test = 'int getHelper(const string*, const WordNode*&) const'
        self.assertEqual(result, Sh2s.format_asterisk_ampersand(test))

        result = 'int getHelper(const string **, const WordNode *&) const'
        test = 'int getHelper(const string**, const WordNode*&) const'
        self.assertEqual(result, Sh2s.format_asterisk_ampersand(test))

    def test_extract_class_name(self):
        result = 'WordNode'
        test = 'struct WordNode {'
        self.assertEqual(result, Sh2s.extract_class_name(test))

        result = 'WordNode'
        test = 'class WordNode '
        self.assertEqual(result, Sh2s.extract_class_name(test))

    def test_match_function_line(self):
        # starts with space or tab or letters, optional two ::
        # some optional letters and anything until (
        # ) could be in next line
        match_function = re.compile(r'^\s*\t*\w+:{0,2}\w*\s*.*\(.+\)?')

        testes = [
            'WordTree::WordNode *AddHelper(const string word, WordNode *)',
            'WordNode *AddHelper(const string word, WordNode *)',
            'void outputHelper(ostream &output, const WordNode *) const;'
            'int NumWordsHelper(const WordNode *curr) const;',
            'void copy(const WordTree &wordTree);',
            '    bool operator==(const int id) const;',
            'bool operator<(const Client &right) const;',
            'WordNode();',
            '   Test();',
            'void Transaction::print(const int client_id) const {',
            'WordTree::WordNode::WordNode(const string word, WordTree::WordNode *left,',
            'void WordTree::outputHelper(ostream &output, const WordNode *curr) const {'
        ]

        for test in testes:
            # print(test)
            self.assertTrue(re.match(match_function, test))
        tests = [
            'private:',
            'struct WordNode {',
            '* assign the given wordTree to curr tree',
            'extern const int ACCOUNT_ID_MAX;    // THE MAX of account number',
            'class Client {'
        ]

        for test in tests:
            self.assertFalse(re.match(match_function, test))

    def test_read_header(self):
        # /home/k/Dropbox/Clion/css342/as5-p/Test
        d = sh2s.read_header('/home/k/Dropbox/Clion/CSS343/AS1-BST/WordTree')
        # d = sh2s.read_header('/home/k/Dropbox/Clion/css342/as5-p/Test')
        # for k, v in d.items():
        #     print(k, v)
        # self.fail()
        self.assertTrue(1)
        pass

    def test_read_source(self):
        # /home/k/Dropbox/Clion/css342/as5-p/Test
        d = sh2s.read_header('/home/k/Dropbox/Clion/CSS343/AS1-BST/WordTree')
        sh2s.read_source_file('/home/k/Dropbox/Clion/CSS343/AS1-BST/WordTree.cpp')
        # d = sh2s.read_header('/home/k/Dropbox/Clion/css342/as5-p/Test')

        self.fail()
        # self.assertTrue(1)
        pass
