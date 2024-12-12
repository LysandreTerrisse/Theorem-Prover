# Theorem Prover

## Backus-Naur Form
Here is the Backus-Naur form:
```
<expression> ::= <name> ":" <term> "=" <term> ";"
<name> ::= "_"
<term> ::= "(" <name> ":" <term> ")" ("->" | "=>") <term> | (<name> | "(" <term> ")")+
```

Or equivalently:
```
<expression> ::= <name> ":" <term> "=" <term> ";"
<name> ::= "_"
<term> ::= <simplearrow> | <doublearrow> | <name> | <application>
<simplearrow> ::= "(" <name> ":" <term> ")" "->" <term>
<doublearrow> ::= "(" <name> ":" <term> ")" "=>" <term>
<application> ::= (<name> | "(" <term> ")") (<name> | "(" <term> ")")
```

## Notation in the code
I use the following notation in the code:
- For expressions: `a : A = x;`
- For simple arrows: `(a : A) -> B`
- For double arrows: `(a : A) => b`
- For applications: `f a`

I use `x` to refer to a term of type `A` when the name `a` is already taken.

## Problems remaining
There are no universes
