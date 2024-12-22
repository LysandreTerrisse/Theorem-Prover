import re, sys

"""Tokenization"""

def tokenization(path):
    tokens = []
    try:
        with open(path, "r") as fd:
            for line in fd:
                tokens += [s for s in re.split(r"( |:|\(|\)|:|;)", line.strip()) if s not in ["", " "]]
    except Exception:
        exit("File Error: cannot open file")
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
                match("("); res = [res, term()]; match(")");
            else:
                res = [res, name()]
            
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
    global context, i
    i = 0
    for [a, A, x] in expressions:
        A, x = substitute(A), substitute(x)
        if a=="U":
            exit(f"Name Error: cannot use name 'U'")
        A_beta = beta_reduce(A)
        A_t = get_type(A_beta)
        if A_t !="U":
            exit(f"Type Error: '{stringify(A)}' has type '{stringify(A_t)}' but is supposed to have type 'U'")
        x_beta = beta_reduce(x)
        x_t = get_type(x_beta)
        if not alpha_equiv(x_t, A_beta):
            exit(f"Type Error: '{stringify(x)}' has type '{stringify(x_t)}' but is supposed to have type '{stringify(A_beta)}'")
        add(a, A_beta, x_beta)

def stringify(a):
    match a:
        case [arrow, a, A, B]:
            return f"({a} : {stringify(A)}) {arrow} {stringify(B)}"
        case [f, a]:
            return f"({stringify(f)}) ({stringify(a)})"
        case a:
            return a

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

#When called with no rho, it gives every bound variable in "a" a unique name. When called with {b : c}, it returns a[c/b]
def substitute(a, rho={}):
    global i
    match a:
        #((a : A) -> B)[rho] = ((i : A[rho]) -> B[i/a, rho]) with i being free
        case [arrow, a, A, B]:
            if a=="U":
                exit(f"Name Error: cannot use name 'U'")
            if a == "_":
                return [arrow, a, substitute(A, rho), substitute(B, rho)]
            rho2 = rho | {a : i}
            i+=1
            return [arrow, i-1, substitute(A, rho), substitute(B, rho2)]
        case [f, a]:
            return [substitute(f, rho), substitute(a, rho)]
        case a:
            return rho[a] if a in rho else a

#Beta reduction unfolds definitions and transforms ((x : A) => b) a into b[a/x]
def beta_reduce(a):
    match a:
        case [arrow, a, A, B]:
            A_beta = beta_reduce(A); add(a, A_beta); B_beta = beta_reduce(B); remove(a)
            return [arrow, a, A_beta, B_beta]
        case [f, a]:
            f_beta, a_beta = beta_reduce(f), beta_reduce(a)
            match f_beta:
                case ["=>", x, A, b]:
                    a_t = get_type(a_beta)
                    if not alpha_equiv(A, a_t):
                        exit(f"Type Error: '{stringify(a)}' has type '{stringify(a_t)}' but is applied on '{stringify(f)}' of type '{stringify(get_type(f_beta))}'")
                    return beta_reduce(substitute(b, {x : a}))
                case _:
                    return [f_beta, a_beta]
        case a:
            tupl = get(a)
            return tupl[2] if len(tupl)==3 else a

#(a1 : A1) -> B1 and (a2 : A2) -> B2 are alpha_equivalent if and only if A1 and A2 are alpha equivalent, and B1 and B2[a1/a2] are alpha equivalent
def alpha_equiv(a1, a2):
    match a1, a2:
        case [arrow1, a1, A1, B1], [arrow2, a2, A2, B2]:
            return arrow1==arrow2 and alpha_equiv(A1, A2) and alpha_equiv(B1, substitute(B2, {a2 : a1}))
        case [f1, a1], [f2, a2]:
            return alpha_equiv(f1, f2) and alpha_equiv(a1, a2)
        case a1, a2:
            return a1==a2

def get_type(a):
    match a:
        case [arrow, a, A, B]:
            A_t = get_type(A)
            if A_t!="U":
                exit(f"Type Error: '{stringify(A)}' has type '{stringify(A_t)}' but is supposed to have type 'U'")
            add(a, A); B_t = get_type(B); remove(a)
            if arrow=="=>":
                return ["->", a, A, B_t]
            if B_t!="U":
                exit(f"Type Error: '{stringify(B)}' has type '{stringify(B_t)}' but is supposed to have type 'U'")
            return "U"
        case [f, a]:
            f_t, a_t = get_type(f), get_type(a)
            match f_t:
                case ['->', x, A, B]:
                    if not alpha_equiv(A, a_t):
                        exit(f"Type Error: '{stringify(a)}' has type '{stringify(a_t)}' but is applied on '{stringify(f)}' of type '{stringify(get_type(f_beta))}'")
                    return beta_reduce(substitute(B, {x : a}))
                case _:
                    exit(f"Type Error: '{stringify(f)}' has type '{stringify(f_t)}' but is applied on '{stringify(a)}' of type '{stringify(a_t)}'")
        case a:
            return get(a)[1]

if len(sys.argv)!=2:
    exit(f"Parameter Error: expected file name but got {len(sys.argv)-1} arguments")
tokens = tokenization(sys.argv[1])
i = 0
context = [("U", "U")]
type_checker(parsing())
