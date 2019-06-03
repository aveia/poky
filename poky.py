# encoding: utf-8

'''
poky
an experiment
created on 2019-6-2
'''

import argparse
import math
import sys
from functools import reduce

def read_file(filepath):
    with open(filepath) as f:
        return f.read()

def parse(code):

    code_tree = ['progn']

    stack = [code_tree]

    state = 'whitespace'
    token = ''

    for char in code:

        if state == 'whitespace':

            if 'a' <= char <= 'z' or 'A' <= char <= 'Z' \
                or char in '+-/*!?%<>!=':
                state = 'reading_symbol'
                token += char

            elif '0' <= char <= '9' or char == '.':
                state = 'reading_number'
                token += char

            elif char == ';':
                state = 'comment'

            elif char == '(':
                new_list = []
                stack[-1].append(new_list)
                stack.append(new_list)

            elif char == ')':
                if len(stack) > 1:
                    stack.pop()

        elif state == 'reading_symbol':

            if 'a' <= char <= 'z' or 'A' <= char <= 'Z' \
                or char in '+-/*!?%<>!=':
                token += char

            elif char in ' \t\n':
                state = 'whitespace'
                stack[-1].append(token)
                token = ''

            elif char == ';':
                state = 'comment'
                stack[-1].append(token)
                token = ''

            elif char == '(':
                state = 'whitespace'
                stack[-1].append(token)
                token = ''
                new_list = []
                stack[-1].append(new_list)
                stack.append(new_list)

            elif char == ')':
                state = 'whitespace'
                stack[-1].append(token)
                token = ''
                if len(stack) > 1:
                    stack.pop()

        elif state == 'reading_number':

            if 'a' <= char <= 'z' or 'A' <= char <= 'Z' \
                or char in '+-/*!?%<>!=':
                state = 'reading_symbol'
                token += char

            elif '0' <= char <= '9' or char == '.':
                token += char

            elif char in ' \t\n':
                state = 'whitespace'
                value = float(token) if '.' in token else int(token)
                stack[-1].append(value)
                token = ''

            elif char == ';':
                state = 'comment'
                value = float(token) if '.' in token else int(token)
                stack[-1].append(value)
                token = ''

            elif char == '(':
                state = 'whitespace'
                value = float(token) if '.' in token else int(token)
                stack[-1].append(value)
                token = ''
                new_list = []
                stack[-1].append(new_list)
                stack.append(new_list)

            elif char == ')':
                state = 'whitespace'
                value = float(token) if '.' in token else int(token)
                stack[-1].append(value)
                token = ''
                if len(stack) > 1:
                    stack.pop()

        elif state == 'comment':

            if char == '\n':
                state = 'whitespace'

    return code_tree

def _sum(*args):
    return reduce(lambda x, y: x + y, args, 0)

def _subtract(*args):
    if len(args) == 1:
        return - args[0]
    else:
        return reduce(lambda x, y: x - y, args)

def _multiply(*args):
    return reduce(lambda x, y: x * y, args, 1)

def _divide(*args):
    return reduce(lambda x, y: x / y, args)

def _lesser(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if args[i - 1] >= args[i]:
            return False
    return True

def _lesser_equal(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if args[i - 1] > args[i]:
            return False
    return True

def _greater(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if args[i - 1] <= args[i]:
            return False
    return True

def _greater_equal(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if args[i - 1] < args[i]:
            return False
    return True

def _equal(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if args[i - 1] != args[i]:
            return False
    return True

def _not_equal(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if args[i - 1] == args[i]:
            return False
    return True

def evaluate(thing, context):

    print('evaluating:', thing, file=sys.stderr)

    value = None

    if isinstance(thing, (int, float)):
        value = thing

    elif isinstance(thing, str):
        for scope in context:
            if thing in scope:
                value = scope[thing]
                break

    elif isinstance(thing, list):

        if not thing:
            pass

        elif thing[0] == 'progn':

            for x in thing[1:]:
                value = evaluate(x, context)

        elif thing[0] == 'scope':

            new_scope = {}

            for x in thing[1:]:
                value = evaluate(x, [new_scope] + context)

        elif thing[0] == 'if':

            args = thing[1:]

            if len(args) >= 2:

                cond = evaluate(args[0], context)

                if cond:
                    value = evaluate(args[1], context)

                elif len(args) >= 3:
                    value = evaluate(args[2], context)

        elif thing[0] == 'set!':

            scope = context[0]
            args = thing[1:]

            if len(args) % 2 == 0:
                for i in range(1, len(args), 2):
                    if isinstance(args[i - 1], str):
                        scope[args[i - 1]] = evaluate(args[i], context)

        else:
            new_list = [evaluate(x, context) for x in thing]

            operator = new_list[0]
            args = new_list[1:]

            value = operator(*args)

    print('value:', value, file=sys.stderr)
    return value

def interpret(tree):

    global_scope = {
        'pi': 3.1415926535,
        'sqrt': math.sqrt,
        'print': print,
        '+': _sum,
        '-': _subtract,
        '*': _multiply,
        '/': _divide,
        '<': _lesser,
        '<=': _lesser_equal,
        '>': _greater,
        '>=': _greater_equal,
        '=': _equal,
        '!=': _not_equal,
    }

    # scope list
    context = [global_scope]

    return evaluate(tree, context)

def main():

    parser = argparse.ArgumentParser('poky v0')
    parser.add_argument(dest='input_file')

    args = parser.parse_args()

    code = read_file(args.input_file)

    code_tree = parse(code)

    result = interpret(code_tree)

    print('result:', result)

if __name__ == '__main__':
    main()
