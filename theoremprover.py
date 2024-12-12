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
        if a=="U":
            exit(f"Name Error: cannot use name 'U'")
        A_beta = beta_reduce(A)
        print("A :", stringify(A))
        print("A_beta :", stringify(A_beta))
        A_t = get_type(A_beta)
        if A_t !="U":
            exit(f"Type Error: '{stringify(A)}' has type '{stringify(A_t)}' but is supposed to have type 'U'")
        x_beta = beta_reduce(x)
        x_t = get_type(x_beta)
        if not alpha_equiv(x_t, A_beta):
            exit(f"Type Error: '{stringify(x)}' has type '{stringify(x_t)}' but is supposed to have type '{stringify(A_beta)}'")
        add(a, A_beta, x_beta)

def stringify(expr):
    match expr:
        case [arrow, a, A, B]:
            return f"({a} : {stringify(A)}) {arrow} {stringify(B)}"
        case ['application', f, a]:
            return f"({stringify(f)}) ({stringify(a)})"
        case a:
            return a

def substitute(expr, new, old):
    match expr:
        case [arrow, a, A, B]:
            return [arrow, a, substitute(A, new, old), B if a==old else substitute(B, new, old)]
        case ['application', f, a]:
            return ['application', substitute(f, new, old), substitute(a, new, old)]
        case a:
            return new if a==old else a

def add(a, A, x=None):
    global context
    if a != "_":
        context.append((a, A) if x is None else (a, A, x))

def remove(a):
    global context
    if a != "_":
        context.pop()

def get(a):
    global context
    for i in range(len(context)-1, -1, -1):
        if context[i][0]==a:
            return context[i]
    exit(f"Context Error: unknown variable '{a}'")

def unfold(a):
    tupl = get(a)
    return tupl[2] if len(tupl)==3 else a

#Beta reduction unfolds definitions and transforms ((a : A) => b) x into b[x/a]
def beta_reduce(a):
    match a:
        case [arrow, a, A, B]:
            if a=="U":
                exit(f"Name Error: cannot use name 'U'")
            A_beta = beta_reduce(A); add(a, A_beta); B_beta = beta_reduce(B); remove(a)
            return [arrow, a, A_beta, B_beta]
        case ['application', f, a]:
            f_beta, a_beta = beta_reduce(f), beta_reduce(a)
            match f_beta:
                case ["=>", x, A, B]:
                    a_t = get_type(a_beta)
                    if not alpha_equiv(A, a_t):
                        exit(f"Type Error: '{stringify(a)}' has type '{stringify(a_t)}' but is applied on '{stringify(f)}' of type '{stringify(get_type(f_beta))}'")
                    return beta_reduce(substitute(B, a_beta, x))
                case _:
                    return ['application', f_beta, a_beta]
        case a:
            return unfold(a)

def alpha_equiv(a1, a2, i=0):
    match a1, a2:
        case [arrow1, a1, A1, B1], [arrow2, a2, A2, B2]:
            return arrow1==arrow2 and alpha_equiv(A1, A2, i) and alpha_equiv(substitute(B1, i, a1), substitute(B2, i, a2), i+1)
        case [f1, a1], [f2, a2]:
            return alpha_equiv(f1, f2, i) and alpha_equiv(a1, a2, i)
        case a1, a2:
            return a1==a2

def get_type(a):
    match a:
        case ["->", a, A, B]:
            return get_simple_arrow_type(a, A, B)
        case ["=>", a, A, b]:
            return get_double_arrow_type(a, A, b)
        case ["application", f, a]:
            return get_application_type(f, a)
        case a:
            return get_name_type(a)

def get_name_type(a):
    return get(a)[1]

def get_application_type(f, a):
    f_t, a_t = get_type(f), get_type(a)
    match f_t:
        case ['->', x, A, B]:
            if not alpha_equiv(A, a_t):
                exit(f"Type Error: '{stringify(a)}' has type '{stringify(a_t)}' but is applied on '{stringify(f)}' of type '{stringify(get_type(f_beta))}'")
            return beta_reduce(substitute(B, a, x))
        case _:
            exit(f"Type Error: '{stringify(f)}' has type '{stringify(f_t)}' but is applied on '{stringify(a)}' of type '{stringify(a_t)}'")

def get_double_arrow_type(a, A, b):
    A_t = get_type(A)
    if A_t!="U":
        exit(f"Type Error: '{stringify(A)}' has type '{stringify(A_t)}' but is supposed to have type 'U'")
    add(a, A); b_t = get_type(b); remove(a)
    return ["->", a, A, b_t]

def get_simple_arrow_type(a, A, B):
    A_t = get_type(A)
    if A_t!="U":
        exit(f"Type Error: '{stringify(A)}' has type '{stringify(A_t)}' but is supposed to have type 'U'")
    add(a, A); B_t = get_type(B); remove(a)
    if B_t!="U":
        exit(f"Type Error: '{stringify(B)}' has type '{stringify(B_t)}' but is supposed to have type 'U'")
    return "U"

tokens = tokenization("input.in")
i = 0
context = [("U", "U")]
type_checker(parsing())
