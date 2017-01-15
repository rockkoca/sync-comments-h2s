import os
import re
import collections

'''
This program assumes the code is well formatted by IDE

Read comments from .h file and insert them into the .cpp file.
Always update the comments from .h to .cpp file. The old
comments in .cpp file will be deleted.

Generate the file header in a block file comment.
    (including author, version, etc)
'''


class Sh2s(object):
    _file_comment_key = 'file_comment'
    _source_name = 'source_name'
    _match_function = re.compile(r'^\s*\t*~?\w+:{0,2}\w*\s*.*\(.+\)?')

    def __init__(self, path: str):
        if not os.path.isdir(path):
            raise Exception('The path is not a dir!')
        os.chdir(path)
        self.file_names = []
        self.path = path

    def read_header(self, file_name: str) -> {str: [str]}:
        """

        :param file_name:
        """
        comments = {}
        comment = []  # hold single comment block
        comments[self._source_name] = file_name + '.cpp'
        file_name += '.h'
        class_levels = collections.deque([])
        lines = []
        inside_block_comment = False

        # starts with space or tab or letters, optional two ::
        # some letters and anything until (
        # ) could be in next line
        match_function = self._match_function

        match_friend = re.compile(r'^\s*\t*friend')

        # hold all the comments
        # key is the full method name including the class name
        # value is the comment block

        with open(file_name) as file:
            lines = file.readlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            i += 1
            # print(comment, line)

            temp_line = line.strip().lower()
            # replace all the double space with one
            temp_line = self.replace_double_space(temp_line)
            if temp_line.startswith('class') or temp_line.startswith('struct'):
                inside_block_comment = False
                class_levels.append(self.extract_class_name(line))
                # print('is class', line, comment)

                # if meet a class or sturct and the file_comment is empty
                # add the current comment to the file comment
                # if already has file comment, probably the comment is for a class
                # todo skip for now
                if self._file_comment_key not in comments:
                    comments[self._file_comment_key] = comment.copy()
                # print(comments, 'in class')
                comment.clear()
            elif temp_line.startswith('/*'):
                inside_block_comment = True
                comment.append(line)
            elif temp_line.endswith('*/'):
                inside_block_comment = False
                comment.append(line)
            elif temp_line.startswith('//'):
                # line comment??
                # TODO thinking about this case
                # print(line)
                comment.append(line)
            else:
                # skip include and define etc
                if temp_line.startswith('#'):
                    continue
                # friend functions
                elif re.search(match_friend, line):
                    name = self.extract_function_name(line)
                    # print(name , 'in frient')
                    comments[name] = comment.copy()
                    comment.clear()
                elif temp_line == '\n':
                    comment.append(line)
                elif re.match(match_function, line):
                    """if this line is the function"""

                    '''if ) not in this line, loop until find it'''
                    while ')' not in line:
                        line = line[:-1] + lines[i].lstrip()
                        i += 1
                    assert (')' in line)
                    name = self.extract_function_name(line)

                    # constructor and function are different
                    match_constructor = re.compile(r'^\s*\t*~?\w+\s*\(')
                    re_type = ''
                    starts = ''
                    if not re.search(match_constructor, name):
                        temp = name.split(' ')
                        re_type = temp[0]
                        name = ' '.join(temp[1:])
                        if re.search(r'(^(\*|&))\w+', name):
                            # print(name)
                            starts = name[0]
                            name = name[1:]

                    # build the full function name with class name
                    class_levels.append(name)
                    name = '::'.join(class_levels)
                    class_levels.pop()
                    if starts:
                        name = starts + name
                    if re_type:
                        name = re_type + ' ' + name

                    # print(name, '###################in function')
                    comments[name] = comment.copy()
                    comment.clear()
                elif re.search('}\s*;', line):
                    '''end of the class'''
                    class_levels.pop()
                elif inside_block_comment:
                    comment.append(line)
                else:
                    continue
                    # print(line, '##################no match')
        return comments

    @staticmethod
    def extract_class_name(line: str) -> str:
        return line.replace('class', '') \
            .replace('struct', '').replace('{', '').strip()

    @staticmethod
    def extract_function_name(line: str) -> str:
        return Sh2s.unify_function_name(line.replace('friend', ''))

    @staticmethod
    def unify_function_name(line: str) -> str:
        line = re.sub(';|\{|}', "", line).strip()
        no_pram = re.compile(r'\(\s*\)')
        if re.search(no_pram, line):
            return re.sub(no_pram, '()', line)

        const = False
        line = Sh2s.replace_double_space(line)

        # remove the end const
        match_const = re.compile(r'const\s*;?$')
        if re.search(match_const, line):
            const = True
            line = re.sub('const$', '', line.strip())
            line = line.rstrip()

        # remove the )
        line = re.sub('\)', '', line.strip())
        # line = line.replace(')', '')
        assert (')' not in line)
        parts = line.split('(')
        # print(parts)

        # remove all the variable name
        part2s = parts[-1].split(',')
        for i, p2 in enumerate(part2s):
            p2 = p2.strip()
            print(p2, part2s, line)
            while p2[-1].isalpha() or p2[-1] == '_' or '=' in p2:
                p2 = p2[:-1]
            part2s[i] = p2.rstrip()
        part2 = ", ".join(part2s)
        parts[-1] = part2
        # print(parts)
        # assert (')' not in s for s in parts)
        result = '('.join([s.strip() for s in parts]) + ')' + (' const' if const else '')
        return Sh2s.format_asterisk_ampersand(result)

    @staticmethod
    def format_asterisk_ampersand(line: str) -> str:
        """
        limitation: does not deal with * * or * &
        This program assumes the the code is well formatted by IDE

        :param line:
        :return:
        """
        # todo use regex could be more efficient
        # letter + *
        # ls = re.compile(r'\w*\*')
        if ('*' in line and ' *' not in line) or ('&' in line and ' &' not in line):
            line2 = ''
            for s in line:
                if (s == '&' or s == '*') and line2[-1].isalpha():
                    line2 += ' ' + s
                else:
                    line2 += s
            return line2
        return line

    @staticmethod
    def replace_double_space(line: str) -> str:
        while "  " in line:
            line = line.replace("  ", ' ')
        return line

    def read_source_file(self, file_name: str) -> None:
        is_in_function = []
        d = self.read_header('/home/k/Dropbox/Clion/CSS343/AS1-BST/WordTree')
        with open(file_name, 'r') as file:
            for line in file:
                if re.search(self._match_function, line):
                    if not is_in_function:
                        func = self.unify_function_name(line)
                        if func not in d:
                            print('*' * 100)
                            print(func)
                if '{' in line:
                    is_in_function.append('{')
                if '}' in line:
                    is_in_function.pop()



