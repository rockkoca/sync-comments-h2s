from unittest import TestCase
from sync_comment_h2s import *

my_path = "/".join(os.path.realpath(__file__).split('/')[:-1])
os.chdir(my_path)
sh2s = Sh2s(my_path)


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
        test = 'WordTree    ::    WordNode *AddHelper(const string word, WordNode *)'
        self.assertEqual(result, Sh2s.unify_function_name(test))

        result = 'int getHelper(const string, const WordNode *) const'
        test = '       int            getHelper(         const    ' \
               'string word, const WordNode *curr)                 const;'
        self.assertEqual(result, Sh2s.unify_function_name(test))

        result = 'WordTree &WordTree::operator=(const WordTree &)'
        test = 'WordTree &WordTree::operator     =     (const WordTree         &      right)'
        self.assertEqual(result, Sh2s.unify_function_name(test))

        result = 'WordTree &WordTree::operator=(const WordTree)'
        test = 'WordTree &WordTree::operator     =     (const WordTree            right)'
        self.assertEqual(result, Sh2s.unify_function_name(test))

        result = 'Movie::Movie(const string)'
        test = 'Movie::Movie(const string "sdf")'
        self.assertEqual(result, Sh2s.unify_function_name(test))

        test1 = 'WordNode(const string word, WordTree::WordNode *left,' \
                'WordTree::WordNode *right, const int count) {'
        test2 = 'WordNode(const string word, WordTree::WordNode *left = nullptr,' \
                'WordTree::WordNode *right = nullptr, const int count = "ok")'
        self.assertEqual(Sh2s.unify_function_name(test1),
                         Sh2s.unify_function_name(test2))

        result = 'void Test_sh2s::doSomething1Helpers(Test_sh2s::Node *)'
        test = 'void Test_sh2s::doSomething1Helpers(Test_sh2s::Node *head)'
        self.assertEqual(result, Sh2s.unify_function_name(test))

    def test_format_asterisk_ampersand(self):
        result = 'int getHelper(const string &, const WordNode *&);'
        test = 'int getHelper(const string&, const WordNode*&)       ;'
        self.assertEqual(result, Sh2s.format_asterisk_ampersand_comma_parentheses(test))

        result = 'int getHelper(const string *, const WordNode *&) const'
        test = 'int getHelper(const string*, const WordNode*&) const'
        self.assertEqual(result, Sh2s.format_asterisk_ampersand_comma_parentheses(test))

        result = 'int getHelper(const string **, const WordNode *&) const'
        test = 'int getHelper  (    const string*      *, const WordNode*         &   )    const'
        self.assertEqual(result, Sh2s.format_asterisk_ampersand_comma_parentheses(test))

        result = 'int getHelper(const string **str, const WordNode *&) const'
        test = 'int getHelper  (    const string*      *  str, const WordNode*         &   )    const'
        self.assertEqual(result, Sh2s.format_asterisk_ampersand_comma_parentheses(test))

    def test_extract_class_name(self):
        result = ['WordNode']
        test = 'struct WordNode {'
        self.assertEqual(result, Sh2s.extract_class_name(test))

        result = ['Node', 'WordNode']
        test = 'class WordNode : public Node {'
        self.assertEqual(result, Sh2s.extract_class_name(test))

        result = ['SuperSuper', 'Super', 'WordNode']
        test = 'class WordNode : private Super : public SuperSuper {}'
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
            'void WordTree::outputHelper(ostream &output, const WordNode *curr) const {',
            'void KevinBaconGame::readDatabase(ifstream &infile) {'
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

    def test_read_source_and_header(self):
        d = sh2s.read_header('test_sh2s.h')
        names = sh2s.write_source_file('test_sh2s.cpp', d)
        # for k, v in d.items():
        #     print(k, v)
        for name in names:
            self.assertTrue(name in d)

        output = open('test_sh2s.cpp', 'r')
        correct_output = open('test_sh2s_correct.cpp', 'r')
        for l1, l2 in zip(output, correct_output):
            self.assertEqual(l1, l2)

        names = sh2s.write_source_file('/home/k/Desktop/KevinBaconGame.cpp', {})
        print(names)

    def test_update_headers_for_code_file(self):
        sh2s.update_headers_for_code_file('test_sh2s.cpp', {'author': 'Koca'})
