#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import collections
from subprocess import *

'''
This program assumes the code is well formatted by IDE although
it tries to format the code as much as possible.

Read comments from .h file and insert them into the .cpp file.
Always update the comments from .h to .cpp file. The old
comments in .cpp file will be deleted.

Generate the file header in a block file comment based on users
input such as author, file, etc.
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
        self.file_comments = {}
        self.only_update_file_comments = False

    def match_fun_name(self, line: str) -> int:
        """

        :param line: one line of code
        :return:    0 => not function name;
                    1 => function name;
                   -1 => not sure. or keep going
        """
        # TODO work on the -1 part.
        match_function = self._match_function

        # =(?!=) does not work for ==
        no_equal_out_parentheses = re.compile(r'.*?(?<!operator)\s*=(?!=).*?\(', re.MULTILINE)
        a_operator_overloading = re.compile(r'.*?operator\s*(={1,2})', re.MULTILINE)
        if re.search(match_function, line):
            if re.search(no_equal_out_parentheses, line) \
                    and not re.search(a_operator_overloading, line):
                return 0
            else:
                return 1

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

            # remove variables
            remove_var = re.compile(r"""
                        (?P<g1>
                            (const    # starts with constant
                            \s+
                            )?        # some space after const
                            \w+[0-9a-zA-Z]*(::\w+[0-9a-zA-Z]*)*  # Class11a or Class::class::class
                            (\s*(\*\s*)*\s*&*)?     # space and * or ** or *& after that or nothing
                        )

                        """, re.VERBOSE)

            # TODO  this statement does not work!!!!!
            # remove_var.sub(r'\g<g1>', p2)
            try:
                p2 = remove_var.search(p2).group()
            except Exception:
                pass

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

        # replace \t with four space
        line = re.sub(r'\t', '    ', line)
        return re.sub(r'\s+', ' ', line)

    def read_header(self, file_name: str) -> {str: [str]}:
        """
        read comments from header file.
            The comments will be put in a dictionary with func name as the key
            and comments as the value
        :param file_name: the file name of a header file
        """
        # TODO optimize the reading. multi-line function does not work well
        # TODO if the line break is before (
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

                # skip the class forward declaration
                if temp_line.endswith(';'):
                    continue
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
                    while ')' not in line:
                        line = line[:-1] + lines[i].lstrip()
                        i += 1
                    assert (')' in line)
                    name = self.extract_function_name(line)
                    # print(name , 'in frient')
                    comments[name] = comment.copy()
                    comment.clear()
                elif temp_line == '\n':
                    comment.append(line)
                elif self.match_fun_name(line) == 1:
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
                    # print(class_levels, comment)
                    if class_levels:
                        comment.clear()  # testing
                    continue

                    # print(line, '##################no match')
        # print(comments)
        return comments

    def write_source_file(self, file_name: str, comments: {str: [str]}) -> [str]:
        """
        Write the comments to a source file.
        :param file_name: the file name of a source file
        :param comments: the list of comments
        :return: [function names]
        """
        print(file_name, os.getcwd())
        is_in_function = []
        # comments = self.read_header('/home/k/Dropbox/Clion/CSS343/AS1-BST/WordTree')

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
            in_string = ""
            in_parentheses = []
            for s in string:
                if not in_string:
                    if s == '"' or s == "'":
                        in_string = s
                        continue
                else:
                    if s == in_string:
                        in_string = ''
                    continue

                if not in_parentheses:
                    if s == '(':
                        in_parentheses.append(s)
                        continue
                else:
                    if s == ')':
                        in_parentheses.pop()
                    continue

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

            # match function name line
            if self.match_fun_name(line) == 1:

                function_lines.append(line)
                if not is_in_function:

                    # get full function name
                    while ')' not in line:
                        # print(line)
                        line = line.rstrip() + lines[i].lstrip()
                        function_lines.append(lines[i])
                        i += 1
                    func = self.unify_function_name(line)
                    func_names.append(func)

                maintain_func_scope(line)
            else:
                if is_in_function:
                    function_lines.append(line)

                else:

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
            # print(is_in_function, function_lines)
            # insert the comments for each function
            if not is_in_function and function_lines:

                # remove extra empty lines for the source code
                while updated_source_lines and not updated_source_lines[-1].strip():
                    updated_source_lines.pop()

                updated_source_lines += ['\n'] + comments.get(func_names[-1], []) + function_lines
                function_lines.clear()

        # check whether all the functions are in header file
        for func in func_names:
            if func not in comments:
                print(func, ' not fund')
        # for line in updated_source_lines:
        #     print(line)
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
            check_output('cp "{}" "{}/{}"'
                         .format(file_name, back_up_folder, file_name + '.bak'), shell=True)
        except Exception as e:
            print(e)
            raise Exception('Error! Cannot create backup of {}'.format(file_name))

        return True

    def update_headers_for_each_code_file(self) -> None:
        if not self.file_comments:
            return
        file_names = self.get_code_file_names()
        for file_name in file_names:
            self.update_headers_for_code_file(file_name, self.file_comments.copy())

    def update_headers_for_code_file(self, file_name, info: {str: str}) -> None:
        """
        The comment block must in the top the file.
        Nothing before this block.
        In addition, the comment must start with /*

        :param file_name:
        :param info:
        """
        os.chdir(self.path)

        with open(file_name, 'r') as file:
            lines = file.readlines()
        block = []
        block_end = -1
        for i, line in enumerate(lines):
            # not in comment block and not starts with /* and not empty line
            if not block:
                if not re.search(r'^\s*/\*', line) and not line.strip() == '':
                    # no file comment was found
                    break
                else:
                    if line.strip() == '':
                        continue
                    else:
                        block.append(line)
            else:
                block.append(line)
                if re.search(r'\*/$', line):
                    block_end = i + 1
                    break
        string_block = str(block)
        extra_info_in_block = []
        if block:
            if not re.search(r'[@|\\](\w+)[\s|:]', string_block):
                block = []
                block_end = -1
        if block:
            for line in block:
                groups = re.search(r'[@|\\](\w+)[\s*:?\s*](.*)', line.rstrip())
                if groups:
                    # print(groups.groups())
                    k, v = groups.groups()
                    # print(k, v)
                    if k not in info:
                        info[k] = v.strip()
                else:
                    extra_info_in_block.append(line)

        block = []
        self.append_block_comment(block, '/**\n', False)
        if 'file' in info:
            del info['file']
        max_len_key = max(len(k) for k in info.keys()) + 1

        self.append_block_comment(block, '* @{:<{}} {}\n'.format("file", max_len_key, file_name))
        for k in sorted(info.keys()):
            self.append_block_comment(block, '* @{:<{}} {}\n'.format(k, max_len_key, info[k]))
        for line in extra_info_in_block:
            if re.search(r'(^\s*/\*)|(\*/$)', line):
                continue
            self.append_block_comment(block, line)
        self.append_block_comment(block, '*/\n')

        if block_end < 0:
            lines = block + lines
        else:
            lines = block + lines[block_end:]

        with open(file_name, 'w') as file:
            file.writelines(lines)

    def get_code_file_names(self) -> [str]:
        if not self.file_names:
            self.file_names = os.listdir('.')
            self.file_names = [
                file for file in self.file_names if
                re.match(r'^[^.].*?\.(cpp|h)$', file)
                ]
        return self.file_names

    def perform_args(self):
        args = sys.argv
        args_len = len(args)
        if args_len > 1:
            # has args to deal with
            i = 1
            while i < args_len:
                if args[i] == '-extension':
                    i += 1
                    try:
                        self.header_extension, self.source_extension = args[i].split('|')
                    except IndexError:
                        raise IndexError('No extension pairs found! i.e.: h|cpp')
                    except ValueError:
                        raise ValueError('Wrong extension pairs format! i.e.: h|cpp')
                    except Exception as e:
                        print("Unknown error!", e)
                        raise Exception(e)
                elif args[i] == '-fc' or args[i] == '-fc-only':
                    i += 1
                    try:
                        comments = args[i].split('|')
                        for comment in comments:
                            k, self.file_comments[k] = comment.split(':')
                        if args[i] == '-fc-only':
                            self.only_update_file_comments = True
                    except IndexError:
                        raise IndexError('No file comments found! i.e.: author:Bill|date:2017.01.01')
                    except ValueError:
                        raise ValueError('Wrong file comments format! i.e.: author:Bill|date:2017.01.01')
                    except Exception as e:
                        print("Unknown error!", e)
                        raise Exception(e)
                else:
                    raise SyntaxError('Wrong arguments! {}'.format(args[i]))

                i += 1

    def run(self):
        self.perform_args()
        file_names = self.get_code_file_names()
        # print(file_names)
        if not self.only_update_file_comments:
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
                        print('If you used any nested struct or class, '
                              'please make sure you used :: all the time!')
        self.update_headers_for_each_code_file()
        print('Finished')


if __name__ == '__main__':
    # print(sys.argv)
    sh2s = Sh2s(path=os.getcwd())
    sh2s.run()
