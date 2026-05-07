"""
parser.py  —  TurtleScript Recursive-Descent Parser
Builds an AST from the token stream produced by lexer.py.

Grammar (simplified EBNF):
  program    ::= statement* EOF
  statement  ::= set_stmt | repeat_stmt | proc_stmt
               | if_stmt  | call_stmt   | cmd_stmt
  set_stmt   ::= SET IDENT '=' expr
  repeat_stmt::= REPEAT expr NEWLINE statement* END
  proc_stmt  ::= PROC IDENT IDENT? NEWLINE statement* END
  if_stmt    ::= IF expr NEWLINE statement* [ELSE NEWLINE statement*] END
  call_stmt  ::= CALL IDENT expr?
  cmd_stmt   ::= KEYWORD [expr]
  expr       ::= NUMBER | FLOAT | IDENT | expr OP expr
"""

class Node:
    pass


class Command(Node):
    """A single drawing command, e.g. FORWARD 80, PENDOWN, COLOR "red"."""
    def __init__(self, name: str, value=None, line: int = 0):
        self.name  = name
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"Command({self.name}, value={self.value!r})"


class SetVar(Node):
    """Variable assignment: SET name = value"""
    def __init__(self, name: str, value, line: int = 0):
        self.name  = name
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"SetVar({self.name!r} = {self.value!r})"


class Repeat(Node):
    """REPEAT count ... END"""
    def __init__(self, count, body: list, line: int = 0):
        self.count = count
        self.body  = body
        self.line  = line

    def __repr__(self):
        return f"Repeat(count={self.count!r}, body={self.body!r})"


class Proc(Node):
    """PROC name [param] ... END"""
    def __init__(self, name: str, param: str | None, body: list, line: int = 0):
        self.name  = name
        self.param = param
        self.body  = body
        self.line  = line

    def __repr__(self):
        return f"Proc({self.name!r}, param={self.param!r}, body={self.body!r})"


class Call(Node):
    """CALL name [arg]"""
    def __init__(self, name: str, arg=None, line: int = 0):
        self.name = name
        self.arg  = arg
        self.line = line

    def __repr__(self):
        return f"Call({self.name!r}, arg={self.arg!r})"


class IfStmt(Node):
    """IF condition ... [ELSE ...] END"""
    def __init__(self, condition, then_body: list, else_body: list, line: int = 0):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body
        self.line      = line

    def __repr__(self):
        return (f"If(cond={self.condition!r}, "
                f"then={self.then_body!r}, else={self.else_body!r})")

def parser(tokens: list) -> list:
    """
    Parse *tokens* into an AST (list of Node).
    Skips NEWLINE tokens transparently.
    Reports errors with line/col info and continues where possible.
    """
    toks = [t for t in tokens if t.type != "NEWLINE"]
    pos  = [0]          
    errors: list[str] = []

    def peek(offset: int = 0):
        idx = pos[0] + offset
        return toks[idx] if idx < len(toks) else None

    def advance():
        t = toks[pos[0]] if pos[0] < len(toks) else None
        pos[0] += 1
        return t

    def expect_ident(context: str = ""):
        t = peek()
        if t and t.type == "IDENT":
            return advance()
        loc = f" at line {t.line}" if t else ""
        errors.append(
            f"  Syntax Error{loc}: expected identifier {context}, "
            f"got {t.type}({t.value!r})" if t else
            f"  Syntax Error: expected identifier {context}, got EOF"
        )
        return None

    def parse_expr():
        """
        Parse a simple expression: NUMBER | FLOAT | IDENT | STRING.
        No full infix parsing — keeps things simple for this DSL.
        If a constant arithmetic expression appears (e.g. 2 + 3),
        constant-fold it here for the constant-folding optimisation.
        """
        t = peek()
        if t is None:
            return None
        if t.type in ("NUMBER", "FLOAT"):
            advance()
            left = t.value
            op_t = peek()
            if op_t and op_t.type == "OP" and op_t.value in ("+", "-", "*", "/"):
                right_t = peek(1)
                if right_t and right_t.type in ("NUMBER", "FLOAT"):
                    advance()  
                    advance() 
                    op = op_t.value
                    r  = right_t.value
                    if op == "+": left = left + r
                    elif op == "-": left = left - r
                    elif op == "*": left = left * r
                    elif op == "/": left = left / r if r != 0 else left
            return left
        if t.type in ("IDENT", "STRING"):
            advance()
            return t.value
        return None

    def parse_block(end_keywords=("END",)):
        body = []
        while True:
            t = peek()
            if t is None:
                errors.append("  Syntax Error: unexpected EOF inside block")
                break
            if t.type == "KEYWORD" and t.value in end_keywords:
                advance()  
                break
            stmt = parse_statement()
            if stmt:
                body.append(stmt)
        return body

    def parse_statement():
        t = peek()
        if t is None:
            return None

        if t.type == "KEYWORD" and t.value == "SET":
            line = t.line
            advance()                  
            name_t = expect_ident("after SET")
            if name_t is None:
                return None
            name = name_t.value
            eq = peek()
            if eq and eq.type == "OP" and eq.value == "=":
                advance()               
            value = parse_expr()
            return SetVar(name, value, line)

        if t.type == "KEYWORD" and t.value == "REPEAT":
            line = t.line
            advance()
            count = parse_expr()
            body  = parse_block(end_keywords=("END",))
            return Repeat(count, body, line)

        if t.type == "KEYWORD" and t.value == "PROC":
            line = t.line
            advance()
            name_t = expect_ident("after PROC")
            if name_t is None:
                return None
            name  = name_t.value
            param = None
            nxt   = peek()
            if nxt and nxt.type == "IDENT":
                param = advance().value
            body  = parse_block(end_keywords=("END",))
            return Proc(name, param, body, line)

        if t.type == "KEYWORD" and t.value == "IF":
            line = t.line
            advance()
            condition   = parse_expr()
            # parse until ELSE or END
            then_body: list = []
            else_body: list = []
            while True:
                tt = peek()
                if tt is None:
                    errors.append(f"  Syntax Error at line {line}: unclosed IF")
                    break
                if tt.type == "KEYWORD" and tt.value == "END":
                    advance()
                    break
                if tt.type == "KEYWORD" and tt.value == "ELSE":
                    advance()
                    else_body = parse_block(end_keywords=("END",))
                    break
                s = parse_statement()
                if s:
                    then_body.append(s)
            return IfStmt(condition, then_body, else_body, line)

        if t.type == "KEYWORD" and t.value == "CALL":
            line = t.line
            advance()
            name_t = expect_ident("after CALL")
            if name_t is None:
                return None
            name = name_t.value
            arg  = parse_expr()         
            return Call(name, arg, line)

        if t.type == "KEYWORD" and t.value in (
            "FORWARD", "BACK", "LEFT", "RIGHT",
            "PENUP", "PENDOWN", "COLOR", "PENWIDTH", "CIRCLE",
        ):
            line = t.line
            advance()
            val = parse_expr()          
            return Command(t.value, val, line)

        errors.append(
            f"  Syntax Error at line {t.line}: "
            f"unexpected token {t.type}({t.value!r})"
        )
        advance()
        return None

    ast = []
    while peek() is not None:
        s = parse_statement()
        if s:
            ast.append(s)

    if errors:
        print("\n[PARSER] Errors found:")
        for e in errors:
            print(e)
    return ast