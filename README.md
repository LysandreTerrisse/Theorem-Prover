# Theorem Prover

## Extended Backus-Naur Form
Here is the Extended Backus-Naur form, where `regex(s)` must be interpreted as the regular expression `s`:
```
<file> ::= (<name> ":" <term> "=" <term> ";")*
<name> ::= regex("^[a-zA-Z_]+$")
<term> ::= "(" <name> ":" <term> ")" ("->" | "=>") <term> | (<name> | "(" <term> ")")+
```

Or equivalently:
```
<file> ::= <expression>*
<expression> ::= <name> ":" <term> "=" <term> ";"
<name> ::= regex("^[a-zA-Z_]+$")
<term> ::= <simplearrow> | <doublearrow> | <application> | <name> | "(" <term> ")"
<simplearrow> ::= "(" <name> ":" <term> ")" "->" <term>
<doublearrow> ::= "(" <name> ":" <term> ")" "=>" <term>
<application> ::= (<name> | "(" <term> ")") (<name> | "(" <term> ")")+
```

## Notation in the code
I use the following notation in the code:
- For expressions: `a : A = x;`
- For simple arrows: `(a : A) -> B`
- For double arrows: `(a : A) => b`
- For applications: `f a`

I use `x` to refer to a term of type `A` when the name `a` is already taken.

In the comments in the code, I sometimes use `X[a/b]` to mean "`X` if we substitute `a` for `b`" (or equivalently, if we use `a` instead of `b`). When I write `X[b/a, c/b]`, it means we replace `a` by `b` and we replace `b` by `c` at the same time, but we don't replace `a` by `c`. Furthermore, when we have two substitutions `b/a` and `c/a`, the leftmost one has the priority.

## Special name
There is only one special name, which is `U`. It is the type of all types, including `U` itself. Furthermore, `U` is the only name that cannot be overwritten.

## Girard's paradox
As `U` is of type `U`, this leaeds to Girard's paradox, stating that if a type is its own type, then we have a contradiction. To fix this, we would need to have a chain of universes `U0 : U1 : U2 : ...`, but I prefer to keep this language simple. The proof of Girard's paradox can be found in `paradox.in`. This proof was made from [this source](https://www.cs.princeton.edu/courses/archive/fall07/cos595/stdlib/html/Coq.Logic.Hurkens.html). When running the theorem prover on `paradox.in`, the program never halts, as it would try to beta-reduce the expression when typing.
