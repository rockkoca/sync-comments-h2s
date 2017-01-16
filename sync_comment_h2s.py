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
                class_levels.append(self.extract_class_name(line)[-1])
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
    def extract_class_name(line: str) -> [str]:
        """
        return a list, the last element is the current class name
        the first is top level class that this class derived from
        :param line:
        :return: [supers, class name]
        """
        # TODO Multiple Inheritance is not considered yet,
        # TODO They go to each level and separated with a comma

        line = re.sub(r'\s*(struct|class|public|private|protected)\s+|(\{|})',
                      ' ', line)
        # print([s.strip() for s in line.split(':')][::-1])
        return [s.strip() for s in line.split(':')][::-1]

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

            # print(p2, part2s, line)
            while p2[-1].isalpha() or p2[-1] == '_':
                p2 = p2[:-1]
            if '=' in p2:
                p2 = re.sub(r'\s*\w+_?\w*\s*=\s*.+$', '', p2)

            p2 = re.sub(r'(\*)\w+\s*$', '*', p2)
            p2 = re.sub(r'(&)\w+\s*$', '&', p2)

            part2s[i] = p2.rstrip()
        part2 = ", ".join(part2s)
        parts[-1] = part2
        # print(parts)
        # assert (')' not in s for s in parts)
        result = '('.join([s.strip() for s in parts]) + ')' + (' const' if const else '')
        return Sh2s.format_asterisk_ampersand_comma_parentheses(result)

    @staticmethod
    def format_asterisk_ampersand_comma_parentheses(line: str) -> str:
        """
        This program assumes the the code is well formatted by IDE.
        These id no guarantee for the following this function.
        :param line: a function line
        :return: formatted function
        """
        # todo use regex could be more efficient
        # no more than one space between anything
        line = re.sub(r'(\w+)\s*(\*|&)', r'\1 \2', line)

        # remove extra space between * and & or *
        line = re.sub(r'\*\s+(&|\*)', r'*\1', line)

        # remove extre space between(* or &) between letters
        line = re.sub(r'(\*|&)\s*(\w+)', r'\1\2', line)

        # no space before or after '('
        line = re.sub(r'(.*?)\s+(\()\s+(.*?)', r'\1\2\3', line)

        # no space before ')', no more than one space after ')'
        line = re.sub(r'(.*?)\s+(\))\s+(.*?)', r'\1\2 \3', line)

        # no space between ')' and ';'
        line = re.sub(r'\)\s+;', ');', line)

        # no space before and after '::'
        line = re.sub(r'(.*?)\s+::\s+(.*?)', r'\1::\2', line)

        # no space between 'operator' and operators
        line = re.sub(r'operator\s+(.)', r'operator\1', line)
        return line

    @staticmethod
    def replace_double_space(line: str) -> str:
        # while "  " in line:
        #     line = line.replace("  ", ' ')
        return re.sub(r'\s+', ' ', line)

    def write_source_file(self, file_name: str) -> [str]:
        is_in_function = []
        d = self.read_header('/home/k/Dropbox/Clion/CSS343/AS1-BST/WordTree')

        # todo debug only
        print(d)
        lines = []
        with open(file_name, 'r') as file:
            lines = file.readlines()
        i = 0

        def maintain_func_scope(string: str) -> None:
            # print(is_in_function)
            """
            Maintain func scope by counting the number of { and }
            :param string: a line of code
            """
            for s in string:
                if '{' == s:
                    is_in_function.append('{')
                elif '}' == s:
                    is_in_function.pop()
                    # print('after', is_in_function)

        updated_source_lines = d.get(self._file_comment_key, [])
        function_lines = []
        func_names = []
        while i < len(lines):
            line = lines[i]
            i += 1

            # print(line)

            if re.search(self._match_function, line):

                # print(line)

                function_lines.append(line)
                if not is_in_function:

                    # get full function name
                    while ')' not in line:
                        # print(line)
                        line = line.rstrip() + lines[i].lstrip()
                        function_lines.append(lines[i])
                        i += 1
                    func = self.unify_function_name(line)

                    # print(func)

                    func_names.append(func)
                    # if func in d:
                    #     print('*' * 100)
                    #     print(func)
                maintain_func_scope(line)
                # print()
                # print(function)


            else:
                if is_in_function:
                    function_lines.append(line)
                maintain_func_scope(line)
                # finish a function
            if not is_in_function and function_lines:
                updated_source_lines += ['\n'] + d.get(func_names[-1], []) + function_lines
                function_lines.clear()
                # print(function)

        # print(func_names, '*' * 100)
        print()
        for func in func_names:
            if func not in d:
                print(func, ' not fund')

        with open('/home/k/Dropbox/Clion/CSS343/AS1-BST/WordTree1.cpp', 'w') as file:
            file.writelines(updated_source_lines)

        return func_names
