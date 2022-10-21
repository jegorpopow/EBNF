import sublime
import sublime_plugin

import re

class TransformCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        for region in selection:
            region_text = self.view.substr(region)
            trasformed_text = self.trasformed_text(region_text)
            self.view.replace(edit, region, trasformed_text)

    def is_enabled(self):
        return len(self.view.sel()) > 0
    
    def split(self, string, char):
        last = 0
        stack = []
        res = []
        match = {
            ')': '(',
            ']': '[',
            '}': '{',
        }
        count = 0
        for i, c in enumerate(string):
            if (count == 0) and (c in '([{'):
                stack.append(c)
            if (count == 0) and (c in ')]}'):
                if (len(stack) == 0) or (stack[-1] != match[c]):
                    return string
                if stack[-1] == match[c]:
                    stack.pop()
            if c == '"':
                if (i == 0) or (string[i - 1] != '\\'):
                    count += 1
                    count %= 2
            if (c == char) and (count == 0) and (len(stack) == 0):
                res.append(string[last:i])
                last = i + 1
        res.append(string[last:])
        return res

    def can_remove_brackets(self, string):
        return len(self.split(string, '|')) == 1

    def remove_brackets(self, string):
        last = 0
        stack = []
        res = string
        match = {
            ')': '(',
            ']': '[',
            '}': '{',
        }
        count = 0
        for i, c in enumerate(string):
            if (count == 0) and (c == '('):
                stack.append(i)
            if (count == 0) and (c == ')'):
                if (len(stack) == 0) or (string[stack[-1]] != match[c]):
                    return string
                if self.can_remove_brackets(string[stack[-1] + 1: i]):
                    res = res[:stack[-1]] + ' ' + res[stack[-1] + 1:]
                    res = res[:i] + ' ' + res[i + 1:]
                stack.pop()
            if c == '"':
                if (i == 0) or (string[i - 1] != '\\'):
                    count += 1
                    count %= 2
        return res


    def transform_without_brackets(self, expr):
        res = ''
        if re.match("\s*\|", expr):
            res = ' | '
        symbols_pre = [[s1 for s1 in re.split('\s+', s) if s1 != ''] for s in self.split(expr, '|')]
        symbols = [list(i) for i in set(tuple(i) for i in symbols_pre)]
        start_symbol_dict = {}
        start_symbol_compressed = {}
        end_symbol_dict = {}
        for i, s in enumerate(symbols): 
            if len(s) == 0:
                continue

            if s[0] not in start_symbol_dict.keys():
                start_symbol_dict[s[0]] = []
            start_symbol_dict[s[0]].append(i)
            start_symbol_compressed[s[0]] = False
        
        for i, s in enumerate(symbols): 
            if len(s) == 0:
                continue
            if s[-1] not in end_symbol_dict.keys():
                end_symbol_dict[s[-1]] = [] 
            if len(start_symbol_dict[s[0]]) == 1:
                end_symbol_dict[s[-1]].append(i)

        for start in start_symbol_dict.keys():
            if len(start_symbol_dict[start]) == 1:
                if not start_symbol_compressed[start]:
                    if len(end_symbol_dict[symbols[start_symbol_dict[start][0]][-1]]) == 1:
                        res += ' '.join(symbols[start_symbol_dict[start][0]]) + ' | '
                    else:
                        res += '('
                        for i in end_symbol_dict[symbols[start_symbol_dict[start][0]][-1]]:
                            cur_s = symbols[i]
                            res += ' '.join(cur_s[:-1]) + ' | '
                            start_symbol_compressed[cur_s[0]] = True
                        res = res[:-3]
                        res += ') ' + symbols[start_symbol_dict[start][0]][-1] + ' | '
            else:
                res += start + ' ('
                for i in start_symbol_dict[start]:
                    cur_s = symbols[i]
                    res += ' '.join(cur_s[1:]) + ' | '
                res = res[:-3]
                res += ') | '

        if res != ' | ':
            res = res[:-3] 

        return res



    def transform_expr(self, expr):
        brackets = []
        res = ''
        count = 0
        for i, c in enumerate(expr):
            if c == '"':
                if (i == 0) or (expr[i - 1] != '\\'):
                    count += 1
                    count %= 2
            if (count == 0) and (c in '([{}])'):
                if len(brackets) == 0:
                    res += self.transform_without_brackets(expr[0 : i]) + c
                else:
                    res += self.transform_without_brackets(expr[brackets[-1] + 1: i]) + c
                brackets.append(i)
        if len(brackets) == 0:
            a = 0
        else:
            a = brackets[-1] + 1
        res += self.transform_without_brackets(expr[a:])
        return res

    def transform_line(self, line):
        splitted = re.split("(\s*<\S*>\s*:=\s*)", line)
        if len(splitted) == 1:
            return line
        else:
            old = splitted[-1]
            res = self.transform_expr(splitted[-1])
            while res != old:
                old = res
                res = self.remove_brackets(self.transform_expr(res))
            return splitted[1] + res

    def trasformed_text(self, text):
        lines = text.split('\n')
        res = []
        for line in lines:
            res.append(self.transform_line(line))
        return '\n'.join(res)