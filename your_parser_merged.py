import sys
from pathlib import Path

import ply.lex as lex
import ply.yacc as yacc

class LanguageError(Exception):
    pass

# Reserved words

reserved = {
    "let": "LET",
    "func": "FUNC",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "return": "RETURN",
    "print": "PRINT",
    "true": "TRUE",
    "false": "FALSE",
    "int": "INT",
    "float": "FLOAT",
    "bool": "BOOL",
    "string": "STRING",
    "array": "ARRAY",
}

# Tokens

tokens = [
    "ID",
    "INTEGER",
    "DECIMAL",
    "TEXT",
    "MEMORY",

    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "MOD",

    "EQ",
    "NE",
    "LT",
    "GT",
    "LE",
    "GE",
    "ASSIGN",

    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "LBRACKET",
    "RBRACKET",

    "SEMI",
    "COMMA",
] + list(reserved.values())

# Operators

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_MOD = r"%"

t_EQ = r"=="
t_NE = r"!="
t_LE = r"<="
t_GE = r">="
t_LT = r"<"
t_GT = r">"

t_ASSIGN = r"="

# Symbols

t_LPAREN = r"\("
t_RPAREN = r"\)"

t_LBRACE = r"\{"
t_RBRACE = r"\}"

t_LBRACKET = r"\["
t_RBRACKET = r"\]"

t_SEMI = r";"
t_COMMA = r","

# Ignored characters

t_ignore = " \t\r"

# Comments

def t_COMMENT(t):
    r"//[^\n]*"
    pass

# Memory-Aware token

def t_MEMORY(t):
    r"@memory\b"
    return t

# Decimal Numbers

def t_DECIMAL(t):
    r"\d+\.\d+"
    t.value = float(t.value)
    return t

# Integers numbers

def t_INTEGER(t):
    r"\d+"
    t.value = int(t.value)
    return t

# Strings

def t_TEXT(t):
    r'"([^"\\\n]|\\.)*"'
    return t

# Identifies / Reserved words

def t_ID(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"

    t.type = reserved.get(t.value, "ID")

    return t

# Line numbers

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

# Lexical errors

def t_error(t):
    if t.value[0] == '"':
        description = "string without a closing quotation mark"
    else:
        description = f"ilegal caracter {t.value[0]!r}"

    raise LanguageError(f"{description} in line {t.lineno}")

# Build lexer

lexer = lex.lex()


# ============================================================
# PARSER
# ============================================================

# Accepted memory budget units.
MEMORY_UNITS = {
    "bytes": 1,
    "kb": 1024,
    "mb": 1024 * 1024,
}

# Sample memory model for Subproject 2.
# Subproject 1 does not calculate or enforce memory consumption.
MEMORY_TYPE_BYTES = {
    "int": 4,
    "float": 4,
}

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

    amount = p[3]
    unit = p[4]

    if unit not in MEMORY_UNITS:
        raise LanguageError(
            f"unsupported memory unit {unit!r} at line {p.lineno(4)}; "
            "expected 'bytes', 'kb', or 'mb'"
        )

    p[0] = {
        "type": "memory_function",
        "budget": amount,
        "unit": unit,
        "budget_bytes": amount * MEMORY_UNITS[unit],
        "line": p.lineno(1),
        "function": p[6],
    }

def p_memory_function_empty(p):
    """memory_function : MEMORY LPAREN RPAREN function_def"""

    raise LanguageError(
        f"empty @memory() annotation at line {p.lineno(1)}; "
        "expected an integer budget and a unit, "
        "for example @memory(40kb)"
    )


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
    
def p_expression_plus(p):
    "expression : expression PLUS expression"

    p[0] = {
        "type": "binary",
        "operator": p[2],
        "left": p[1],
        "right": p[3],
    }


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
        errorlog=yacc.NullLogger(),
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
