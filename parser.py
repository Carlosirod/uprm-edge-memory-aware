import sys
from pathlib import Path

import ply.yacc as yacc
from lexer import tokens, lexer, LanguageError

def node(kind, **fields):
    return {"kind": kind, **fields}


def p_program(p):
    """program : statement_list"""
    p[0] = p[1]


def p_statement_list(p):
    """statement_list : statement_list statement
                      | empty"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_statement(p):
    """statement : function_def
                 | function_call
                 | memory_function"""
    p[0] = p[1]


def p_memory_function(p):
    """memory_function : MEMORY LPAREN INTEGER ID RPAREN function_def"""
    unit = p[4]
    if unit not in ("kb", "mb", "bytes"):
        raise SyntaxError(f"Unsupported memory unit: {unit}")
    p[0] = {
        "type": "memory_function",
        "budget": p[3],
        "unit": unit,
        "function": p[6]
    }


def p_function_def(p):
    """function_def : FUNC ID LPAREN RPAREN LBRACE statement_list RBRACE"""
    p[0] = {
        "type": "function",
        "name": p[2],
        "body": p[6]
    }


def p_function_call(p):
    """function_call : ID LPAREN RPAREN SEMI"""
    p[0] = {
        "type": "call",
        "name": p[1]
    }


def p_statement_let(p):
    """statement : LET ID ASSIGN expression SEMI"""
    p[0] = {
        "type": "let",
        "name": p[2],
        "value": p[4]
    }


def p_statement_print(p):
    """statement : PRINT LPAREN expression RPAREN SEMI"""
    p[0] = {
        "type": "print",
        "value": p[3]
    }


def p_expression_array(p):
    """expression : ARRAY LPAREN type_name COMMA INTEGER RPAREN"""
    p[0] = {
        "type": "array",
        "element_type": p[3],
        "size": p[5]
    }


def p_type_name(p):
    """type_name : INT
                 | FLOAT
                 | BOOL
                 | STRING"""
    p[0] = p[1]


def p_expression_integer(p):
    """expression : INTEGER"""
    p[0] = p[1]


def p_expression_decimal(p):
    """expression : DECIMAL"""
    p[0] = p[1]


def p_expression_text(p):
    """expression : TEXT"""
    p[0] = p[1]


def p_expression_boolean(p):
    """expression : TRUE
                  | FALSE"""
    p[0] = p[1]


def p_expression_variable(p):
    """expression : ID"""
    p[0] = p[1]


def p_empty(p):
    """empty :"""
    p[0] = []


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

####

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
