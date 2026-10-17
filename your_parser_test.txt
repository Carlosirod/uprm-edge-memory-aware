import ply.lex as lex
import ply.yacc as yacc

#Lexer
tokens = (
    "INTEGER",
    "PLUS",
)

t_PLUS = r"\+"

def t_INTEGER(t):
    r"\d+"
    t.value = int(t.value)
    return t

t_ignore = " \t\r"

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    
def t_error(t):
    raise SyntaxError(
        f"Caracter ilegal {t.value[0]!r} en linea {t.lineno}"
    )

#Parser

precedence = (
    ("left", "PLUS"),
)

def p_expression_integer(p):
    "expression : INTEGER"
    p[0] = p[1]
    
def p_expression_plus(p):
    "expression : expression PLUS expression"

    p[0] = {
        "kind": "sum",
        "left": p[1],
        "right": p[3],
    }

def p_error(p):
    if p is None:
        raise SyntaxError("La entrada termino antes de completar la expresion")

    raise SyntaxError(
        f"Token inesperado {p.value!r} en linea {p.lineno}"
    )
    
    
#test
lexer = lex.lex()

lexer.input("5 + 3")

for token in lexer:
    print(token.type, token.value)

parser = yacc.yacc(
    start="expression",
    write_tables=False,
    debug=False,
)

    
result = parser.parse("5 + 3", lexer=lexer)
print("Expresion reconocida:", result)
    
    