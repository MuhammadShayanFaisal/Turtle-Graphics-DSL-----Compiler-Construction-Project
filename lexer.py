"""
lexer.py  —  TurtleScript Lexical Analyser
Uses regex-based tokenisation with line/column tracking.
Token types: KEYWORD, NUMBER, FLOAT, STRING, IDENT, NEWLINE
"""

import re

# ─────────────────────────────────────────────
# Keyword set (all uppercase commands)
# ─────────────────────────────────────────────
KEYWORDS = {
    "FORWARD", "BACK", "LEFT", "RIGHT",
    "PENUP", "PENDOWN", "SET",
    "REPEAT", "PROC", "CALL", "END",
    "COLOR", "PENWIDTH", "CIRCLE",
    "IF", "ELSE",
}

# ─────────────────────────────────────────────
# Token spec: (type, regex) in priority order
# ─────────────────────────────────────────────
TOKEN_SPEC = [
    ("FLOAT",    r'\d+\.\d+'),           # float before int
    ("NUMBER",   r'\d+'),                # integer
    ("STRING",   r'"[^"]*"'),            # quoted string
    ("NEWLINE",  r'\n'),                 # line break
    ("SKIP",     r'[ \t]+|#[^\n]*'),     # whitespace / comments
    ("IDENT",    r'[A-Za-z_][A-Za-z_0-9]*'),  # identifiers / keywords
    ("OP",       r'[+\-*/=<>!]+'),       # operators
    ("MISMATCH", r'.'),                  # anything else
]

MASTER_RE = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
)


class Token:
    """A single token with type, value, line and column."""
    __slots__ = ("type", "value", "line", "col")

    def __init__(self, type_: str, value, line: int, col: int):
        self.type  = type_
        self.value = value
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.col})"


def lexer(code: str) -> list[Token]:
    """
    Tokenise *code* and return a list of Token objects.
    Prints a lexical error and continues on unrecognised characters.
    """
    tokens: list[Token] = []
    errors: list[str]   = []
    line_num = 1
    line_start = 0

    for mo in MASTER_RE.finditer(code):
        kind  = mo.lastgroup
        value = mo.group()
        col   = mo.start() - line_start + 1

        if kind == "SKIP":
            continue                     # whitespace / comment — skip silently

        elif kind == "NEWLINE":
            tokens.append(Token("NEWLINE", "\n", line_num, col))
            line_num  += 1
            line_start = mo.end()

        elif kind == "FLOAT":
            tokens.append(Token("FLOAT", float(value), line_num, col))

        elif kind == "NUMBER":
            tokens.append(Token("NUMBER", int(value), line_num, col))

        elif kind == "STRING":
            # Strip surrounding quotes
            tokens.append(Token("STRING", value[1:-1], line_num, col))

        elif kind == "IDENT":
            upper = value.upper()
            if upper in KEYWORDS:
                tokens.append(Token("KEYWORD", upper, line_num, col))
            else:
                tokens.append(Token("IDENT", value, line_num, col))

        elif kind == "OP":
            tokens.append(Token("OP", value, line_num, col))

        elif kind == "MISMATCH":
            errors.append(
                f"  Lexical Error at line {line_num}, col {col}: "
                f"unexpected character {value!r}"
            )

    # Report all lexical errors together (non-fatal)
    if errors:
        print("\n[LEXER] Errors found:")
        for e in errors:
            print(e)

    return tokens