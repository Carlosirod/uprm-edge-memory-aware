import sys
sys.path.insert(0, "ply.zip")

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
        description = "malformed string"
    else:
        description = f"unexpected token ‘{t.value[0]}’"

    raise LanguageError(
        f"{description} at line {t.lineno}"
    )

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

precedence = (
    ("nonassoc", "IF_WITHOUT_ELSE"),
    ("nonassoc", "ELSE"),
    ("nonassoc", "EQ", "NE", "LT", "LE", "GT", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("right", "UMINUS", "UPLUS"),
)


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
    """statement : declaration SEMI
                 | assignment SEMI
                 | expression SEMI
                 | block
                 | function_def
                 | memory_function"""

    p[0] = p[1]


def p_declaration(p):
    """declaration : LET ID ASSIGN expression"""

    p[0] = {
        "type": "let",
        "name": p[2],
        "value": p[4]
    }


def p_assignment(p):
    """assignment : lvalue ASSIGN expression"""

    p[0] = {
        "type": "assignment",
        "target": p[1],
        "value": p[3]
    }


def p_lvalue(p):
    """lvalue : ID
              | lvalue LBRACKET expression RBRACKET"""

    if len(p) == 2:
        p[0] = {
            "type": "variable",
            "name": p[1]
        }

    else:
        p[0] = {
            "type": "index",
            "target": p[1],
            "index": p[3]
        }


def p_block(p):
    """block : LBRACE statement_list RBRACE"""

    p[0] = {
        "type": "block",
        "statements": p[2]
    }


def p_memory_function(p):
    """memory_function : MEMORY LPAREN budget ID RPAREN function_def"""

    amount = p[3]
    unit = p[4]

    if unit not in MEMORY_UNITS:
        raise LanguageError(
            f"unsupported memory unit {unit!r} at line {p.lineno(4)}"
        )

    p[0] = {
        "type": "memory_function",
        "budget": amount,
        "unit": unit,
        "budget_bytes": amount * MEMORY_UNITS[unit],
        "function": p[6]
    }


def p_memory_function_empty(p):
    """memory_function : MEMORY LPAREN RPAREN function_def"""

    raise LanguageError(
        f"malformed @memory annotation at line {p.lineno(1)}"
    )


def p_budget(p):
    """budget : INTEGER
              | DECIMAL"""

    p[0] = p[1]


def p_function_def(p):
    """function_def : FUNC ID LPAREN parameters RPAREN block"""

    p[0] = {
        "type": "function",
        "name": p[2],
        "parameters": p[4],
        "body": p[6]
    }


def p_parameters(p):
    """parameters : parameter_list
                  | empty"""

    p[0] = p[1] or []


def p_parameter_list(p):
    """parameter_list : ID
                      | parameter_list COMMA ID"""

    if len(p) == 2:
        p[0] = [p[1]]

    else:
        p[0] = p[1] + [p[3]]


def p_statement_if(p):
    """statement : IF LPAREN expression RPAREN statement %prec IF_WITHOUT_ELSE
                 | IF LPAREN expression RPAREN statement ELSE statement"""

    p[0] = {
        "type": "if",
        "condition": p[3],
        "then": p[5],
        "else": p[7] if len(p) == 8 else None
    }


def p_statement_while(p):
    """statement : WHILE LPAREN expression RPAREN statement"""

    p[0] = {
        "type": "while",
        "condition": p[3],
        "body": p[5]
    }


def p_statement_for(p):
    """statement : FOR LPAREN for_part SEMI optional_expression SEMI for_part RPAREN statement"""

    p[0] = {
        "type": "for",
        "initial": p[3],
        "condition": p[5],
        "update": p[7],
        "body": p[9]
    }


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


def p_statement_return(p):
    """statement : RETURN optional_expression SEMI"""

    p[0] = {
        "type": "return",
        "value": p[2]
    }


def p_statement_print(p):
    """statement : PRINT LPAREN expression RPAREN SEMI"""

    p[0] = {
        "type": "print",
        "value": p[3]
    }


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

    p[0] = {
        "type": "binary",
        "operator": p[2],
        "left": p[1],
        "right": p[3]
    }


def p_expression_unary(p):
    """expression : MINUS expression %prec UMINUS
                  | PLUS expression %prec UPLUS"""

    p[0] = {
        "type": "unary",
        "operator": p[1],
        "value": p[2]
    }


def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""

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

    p[0] = {
        "type": "literal",
        "value": value
    }


def p_expression_variable(p):
    """expression : lvalue"""

    p[0] = p[1]


def p_expression_call(p):
    """expression : ID LPAREN arguments RPAREN"""

    p[0] = {
        "type": "call",
        "name": p[1],
        "arguments": p[3]
    }


def p_arguments(p):
    """arguments : expressions
                 | empty"""

    p[0] = p[1] or []


def p_expressions(p):
    """expressions : expression
                   | expressions COMMA expression"""

    if len(p) == 2:
        p[0] = [p[1]]

    else:
        p[0] = p[1] + [p[3]]


def p_expression_array(p):
    """expression : ARRAY LPAREN type_name COMMA expression RPAREN"""

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


def p_empty(p):
    """empty :"""

    p[0] = None


def p_error(token):

    if token is None:
        raise LanguageError(
            "missing closing delimiter"
        )

    raise LanguageError(
        f"unexpected token {token.value!r} at line {token.lineno}"
    )


####

active_lexer = None
parser = None


def parse(source):
    """Analiza el codigo y devuelve su AST sin ejecutarlo."""

    global active_lexer
    global parser

    active_lexer = lexer
    active_lexer.lineno = 1

    if parser is None:
        parser = yacc.yacc()

    return parser.parse(
        source,
        lexer=active_lexer
    )


def main():

    if len(sys.argv) != 2:
        print(
            "Uso: python input.py <archivo>.uedge",
            file=sys.stderr
        )
        return 2

    try:

        source = Path(
            sys.argv[1]
        ).read_text(
            encoding="utf-8-sig"
        )

        parse(source)

    except (OSError, UnicodeError) as error:

        print(
            f"Error: no se pudo leer el archivo: {error}",
            file=sys.stderr
        )

        return 2

    except LanguageError as error:
        print(f"Error: {error}")
        return 0

    print("Parsed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())