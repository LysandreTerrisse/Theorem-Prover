# Theorem Prover

## Pure Type System
This system is a [Pure Type System](https://en.wikipedia.org/wiki/Pure_type_system) in which the only sort we have is `U`, the only axiom we have is (`U`, `U`), and in which the only rule we have is (`U`, `U`, `U`).

## Special name
`U` is the only name which is already predefined. Furthermore, `U` cannot be overwritten.

## Extended Backus-Naur Form
Here is the [Extended Backus-Naur form](https://en.wikipedia.org/wiki/Extended_Backus–Naur_form), where `regex(s)` must be interpreted as the regular expression `s`:
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
Which can be interpreted as follows:
- The expression `a : A = x;` means that we declare the variable $a$ of type $A$ as $x$.
- The simple arrow `(a : A) -> B` corresponds to $\prod a : A. B$.
- The double arrow `(a : A) => b` corresponds to $\lambda a : A. b$.
- The application `f a` corresponds to $f ~ a$.

## Notation in the code
In the comments in the code, I sometimes use `X[a/b]` to mean "`X` if we substitute `a` for `b`" (or equivalently, if we use `a` instead of `b`). When I write `X[b/a, c/b]`, it means we replace `a` by `b` and we replace `b` by `c` at the same time, but we don't replace `a` by `c`. Furthermore, when we have two substitutions `b/a` and `c/a`, the leftmost one has the priority.

## Girard's paradox
As `U` is of type `U`, this leads to Girard's paradox, stating that if a type is its own type, then we have a contradiction. To fix this, we would need to have a chain of universes `U0 : U1 : U2 : ...`, but I prefer to keep this language simple. The proof of Girard's paradox can be found in `paradox.in`. This proof was made from [this source](https://www.cs.princeton.edu/courses/archive/fall07/cos595/stdlib/html/Coq.Logic.Hurkens.html). When running the theorem prover on `paradox.in`, the program never halts, as it would try to beta-reduce the expression when typing.
