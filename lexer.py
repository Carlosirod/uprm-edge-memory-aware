import ply.lex as lex

class LexerError(Exception):
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
    raise LexerError(
        f"illegal character '{t.value[0]}' at line {t.lineno}"
    )

# Build lexer

lexer = lex.lex()