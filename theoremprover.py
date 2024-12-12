import re

"""Tokenization"""

def tokenization(path):
    tokens = []
    with open(path, "r") as fd:
        for line in fd:
            tokens += [s for s in re.split(r"( |:|\(|\)|:|;)", line.strip()) if s not in ["", " "]]
    return tokens

"""Parsing"""

def expression():
    global tokens, i
    a = name(); match(":"); A = term(); match("="); x = term(); match(";")
    return [a, A, x]

def name():
    global tokens, i
    if not re.match("^[a-zA-Z_]+$", tokens[i]):
        exit(f"Syntax Error: expected name but got '{tokens[i]}'")
    i+=1
    return tokens[i-1]

def match(*args):
    global tokens, i
    if tokens[i] not in args:
        exit("Syntax Error: expected '" + "' or '".join(args) + f"' but got '{tokens[i]}'")
    i+=1
    return tokens[i-1]

def term():
    global tokens, i
    #If we are in an arrow case
    if i+2 < len(tokens) and tokens[i+2]==":":
        match("("); a = name(); match(":"); A = term(); match(")"); ar = match("=>", "->"); B = term()
        return [ar, a, A, B]
    else:
        res = None
        if tokens[i]=="(":
            match("("); res = term(); match(")");
        else:
            res = name()

        while tokens[i] not in ["=", ")", ";"]:
            if tokens[i]=="(":
                match("("); res = ["application", res, term()]; match(")");
            else:
                res = ["application", res, name()]
            
            if i==len(tokens):
                exit("Syntax Error: end of file reached because of missing ';'")
        return res

def parsing():
    global tokens, i
    expressions = []
    while i<len(tokens):
        expressions.append(expression())
    return expressions

"""Type checking"""

def type_checker(expressions):
    global context
    for [a, A, x] in expressions:
        A_nf = normal_form(A)
        A_t = get_type(A_nf)
        if A_t !="U":
            exit(f"Type Error: '{stringify(A)}' has type '{stringify(A_t)}' but is supposed to have type 'U'")
        x_nf = normal_form(x)
        x_t = get_type(x_nf)
        if x_t!=A_nf:
            exit(f"Type Error: '{stringify(x)}' has type '{stringify(x_t)}' but is supposed to have type '{stringify(A_nf)}'")
        if a!="_":
            context.append((a, A_nf, x_nf))

def stringify(expr):
    match expr:
        case [arrow, a, A, B]:
            return f"({a} : {stringify(A)}) {arrow} {stringify(B)}"
        case ['application', f, a]:
            return f"({stringify(f)}) ({stringify(a)})"
        case s:
            return s

def substitute(expr, new, old):
    match expr:
        case [arrow, a, A, B]:
            return [arrow, a, substitute(A, new, old), B if a==old else substitute(B, new, old)]
        case ['application', f, a]:
            return ['application', substitute(f, new, old), substitute(a, new, old)]
        case s:
            return new if s==old else s

#Normal form converts variables into their definitions if they have one (if replace_defs==True), transforms bounded variables into numbers, and transforms ((a : A) => b) x into b[x/a]
def normal_form(expr, i=0, replace_defs=True):
    match expr:
        case [arrow, a, A, B]:
            return return [arrow, i, normal_form(A, i+1, replace_defs), normal_form(substitute(B, i, a) if a!="_" else "_", i+1, replace_defs)]
        case ['application', f, a]:
            f_nf, a_nf = normal_form(f, i, replace_defs), normal_form(a, i, replace_defs)
            match f_nf:
                case ["=>", x, A, B]:
                    a_t = get_type(a_nf)
                    if A!=a_t:
                        f_t = get_type(f_nf)
                        exit(f"Type Error: '{stringify(a)}' has type '{stringify(a_t)}' but is applied on '{stringify(f)}' of type '{stringify(f_t)}'")
                    return normal_form(substitute(B, a_nf, x), i, replace_defs)
                case _:
                    return ['application', f_nf, a_nf]
        case s:
            if not replace_defs or type(s) is int:
                assert s=="U" or type(s) is int, s
                return s

            for j in range(len(context)-1, -1, -1):
                if context[j][0]==s:
                    return normal_form(context[j][2], i, False) if len(context[j])==3 else s
            
            exit(f"Context Error: unknown variable '{s}'")
        
def get_type(expr):
    match expr:
        case ["->", a, A, B]:
            return get_simple_arrow_type(a, A, B)
        case ["=>", a, A, b]:
            return get_double_arrow_type(a, A, b)
        case ["application", f, a]:
            return get_application_type(f, a)
        case s:
            return get_name_type(s)

def get_name_type(s):
    global context
    for i in range(len(context)-1, -1, -1):
        if context[i][0]==s:
            return context[i][1]
    exit(f"Context Error: unknown variable '{s}'")

def get_application_type(f, a):
    f_type, a_type = get_type(f), get_type(a)
    match f_type:
        case ['->', x, A, B]:
            return substitute(B, a, x)
        case _:
            exit(f"Type Error: '{stringify(f)}' has type '{stringify(f_type)}' but is applied on '{stringify(a)}' of type '{stringify(a_type)}'")

def get_double_arrow_type(a, A, b):
    global context
    A_type = get_type(A)
    if A_type!="U":
        exit(f"Type Error: '{stringify(A)}' has type '{stringify(A_type)}' but is supposed to have type 'U'")
    if a!="_":
        context.append((a, A))
    b_type = get_type(b)
    if a!="_":
        context.pop()
    return ["->", a, A, b_type]

def get_simple_arrow_type(a, A, B):
    global context
    A_type = get_type(A)
    if A_type!="U":
        exit(f"Type Error: '{stringify(A)}' has type '{stringify(A_type)}' but is supposed to have type 'U'")
    if a!="_":
        context.append((a, A))
    B_type = get_type(B)
    if B_type!="U":
        exit(f"Type Error: '{stringify(B)}' has type '{stringify(B_type)}' but is supposed to have type 'U'")
    if a!="_":
        context.pop()
    return "U"

tokens = tokenization("input.in")
i = 0
context = [("U", "U")]
type_checker(parsing())
