import re

"""
<expression> ::= <name> ":" <term> "=" <term> ";"
<name> ::= "_"
<term> ::= "(" <name> ":" <term> ")" ("->" | "=>") <term> | (<name> | "(" <term> ")")+
"""

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
    s = name(); match(":"); t1 = term(); match("="); t2 = term(); match(";")
    return ["expression", s, t1, t2]

def name():
    global tokens, i
    if not re.match("^[a-zA-Z_]+$", tokens[i]):
        exit(f"Syntax Error: expected name but got '{tokens[i]}' at token {i+1}")
    i+=1
    return ["name", tokens[i-1]]

def match(*args):
    global tokens, i
    if tokens[i] not in args:
        exit("Syntax Error: expected '" + "' or '".join(args) + f"' but got '{tokens[i]}' at token {i+1}")
    i+=1
    return tokens[i-1]

def term():
    global tokens, i
    #If we are in an arrow case
    if i+2 < len(tokens) and tokens[i+2]==":":
        match("("); n = name(); match(":"); t1 = term(); match(")"); ar = match("=>", "->"); t2 = term()
        return [ar, n, t1, t2]
    else:
        res = ["list"]
        while tokens[i] not in ["=", ")", ";"]:
            if tokens[i]=="(":
                match("("); res.append(term()); match(")")
            else:
                res.append(name())

            if i==len(tokens):
                exit("Syntax Error: end of file reached because of missing ';'")
        return res[1] if len(res)==2 else res

def parsing():
    global tokens, i
    expressions = []
    while i<len(tokens):
        expressions.append(expression())
    return expressions

"""Type checking"""

def type_checker(trees):
    global context
    for tree in trees:
        type_nf = normal_form(tree[2])
        type_type = get_type(type_nf)
        if type_type != ["name", "U"]:
            exit(f"Type Error: got type '{stringify(type_type)}' instead of 'U'")
        term_nf = normal_form(tree[3])
        term_type = get_type(term_nf)
        if term_type!=type_nf:
            exit(f"Type Error: got type '{stringify(term_type)}' instead of '{stringify(tree[2])}'")
        if tree[1][1]!="_":
            context.append((tree[1][1], term_type, term_nf))

def stringify(tree):
    if tree[0] in ["=>", "->"]:
        return f"({tree[1][1]} : {stringify(tree[2])}) {tree[0]} {stringify(tree[3])}"
    if tree[0] == "list":
        return "".join([f" ({stringify(e)}) " for e in tree[1:]])
    if tree[0] == "name":
        return tree[1]

#new is a tree and old is a string
def substitute(tree, new, old):
  assert type(new) is list
  assert type(old) is str
  if tree[0] in ["->", "=>"]:
      return [tree[0], tree[1], substitute(tree[2], new, old), tree[3] if tree[1][1]==old else substitute(tree[3], new, old)]
  elif tree[0]=="list":
      return ["list"] + [substitute(t, new, old) for t in tree[1:]]
  elif tree[0]=="name":
      return new if tree[1]==old else tree

#Normal form:
#- Converts variables into their definitions if they have one (if replace_defs==True)
#- Transforms bounded variables into numbers
#- Transforms ((a : A) => b) x into b[x/a], and transforms a b c into (a b) c
def normal_form(tree, i=0, replace_defs=True):
    if tree[0] in ["->", "=>"]:
        return [tree[0], ['name', str(i)], normal_form(tree[2], i+1, replace_defs), normal_form(substitute(tree[3], ['name', str(i)], tree[1][1]), i+1, replace_defs)]
    elif tree[0]=="list":
        if len(tree)==2:
            return normal_form(tree[1], i, replace_defs)
        else:
            f_nf = normal_form(tree[:-1], i, replace_defs)
            arg_nf = normal_form(tree[-1], i, replace_defs)
            if f_nf[0]=="=>":
                return normal_form(substitute(f_nf[3], arg_nf, f_nf[1][1]), i, replace_defs)
            else:
                return ["list", f_nf, arg_nf]
    elif tree[0]=="name":
        if not replace_defs:
            assert tree[1]=="U" or tree[1].isnumeric(), tree
            return tree

        if type(tree[1]) is int:
            return tree
        
        for j in range(len(context)-1, -1, -1):
            if context[j][0]==tree[1]:
                return normal_form(context[j][2], i, False) if len(context[j])==3 else tree

        if tree[1]=="U" or tree[1].isnumeric():
            return tree
        
        exit(f"Context Error: unknown variable '{tree[1]}'")

def get_type(tree):
    if tree[0]=="->":
        return get_simple_arrow_type(tree)
    elif tree[0]=="=>":
        return get_double_arrow_type(tree)
    elif tree[0]=="list":
        return get_list_type(tree)
    elif tree[0]=="name":
        return get_name_type(tree)

"""
To get the type of a variable, we need to look in the context from end to beginning
"""
def get_name_type(tree):
    global context
    for i in range(len(context)-1, -1, -1):
        if context[i][0]==tree[1]:
            return context[i][1]
    exit(f"Context Error: unknown variable '{tree[1]}'")

def get_list_type(tree):
    if len(tree)==2:
        return get_type(tree[-1])
    else:
        f_type = get_type(tree[:-1])
        a_type = get_type(tree[-1])
        if f_type[0]!="->" or f_type[2]!=a_type:
            exit(f"Type Error: '{stringify(tree[:-1])}' has type '{stringify(f_type)}' but is applied on '{stringify(tree[-1])}' of type '{stringify(a_type)}'")
        return substitute(f_type[3], tree[-1], f_type[1][1])

def get_double_arrow_type(tree):
    global context
    A_type = get_type(tree[2])
    if A_type!=["name", "U"]:
        exit(f"Type Error: '{stringify(tree[2])}' has type '{stringify(A_type)}' but is supposed to have type 'U'")
    if tree[1][1]!="_":
        context.append((tree[1][1], tree[2]))
    b_type = get_type(tree[3])
    if tree[1][1]!="_":
        context.pop()
    return ["->", tree[1], tree[2], b_type]

def get_simple_arrow_type(tree):
    global context
    A_type = get_type(tree[2])
    if A_type!=["name", "U"]:
        exit(f"Type Error: '{stringify(tree[2])}' has type '{stringify(A_type)}' but is supposed to have type 'U'")
    if tree[1][1]!="_":
        context.append((tree[1][1], tree[2]))
    B_type = get_type(tree[3])
    if B_type!=["name", "U"]:
        exit(f"Type Error: '{stringify(tree[3])}' has type '{stringify(B_type)}' but is supposed to have type 'U'")
    if tree[1][1]!="_":
        context.pop()
    return ["name", "U"]

tokens = tokenization("input.in")
i = 0
context = [("U", ["name", "U"])]
type_checker(parsing())










