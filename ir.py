"""
ir.py  —  TurtleScript Intermediate Representation (Three-Address Code)
Translates the AST into a flat list of TAC tuples:

  ('SET',          var_name, value)
  ('CMD',          cmd_name, value)
  ('REPEAT_START', count)
  ('REPEAT_END',   None)
  ('PROC_START',   name,     param_or_None)
  ('PROC_END',     name)
  ('CALL',         name,     arg_or_None)
  ('IF_TRUE',      condition, label)
  ('LABEL',        label)
  ('JUMP',         label)
"""

_label_counter = [0]


def _new_label(prefix: str = "L") -> str:
    _label_counter[0] += 1
    return f"{prefix}{_label_counter[0]}"


def generate_ir(ast: list) -> list:
    """Walk the AST and emit a flat TAC instruction list."""
    ir: list = []

    def emit(*args):
        ir.append(args)

    def gen(stmt):
        name = stmt.__class__.__name__

        # ── SET ───────────────────────────────────────────────────────────
        if name == "SetVar":
            emit("SET", stmt.name, stmt.value)

        # ── COMMAND ───────────────────────────────────────────────────────
        elif name == "Command":
            emit("CMD", stmt.name, stmt.value)

        # ── REPEAT ────────────────────────────────────────────────────────
        elif name == "Repeat":
            emit("REPEAT_START", stmt.count)
            for s in stmt.body:
                gen(s)
            emit("REPEAT_END", None)

        # ── PROC ──────────────────────────────────────────────────────────
        elif name == "Proc":
            emit("PROC_START", stmt.name, stmt.param)
            for s in stmt.body:
                gen(s)
            emit("PROC_END", stmt.name)

        # ── CALL ──────────────────────────────────────────────────────────
        elif name == "Call":
            emit("CALL", stmt.name, stmt.arg)

        # ── IF / ELSE ─────────────────────────────────────────────────────
        elif name == "IfStmt":
            else_label = _new_label("ELSE")
            end_label  = _new_label("ENDIF")

            emit("IF_FALSE", stmt.condition, else_label)
            for s in stmt.then_body:
                gen(s)
            emit("JUMP", end_label)
            emit("LABEL", else_label)
            for s in stmt.else_body:
                gen(s)
            emit("LABEL", end_label)

    for stmt in ast:
        gen(stmt)

    return ir