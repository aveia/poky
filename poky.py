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

def error(*args):
    print(*args, file=sys.stderr)
    sys.exit(1)

def read_file(filepath):
    with open(filepath) as f:
        return f.read()

def to_list(x):
    if not isinstance(x, list):
        return [x]
    return x

class Symbol:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<symbol:{self.name}>'

class Function:
    def __init__(self, name, params, forms):
        self.name = name or Symbol(None)
        self.params = params
        self.forms = forms

    def __repr__(self):
        name = self.name.name
        param_names = [x.name for x in self.params]
        return f'<function:({" ".join([name or "nil"] + param_names)})>'

class Cons:
    def __init__(self, x1, x2):
        self.x1 = x1
        self.x2 = x2

    def __repr__(self):
        s = '('
        cur = self.x1
        nxt = self.x2
        while type(nxt) is Cons:
            s += repr(cur) + ' '
            cur = nxt.x1
            nxt = nxt.x2
        if nxt is None:
            s += repr(cur)
        else:
            s += repr(cur) + ' . ' + repr(nxt)
        s += ')'
        return s

def parse(code):

    code_tree = [Symbol('progn')]

    stack = [code_tree]

    state = 'whitespace'
    token = ''

    last_char = None

    for char in code:

        last_char = char

        if state == 'whitespace':

            if 'a' <= char <= 'z' or 'A' <= char <= 'Z' \
                or char in '+-/*!?%<>!=':
                state = 'reading_symbol'
                token += char

            elif '0' <= char <= '9' or char == '.':
                state = 'reading_number'
                token += char

            elif char == '"':
                state = 'reading_string'

            elif char == ';':
                state = 'comment'

            elif char == '(':
                new_list = []
                stack[-1].append(new_list)
                stack.append(new_list)

            elif char == ')':
                if len(stack) > 1:
                    stack.pop()
                else:
                    error('Unexpected closing parenthesis')

            elif char not in ' \t\n':
                error('Unexpected character: "{}"'.format(char))

        elif state == 'reading_symbol':

            if 'a' <= char <= 'z' or 'A' <= char <= 'Z' \
                or char in '+-/*!?%<>!=' or '0' <= char <= '9':
                token += char

            elif char in ' \t\n':
                state = 'whitespace'
                symbol = Symbol(token)
                stack[-1].append(symbol)
                token = ''

            elif char == ';':
                state = 'comment'
                symbol = Symbol(token)
                stack[-1].append(symbol)
                token = ''

            elif char == '(':
                state = 'whitespace'
                symbol = Symbol(token)
                stack[-1].append(symbol)
                token = ''
                new_list = []
                stack[-1].append(new_list)
                stack.append(new_list)

            elif char == ')':
                state = 'whitespace'
                symbol = Symbol(token)
                stack[-1].append(symbol)
                token = ''
                if len(stack) > 1:
                    stack.pop()
                else:
                    error('Unexpected closing parenthesis')

            else:
                error('Unexpected character: "{}"'.format(char))

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

            else:
                error('Unexpected character: "{}"'.format(char))

        elif state == 'reading_string':

            if char == '\\':
                state = 'reading_escape_sequence'
            elif char == '"':
                state = 'whitespace'
                stack[-1].append(token)
                token = ''
            else:
                token += char

        elif state == 'reading_escape_sequence':

            state = 'reading_string'
            if char == 'n':
                token += '\n'
            elif char == '\n':
                pass
            else:
                token += char

        elif state == 'comment':

            if char == '\n':
                state = 'whitespace'

    if len(stack) > 1:
        error('Unexpected end-of-file: perhaps there are missing parenthesis '
            'at the end')

    if state == 'reading_string':
        error('Unexpected end-of-file: perhaps there is a missing closing '
            'double quote at the end')

    if token:
        if state == 'reading_symbol':
            stack[-1].append(Symbol(token))
        elif state == 'reading_number':
            stack[-1].append(float(token) if '.' in token else int(token))

    if last_char != '\n':
        print('Warning: file does not end in a newline', file=sys.stderr)

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
        if not args[i - 1] < args[i]:
            return None
    return True

def _lesser_equal(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if not args[i - 1] <= args[i]:
            return None
    return True

def _greater(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if not args[i - 1] > args[i]:
            return None
    return True

def _greater_equal(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if not args[i - 1] >= args[i]:
            return None
    return True

def _equal(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if not args[i - 1] == args[i]:
            return None
    return True

def _not_equal(*args):
    if len(args) < 2:
        return True
    for i in range(1, len(args)):
        if args[i - 1] == args[i]:
            return None
    return True

def _list(*args):
    if not args:
        return None
    return Cons(args[0], _list(*args[1:]))

def _cons(x1, x2):
    return Cons(x1, x2)

def _car(cons):
    return cons.x1

def _cdr(cons):
    if cons == None:
        return None
    return cons.x2

def _read_token():
    token = ''
    char = sys.stdin.read(1)
    while char not in '\t\n ':
        token += char
        char = sys.stdin.read(1)
    return token

def _print(*args):
    print(*args, sep='', end='')
    sys.stdout.flush()

def _println(*args):
    print(*args, sep='')

def evaluate(thing, context, debug):

    if debug:
        print('evaluating:', thing, file=sys.stderr)

    value = None

    if isinstance(thing, (int, float, str)):
        value = thing

    elif isinstance(thing, Symbol):

        found = False

        for scope in context:
            if thing.name in scope:
                value = scope[thing.name]
                found = True
                break

        if not found:
            error('Undeclared variable: "{}"'.format(thing.name))

    elif isinstance(thing, list):

        if not thing:
            pass

        elif isinstance(thing[0], Symbol) and thing[0].name == 'progn':

            for x in thing[1:]:
                value = evaluate(x, context, debug)

        elif isinstance(thing[0], Symbol) and thing[0].name == 'def!':

            scope = context[0]

            name = thing[1]
            params = thing[2]
            forms = thing[3:]

            value = scope[name.name] = Function(name, params, forms)

        elif isinstance(thing[0], Symbol) \
            and thing[0].name in ['lambda', 'lb']:

            params = to_list(thing[1])
            forms = thing[2:]

            value = Function(None, params, forms)

        elif isinstance(thing[0], Symbol) and thing[0].name == 'and':

            value = True

            args = thing[1:]
            for x in args:
                value = evaluate(x, context, debug)
                if value is None:
                    break

        elif isinstance(thing[0], Symbol) and thing[0].name == 'or':

            args = thing[1:]
            for x in args:
                value = evaluate(x, context, debug)
                if value is not None:
                    break

        elif isinstance(thing[0], Symbol) and thing[0].name == 'xor':

            found = False

            for x in args:
                curr = evaluate(x, context, debug)
                if curr is not None:
                    if found:
                        value = None
                        break
                    else:
                        value = curr
                        found = True

        elif isinstance(thing[0], Symbol) and thing[0].name == 'scope':

            new_scope = {}

            for x in thing[1:]:
                value = evaluate(x, [new_scope] + context, debug)

        elif isinstance(thing[0], Symbol) and thing[0].name == 'if':

            args = thing[1:]

            if len(args) >= 2:

                cond = evaluate(args[0], context, debug)

                if cond is not None:
                    value = evaluate(args[1], context, debug)

                elif len(args) >= 3:
                    value = evaluate(args[2], context, debug)

        elif isinstance(thing[0], Symbol) and thing[0].name == 'set!':

            scope = context[0]
            args = thing[1:]

            if args and len(args) % 2 == 0:
                for i in range(1, len(args), 2):
                    if isinstance(args[i - 1], Symbol):
                        scope[args[i - 1].name] = \
                            evaluate(args[i], context, debug)

                value = args[-1]

        else:
            new_list = [evaluate(x, context, debug) for x in thing]

            op = new_list[0]
            fn_args = new_list[1:]

            if isinstance(op, Function):

                new_scope = {}
                for symbol, value in zip(op.params, fn_args):
                    new_scope[symbol.name] = value

                value = evaluate(
                    [Symbol('progn')] + op.forms,
                    [new_scope] + context, debug)
            else:
                value = op(*fn_args)

    if debug:
        print('value of {}:'.format(thing), value, file=sys.stderr)

    return value

def interpret(tree, debug):

    global_scope = {
        't': True,
        'nil': None,
        'pi': 3.1415926535,
        'sqrt': math.sqrt,
        'print': _print,
        'println': _println,
        'read-char': lambda: sys.stdin.read(1),
        'read-token': _read_token,
        'read-line': lambda: sys.stdin.readline(),
        'to-integer': int,
        'to-float': float,
        'to-string': str,
        '+': _sum,
        '-': _subtract,
        '*': _multiply,
        '/': _divide,
        'div': lambda x, y: x // y,
        'mod': lambda x, y: x % y,
        '<': _lesser,
        '<=': _lesser_equal,
        '>': _greater,
        '>=': _greater_equal,
        '=': _equal,
        '!=': _not_equal,
        'list': _list,
        'cons': _cons,
        'car': _car,
        'cdr': _cdr,
        'not': lambda x: x is None or None,
        'null?': lambda x: x is None or None,
    }

    # scope list
    context = [global_scope]

    return evaluate(tree, context, debug)

def main():

    parser = argparse.ArgumentParser('poky v0')
    parser.add_argument(dest='input_file')
    parser.add_argument('-d', '--debug',
        dest='debug', action='store_true', default=False)

    args = parser.parse_args()

    code = read_file(args.input_file)

    code_tree = parse(code)

    interpret(code_tree, args.debug)

if __name__ == '__main__':
    main()
