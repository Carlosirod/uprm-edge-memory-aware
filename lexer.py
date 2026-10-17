import ply.lex as lex

class LanguageError(Exception):
    pass

reserved = {
    word: word.upper()
    for word in (
        "let", "func", "if", "else", "while", "for",
        "return", "print", "true", "false",
        "int", "float", "bool", "string", "array",
    )
}

tokens = list(reserved.values()) + [
    "ID", "INTEGER", "DECIMAL", "TEXT", "MEMORY",
    "PLUS", "MINUS", "TIMES", "DIVIDE", "MOD",
    "EQ", "NE", "LT", "GT", "LE", "GE", "ASSIGN",
    "LPAREN", "RPAREN", "LBRACE", "RBRACE",
    "LBRACKET", "RBRACKET", "SEMI", "COMMA",
]

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
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_SEMI = r";"
t_COMMA = r","

t_ignore = " \t\r"


def t_COMMENT(t):
    r"//[^\n]*"
    pass


def t_MEMORY(t):
    r"@memory\b"
    return t


def t_DECIMAL(t):
    r"(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+"
    t.value = float(t.value)
    return t


def t_INTEGER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_TEXT(t):
    r'"(?:[^"\\\n]|\\[^\n])*"'
    return t


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    t.type = reserved.get(t.value, "ID")
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    if t.value[0] == '"':
        description = "cadena sin comillas de cierre"
    else:
        description = f"caracter ilegal {t.value[0]!r}"

    raise LanguageError(f"{description} en linea {t.lineno}")

lexer = lex.lex()