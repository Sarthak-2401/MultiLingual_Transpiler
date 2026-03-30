"""
Phase 1: Lexical Analysis (Tokenizer)
Converts raw Python source code into a stream of typed tokens.
"""

import re
from dataclasses import dataclass
from typing import List

TOKEN_TYPES = [
    ("KEYWORD",    r'\b(def|return|if|elif|else|while|for|in|and|or|not|True|False|None|import|from|class|pass|break|continue|print)\b'),
    ("FLOAT",      r'\b\d+\.\d+\b'),
    ("NUMBER",     r'\b\d+\b'),
    ("STRING",     r'(\".*?\"|\'.*?\')'),
    ("IDENTIFIER", r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ("LPAREN",     r'\('),
    ("RPAREN",     r'\)'),
    ("LBRACKET",   r'\['),
    ("RBRACKET",   r'\]'),
    ("LBRACE",     r'\{'),
    ("RBRACE",     r'\}'),
    ("COLON",      r':'),
    ("COMMA",      r','),
    ("DOT",        r'\.'),
    ("PLUS_EQ",    r'\+='),
    ("MINUS_EQ",   r'-='),
    ("STAR_EQ",    r'\*='),
    ("DIV_EQ",     r'/='),
    ("EQ_EQ",      r'=='),
    ("NEQ",        r'!='),
    ("LTE",        r'<='),
    ("GTE",        r'>='),
    ("EQUALS",     r'='),
    ("LT",         r'<'),
    ("GT",         r'>'),
    ("PLUS",       r'\+'),
    ("MINUS",      r'-'),
    ("STAR",       r'\*'),
    ("SLASH",      r'/'),
    ("PERCENT",    r'%'),
    ("NEWLINE",    r'\n'),
    ("COMMENT",    r'#[^\n]*'),
    ("WHITESPACE", r'[ \t]+'),
]

@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int

    def to_dict(self):
        return {"type": self.type, "value": self.value, "line": self.line, "col": self.col}

class TokenizeError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(msg)
        self.line = line
        self.col = col

def tokenize(source: str) -> List[Token]:
    """Tokenize Python source code into a list of Token objects."""
    tokens = []
    line_num = 1
    col_num = 1
    pos = 0
    n = len(source)

    pattern_parts = [f'(?P<T{i}_{name}>{regex})' for i, (name, regex) in enumerate(TOKEN_TYPES)]
    master = re.compile('|'.join(pattern_parts))

    while pos < n:
        m = master.match(source, pos)
        if m:
            kind = m.lastgroup.split('_', 1)[1]  # strip T0_ prefix
            value = m.group()
            if kind == "NEWLINE":
                tokens.append(Token("NEWLINE", "\\n", line_num, col_num))
                line_num += 1
                col_num = 1
            elif kind not in ("WHITESPACE", "COMMENT"):
                tokens.append(Token(kind, value, line_num, col_num))
                col_num += len(value)
            else:
                col_num += len(value)
            pos = m.end()
        else:
            ch = source[pos]
            raise TokenizeError(f"Unexpected character: '{ch}'", line_num, col_num)

    return tokens
