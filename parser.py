import sys
from pathlib import Path

import ply.yacc as yacc
from lexer import tokens, lexer, LanguageError

def node(kind, **fields):
    return {"kind": kind, **fields}

precedence = (
    ("nonassoc", "IF_WITHOUT_ELSE"),
    ("nonassoc", "ELSE"),
    ("nonassoc", "EQ", "NE", "LT", "LE", "GT", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("right", "UMINUS", "UPLUS"),
)


def p_program(p):
    "program : statements"
    p[0] = node("program", statements=p[1])


def p_statements(p):
    """statements : statements statement
                  | empty"""
    p[0] = p[1] + [p[2]] if len(p) == 3 else []


def p_statement_simple(p):
    """statement : declaration SEMI
                 | assignment SEMI
                 | expression SEMI
                 | block
                 | function"""
    p[0] = p[1]


def p_declaration(p):
    "declaration : LET ID ASSIGN expression"
    p[0] = node(
        "declaration",
        name=p[2],
        value=p[4],
        line=p.lineno(1),
    )


def p_assignment(p):
    "assignment : lvalue ASSIGN expression"
    p[0] = node("assignment", target=p[1], value=p[3])


def p_lvalue(p):
    """lvalue : ID
              | lvalue LBRACKET expression RBRACKET"""
    if len(p) == 2:
        p[0] = node("variable", name=p[1], line=p.lineno(1))
    else:
        p[0] = node("index", target=p[1], index=p[3])


def p_block(p):
    "block : LBRACE statements RBRACE"
    p[0] = node(
        "block",
        statements=p[2],
        line=p.lineno(1),
    )


def p_function(p):
    "function : FUNC ID LPAREN parameters RPAREN block"
    p[0] = node(
        "function",
        name=p[2],
        parameters=p[4],
        body=p[6],
        memory=None,
        line=p.lineno(1),
    )


def p_function_memory(p):
    "function : MEMORY LPAREN budget ID RPAREN function"
    if p[6]["memory"] is not None:
        raise LanguageError(
            f"anotacion @memory duplicada en linea {p.lineno(1)}"
        )

    p[0] = p[6]
    p[0]["memory"] = {
        "amount": p[3],
        "unit": p[4],
        "line": p.lineno(1),
    }


def p_budget(p):
    """budget : INTEGER
              | DECIMAL"""
    p[0] = p[1]


def p_parameters(p):
    """parameters : names
                  | empty"""
    p[0] = p[1] or []


def p_names(p):
    """names : ID
             | names COMMA ID"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


def p_if(p):
    """statement : IF LPAREN expression RPAREN statement %prec IF_WITHOUT_ELSE
                 | IF LPAREN expression RPAREN statement ELSE statement"""
    p[0] = node(
        "if",
        condition=p[3],
        then=p[5],
        otherwise=p[7] if len(p) == 8 else None,
        line=p.lineno(1),
    )


def p_while(p):
    "statement : WHILE LPAREN expression RPAREN statement"
    p[0] = node(
        "while",
        condition=p[3],
        body=p[5],
        line=p.lineno(1),
    )


def p_for(p):
    "statement : FOR LPAREN for_part SEMI optional_expression SEMI for_part RPAREN statement"
    p[0] = node(
        "for",
        initial=p[3],
        condition=p[5],
        update=p[7],
        body=p[9],
        line=p.lineno(1),
    )


def p_for_part(p):
    """for_part : declaration
                | assignment
                | expression
                | empty"""
    p[0] = p[1]


def p_optional_expression(p):
    """optional_expression : expression
                           | empty"""
    p[0] = p[1]


def p_return(p):
    "statement : RETURN optional_expression SEMI"
    p[0] = node(
        "return",
        value=p[2],
        line=p.lineno(1),
    )


def p_print(p):
    "statement : PRINT LPAREN expression RPAREN SEMI"
    p[0] = node(
        "print",
        value=p[3],
        line=p.lineno(1),
    )


def p_expression_binary(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression"""
    p[0] = node(
        "binary",
        operator=p[2],
        left=p[1],
        right=p[3],
        line=p.lineno(2),
    )


def p_expression_unary(p):
    """expression : MINUS expression %prec UMINUS
                  | PLUS expression %prec UPLUS"""
    p[0] = node(
        "unary",
        operator=p[1],
        value=p[2],
        line=p.lineno(1),
    )


def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_expression_literal(p):
    """expression : INTEGER
                  | DECIMAL
                  | TEXT
                  | TRUE
                  | FALSE"""
    if p.slice[1].type == "TRUE":
        value = True
    elif p.slice[1].type == "FALSE":
        value = False
    else:
        value = p[1]

    p[0] = node("literal", value=value, line=p.lineno(1))


def p_expression_variable(p):
    "expression : lvalue"
    p[0] = p[1]


def p_expression_call(p):
    "expression : ID LPAREN arguments RPAREN"
    p[0] = node(
        "call",
        name=p[1],
        arguments=p[3],
        line=p.lineno(1),
    )


def p_arguments(p):
    """arguments : expressions
                 | empty"""
    p[0] = p[1] or []


def p_expressions(p):
    """expressions : expression
                   | expressions COMMA expression"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


def p_expression_array(p):
    "expression : ARRAY LPAREN type COMMA expression RPAREN"
    p[0] = node(
        "array",
        element_type=p[3],
        size=p[5],
        line=p.lineno(1),
    )


def p_type(p):
    """type : INT
            | FLOAT
            | BOOL
            | STRING"""
    p[0] = p[1]


def p_empty(p):
    "empty :"
    p[0] = None


def p_error(token):
    if token is None:
        raise LanguageError(
            f"unexpected end of file on line {active_lexer.lineno}; "
            "An instruction is incomplete, or a delimiter is missing its closing counterpart"
        )

    raise LanguageError(
        f"unexpected token {token.value!r} in line {token.lineno}; "
        "review the instruction and its delimiters"
    )


# ============================================================
# ANALISIS Y EJECUCION DESDE LA TERMINAL
# ============================================================

active_lexer = None

def parse(source):
    """Analiza el codigo y devuelve su AST sin ejecutarlo."""
    global active_lexer

    active_lexer = lexer
    active_lexer.lineno = 1

    parser = yacc.yacc(
        start="program",
        write_tables=False,
        debug=False,
    )

    return parser.parse(
        source,
        lexer=active_lexer,
        tracking=True,
    )


def main():
    if len(sys.argv) != 2:
        print(
            "Uso: python parser.py <archivo>.uedge",
            file=sys.stderr,
        )
        return 2

    try:
        source = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
        parse(source)

    except (OSError, UnicodeError) as error:
        print(
            f"Error: no se pudo leer el archivo: {error}",
            file=sys.stderr,
        )
        return 2

    except LanguageError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print("Parse successful")
    return 0


if __name__ == "__main__":
    sys.exit(main())