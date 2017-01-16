#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import collections
from subprocess import *

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

    def __init__(self, path: str, header_extension: str = '.h',
                 source_extension: str = '.cpp',
                 comment_indent: int = 0):
        if not os.path.isdir(path):
            raise Exception('The path is not a dir!')
        os.chdir(path)
        self.file_names = []
        self.path = path
        self.header_extension = header_extension
        self.source_extension = source_extension
        self.comment_indent = comment_indent

    def read_header(self, file_name: str) -> {str: [str]}:
        """

        :param file_name:
        """
        comments = {}
        comment = []  # hold single comment block
        comments[self._source_name] = file_name + self.source_extension
        file_name += self.header_extension \
            if not file_name.endswith(self.header_extension) else ''
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
                # comment.append(line.lstrip())
                self.append_block_comment(comment, line, body=False)
            elif temp_line.endswith('*/'):
                inside_block_comment = False
                # comment.append(' ' + line.lstrip())
                self.append_block_comment(comment, line)
            elif temp_line.startswith('//'):
                # line comment??
                # TODO thinking about this case
                # print(line)
                # comment.append(line.lstrip())
                self.append_block_comment(comment, line)
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
                    # comment.append(line)
                    # comment.append(' ' + line.lstrip())
                    self.append_block_comment(comment, line)
                else:
                    continue
                    # print(line, '##################no match')
        return comments

    def append_block_comment(self, comment: [str], line: str, body: bool = True) -> None:
        indent = ' ' * self.comment_indent
        line = line.lstrip()

        if body:
            if line.startswith('//'):
                comment.append(indent + line)
            elif line.startswith('*'):
                comment.append(indent + ' ' + line)
            else:
                comment.append(indent + '  ' + line)
        else:
            comment.append(indent + line)

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
            while p2[-1].isalnum() or p2[-1] == '_':
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

    def write_source_file(self, file_name: str, comments: {str: [str]}) -> [str]:
        print(file_name, os.getcwd())
        is_in_function = []
        # comments = self.read_header('/home/k/Dropbox/Clion/CSS343/AS1-BST/WordTree')

        # todo debug only
        # print(comments)
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

        updated_source_lines = comments.get(self._file_comment_key, [])
        function_lines = []
        func_names = []
        inside_comment_block = False
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

            else:

                if is_in_function:
                    function_lines.append(line)

                else:
                    # print(line)
                    # excluding outside comments
                    if re.search(r'^\s*/\*', line.lstrip()):
                        inside_comment_block = True
                    elif re.search(r'\*/\s*', line.rstrip()):
                        inside_comment_block = False
                    else:

                        # if is not comments, collect it
                        if not inside_comment_block and \
                                re.match(r'^\s*[^/{2}].*?', line):
                            # print(line)
                            updated_source_lines.append(line)
                    # print(inside_comment_block)
                maintain_func_scope(line)
            # insert the comments for each function
            if not is_in_function and function_lines:

                # remove extra empty lines for the source code
                while updated_source_lines and not updated_source_lines[-1].strip():
                    updated_source_lines.pop()

                updated_source_lines += ['\n'] + comments.get(func_names[-1], []) + function_lines
                function_lines.clear()
                # print(function)

        # print(func_names, '*' * 100)
        print()
        for func in func_names:
            if func not in comments:
                print(func, ' not fund')

        with open(file_name, 'w') as file:
            file.writelines(updated_source_lines)

        return func_names

    def header_to_source_name(self, header_file: str) -> str:
        return header_file.replace(self.header_extension, '') + \
               self.source_extension

    def back_up_source_file(self, file_name: str) -> bool:
        os.chdir(self.path)
        back_up_folder = '.sh2s_back_up'
        if not os.path.exists(back_up_folder):
            # let it raise Exceptions
            try:
                check_output('mkdir {}'.format(back_up_folder), shell=True)
            except PermissionError:
                print('Permission error! Cannot create backup folder.')
                return False
            except Exception as e:
                print(e)
                raise Exception('Unknown error! Cannot create backup folder.')
        try:
            check_output('cp {} {}/{}'
                         .format(file_name, back_up_folder, file_name + '.bak'), shell=True)
        except Exception as e:
            print(e)
            raise Exception('Error! Cannot create backup of {}'.format(file_name))

        return True

    def run(self):
        self.file_names = os.listdir('.')
        # print(self.file_names)

        file_names = [
            file for file in self.file_names if
            re.match(r'^[^.].*?\.(cpp|h)$', file)
            ]
        # print(file_names)
        for file in self.file_names:

            if file.endswith(self.header_extension):

                source_file = self.header_to_source_name(file)
                if source_file in file_names:
                    # if both header file and source file are in this dir
                    self.back_up_source_file(source_file)
                    comments = self.read_header(file)
                    self.write_source_file(source_file, comments)
                else:
                    print(source_file, 'does not exist!')

        print('Success')


if __name__ == '__main__':
    print(sys.argv)
    sh2s = Sh2s(path=os.getcwd())
    sh2s.run()
