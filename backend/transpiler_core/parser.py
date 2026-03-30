"""
Phase 2: Syntax Analysis (Parser → AST)
Uses column numbers from tokens to detect block indentation.
"""
from typing import List, Dict, Any, Optional
from .tokenizer import Token

class ParseError(Exception):
    def __init__(self, msg, token=None):
        super().__init__(msg)
        self.token = token

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens  # includes NEWLINE tokens
        self.pos = 0

    # ─── Utilities ─────────────────────────────────────────────────────────────

    def peek(self, offset=0) -> Optional[Token]:
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else None

    def current(self) -> Optional[Token]:
        return self.peek(0)

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def skip_newlines(self):
        while self.current() and self.current().type == "NEWLINE":
            self.advance()

    def expect(self, type_: str, value: str = None) -> Token:
        self.skip_newlines()
        t = self.current()
        if t is None:
            raise ParseError(f"Expected {type_} but reached end of input")
        if t.type != type_:
            raise ParseError(f"Expected {type_} but got {t.type} ('{t.value}')", t)
        if value and t.value != value:
            raise ParseError(f"Expected '{value}' but got '{t.value}'", t)
        return self.advance()

    def match(self, type_: str, value: str = None) -> bool:
        t = self.current()
        if t is None: return False
        if t.type != type_: return False
        if value and t.value != value: return False
        return True

    def match_after_newlines(self, type_: str, value: str = None) -> bool:
        """Peek past newlines to see if the next real token matches."""
        i = self.pos
        while i < len(self.tokens) and self.tokens[i].type == "NEWLINE":
            i += 1
        if i >= len(self.tokens): return False
        t = self.tokens[i]
        if t.type != type_: return False
        if value and t.value != value: return False
        return True

    def current_col(self) -> int:
        """Column of the current non-newline token."""
        i = self.pos
        while i < len(self.tokens) and self.tokens[i].type == "NEWLINE":
            i += 1
        if i >= len(self.tokens): return 0
        return self.tokens[i].col

    # ─── Entry Point ───────────────────────────────────────────────────────────

    def parse(self) -> Dict:
        body = self.parse_stmts_at_col(1)
        return {"type": "Program", "body": body}

    def parse_stmts_at_col(self, col: int) -> List[Dict]:
        """Parse statements that start at exactly `col`."""
        stmts = []
        while True:
            self.skip_newlines()
            t = self.current()
            if t is None: break
            if t.col < col: break  # dedented — end of block
            if t.col > col: break  # over-indented (shouldn't happen at top level)
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return stmts

    def parse_block(self) -> List[Dict]:
        """Parse a colon + indented block."""
        self.expect("COLON")
        self.skip_newlines()
        t = self.current()
        if t is None:
            return []
        block_col = t.col
        if block_col <= 1:
            raise ParseError("Expected indented block", t)
        return self.parse_stmts_at_col(block_col)

    # ─── Statements ────────────────────────────────────────────────────────────

    def parse_statement(self) -> Optional[Dict]:
        self.skip_newlines()
        t = self.current()
        if t is None: return None

        if t.type == "KEYWORD":
            if t.value == "def":    return self.parse_function_def()
            if t.value == "return": return self.parse_return()
            if t.value == "if":     return self.parse_if()
            if t.value == "while":  return self.parse_while()
            if t.value == "for":    return self.parse_for()
            if t.value == "pass":   self.advance(); return {"type": "Pass"}
            if t.value == "break":  self.advance(); return {"type": "Break"}
            if t.value == "continue": self.advance(); return {"type": "Continue"}
            if t.value == "print":  return self.parse_print()

        return self.parse_assignment_or_expr()

    def parse_function_def(self) -> Dict:
        self.expect("KEYWORD", "def")
        name = self.expect("IDENTIFIER").value
        self.expect("LPAREN")
        params = []
        while not self.match("RPAREN"):
            pname = self.expect("IDENTIFIER").value
            ptype = None
            if self.match("COLON"):
                self.advance()
                ptype = self.expect("IDENTIFIER").value
            params.append({"name": pname, "type": ptype})
            if self.match("COMMA"): self.advance()
        self.expect("RPAREN")
        return_type = None
        if self.match("MINUS"):
            self.advance()
            if self.match("GT"):
                self.advance()
                return_type = self.expect("IDENTIFIER").value
        body = self.parse_block()
        return {"type": "FunctionDef", "name": name, "params": params, "return_type": return_type, "body": body}

    def parse_return(self) -> Dict:
        self.expect("KEYWORD", "return")
        value = None
        t = self.current()
        if t and t.type not in ("NEWLINE",):
            value = self.parse_expression()
        return {"type": "Return", "value": value}

    def parse_print(self) -> Dict:
        self.expect("KEYWORD", "print")
        self.expect("LPAREN")
        args = []
        while not self.match("RPAREN"):
            args.append(self.parse_expression())
            if self.match("COMMA"): self.advance()
        self.expect("RPAREN")
        return {"type": "Print", "args": args}

    def parse_if(self) -> Dict:
        stmt_col = self.current().col
        self.expect("KEYWORD", "if")
        condition = self.parse_expression()
        body = self.parse_block()
        elseif_clauses = []
        else_body = None

        while True:
            self.skip_newlines()
            t = self.current()
            if t is None: break
            if t.col != stmt_col: break
            if t.type == "KEYWORD" and t.value == "elif":
                self.advance()
                ec = self.parse_expression()
                eb = self.parse_block()
                elseif_clauses.append({"condition": ec, "body": eb})
            elif t.type == "KEYWORD" and t.value == "else":
                self.advance()
                else_body = self.parse_block()
                break
            else:
                break

        return {"type": "If", "condition": condition, "body": body, "elseif": elseif_clauses, "else": else_body}

    def parse_while(self) -> Dict:
        self.expect("KEYWORD", "while")
        condition = self.parse_expression()
        body = self.parse_block()
        return {"type": "While", "condition": condition, "body": body}

    def parse_for(self) -> Dict:
        self.expect("KEYWORD", "for")
        var = self.expect("IDENTIFIER").value
        self.expect("KEYWORD", "in")
        iterable = self.parse_expression()
        body = self.parse_block()
        return {"type": "For", "var": var, "iterable": iterable, "body": body}

    def parse_assignment_or_expr(self) -> Dict:
        expr = self.parse_expression()
        if self.match("EQUALS"):
            if expr.get("type") != "Identifier":
                raise ParseError("Left side of assignment must be identifier")
            self.advance()
            right = self.parse_expression()
            return {"type": "Assignment", "left": expr["name"], "right": right}
        for op_tok, op in [("PLUS_EQ", "+"), ("MINUS_EQ", "-"), ("STAR_EQ", "*"), ("DIV_EQ", "/")]:
            if self.match(op_tok):
                self.advance()
                right = self.parse_expression()
                return {"type": "Assignment", "left": expr["name"],
                        "right": {"type": "BinaryOp", "op": op, "left": expr, "right": right}}
        return {"type": "ExprStatement", "expr": expr}

    # ─── Expressions ───────────────────────────────────────────────────────────

    def parse_expression(self): return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match("KEYWORD", "or"):
            self.advance(); right = self.parse_and()
            left = {"type": "BinaryOp", "op": "or", "left": left, "right": right}
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.match("KEYWORD", "and"):
            self.advance(); right = self.parse_not()
            left = {"type": "BinaryOp", "op": "and", "left": left, "right": right}
        return left

    def parse_not(self):
        if self.match("KEYWORD", "not"):
            self.advance(); return {"type": "UnaryOp", "op": "not", "operand": self.parse_comparison()}
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_additive()
        ops = {"EQ_EQ": "==", "NEQ": "!=", "LT": "<", "GT": ">", "LTE": "<=", "GTE": ">="}
        while self.current() and self.current().type in ops:
            op = ops[self.advance().type]; right = self.parse_additive()
            left = {"type": "BinaryOp", "op": op, "left": left, "right": right}
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.current() and self.current().type in ("PLUS", "MINUS"):
            op = self.advance().value; right = self.parse_multiplicative()
            left = {"type": "BinaryOp", "op": op, "left": left, "right": right}
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.current() and self.current().type in ("STAR", "SLASH", "PERCENT"):
            op = self.advance().value; right = self.parse_unary()
            left = {"type": "BinaryOp", "op": op, "left": left, "right": right}
        return left

    def parse_unary(self):
        if self.match("MINUS"):
            self.advance(); return {"type": "UnaryOp", "op": "-", "operand": self.parse_primary()}
        return self.parse_primary()

    def parse_primary(self):
        self.skip_newlines()
        t = self.current()
        if t is None: raise ParseError("Unexpected end of input in expression")

        if t.type == "NUMBER":    self.advance(); return {"type": "Number", "value": int(t.value)}
        if t.type == "FLOAT":     self.advance(); return {"type": "Float", "value": float(t.value)}
        if t.type == "STRING":    self.advance(); return {"type": "String", "value": t.value.strip('"\'') }
        if t.type == "KEYWORD" and t.value in ("True", "False"):
            self.advance(); return {"type": "Boolean", "value": t.value == "True"}
        if t.type == "KEYWORD" and t.value == "None":
            self.advance(); return {"type": "None"}

        if t.type == "IDENTIFIER":
            self.advance()
            if self.match("LPAREN"):
                self.advance()
                args = []
                while not self.match("RPAREN"):
                    args.append(self.parse_expression())
                    if self.match("COMMA"): self.advance()
                self.expect("RPAREN")
                return {"type": "FunctionCall", "name": t.value, "args": args}
            if self.match("DOT"):
                self.advance()
                member = self.expect("IDENTIFIER").value
                if self.match("LPAREN"):
                    self.advance()
                    args = []
                    while not self.match("RPAREN"):
                        args.append(self.parse_expression())
                        if self.match("COMMA"): self.advance()
                    self.expect("RPAREN")
                    return {"type": "MethodCall", "object": t.value, "method": member, "args": args}
                return {"type": "MemberAccess", "object": t.value, "member": member}
            return {"type": "Identifier", "name": t.value}

        if t.type == "LPAREN":
            self.advance(); expr = self.parse_expression(); self.expect("RPAREN"); return expr

        if t.type == "LBRACKET":
            self.advance()
            elements = []
            while not self.match("RBRACKET"):
                elements.append(self.parse_expression())
                if self.match("COMMA"): self.advance()
            self.expect("RBRACKET")
            return {"type": "List", "elements": elements}

        raise ParseError(f"Unexpected token: {t.type} ('{t.value}')", t)


def parse(tokens) -> Dict:
    p = Parser(tokens)
    return p.parse()
