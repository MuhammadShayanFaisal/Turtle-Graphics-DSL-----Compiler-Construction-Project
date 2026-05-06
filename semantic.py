"""
semantic.py  —  TurtleScript Semantic Analyser
Performs:
  1. Symbol table management with proper scope stack
     (global scope + one scope per PROC body)
  2. Undefined-variable detection
  3. Undefined-procedure detection
  4. Procedure arity check (expected param count vs call arg)
Collects ALL errors and reports them together (no early exit).
"""


def semantic_analysis(ast: list):
    """
    Walk *ast*, populate the symbol table, and validate semantics.

    Returns:
        (ast, global_symbols, procedures)
        ast              — the original ast (unchanged; pass-through)
        global_symbols   — dict of {name: value} for global variables
        procedures       — dict of {name: Proc node} for defined procedures
    """
    errors: list[str] = []

    # Scope stack: list of dicts.  Index 0 = global, deeper = proc-local.
    scope_stack: list[dict] = [{}]   # global scope
    procedures: dict = {}            # name → Proc node

    # ── helpers ──────────────────────────────────────────────────────────

    def current_scope() -> dict:
        return scope_stack[-1]

    def define(name: str, value=None):
        """Define a variable in the current scope."""
        current_scope()[name] = value

    def lookup(name: str) -> bool:
        """Return True if *name* is visible in any enclosing scope."""
        for scope in reversed(scope_stack):
            if name in scope:
                return True
        return False

    def push_scope():
        scope_stack.append({})

    def pop_scope():
        scope_stack.pop()

    # ── recursive walker ─────────────────────────────────────────────────

    def walk(stmts: list):
        for stmt in stmts:
            node_type = stmt.__class__.__name__

            # ── SET ───────────────────────────────────────────────────────
            if node_type == "SetVar":
                # Check if the assigned value is a known variable reference
                if isinstance(stmt.value, str) and not lookup(stmt.value):
                    errors.append(
                        f"  Semantic Error at line {stmt.line}: "
                        f"undefined variable '{stmt.value}' used in SET"
                    )
                define(stmt.name, stmt.value)

            # ── COMMAND ───────────────────────────────────────────────────
            elif node_type == "Command":
                if isinstance(stmt.value, str) and not lookup(stmt.value):
                    errors.append(
                        f"  Semantic Error at line {stmt.line}: "
                        f"undefined variable '{stmt.value}' "
                        f"used in {stmt.name}"
                    )

            # ── PROC ──────────────────────────────────────────────────────
            elif node_type == "Proc":
                procedures[stmt.name] = stmt
                push_scope()
                # The parameter is visible inside the proc body
                if stmt.param:
                    define(stmt.param, None)
                walk(stmt.body)
                pop_scope()

            # ── CALL ──────────────────────────────────────────────────────
            elif node_type == "Call":
                if stmt.name not in procedures:
                    errors.append(
                        f"  Semantic Error at line {stmt.line}: "
                        f"call to undefined procedure '{stmt.name}'"
                    )
                else:
                    proc = procedures[stmt.name]
                    # Check argument: if proc has a param, a call arg is expected
                    if proc.param and stmt.arg is None:
                        errors.append(
                            f"  Semantic Error at line {stmt.line}: "
                            f"procedure '{stmt.name}' expects an argument, "
                            f"none given"
                        )
                    # Check arg is a known variable (if it is an identifier)
                    if isinstance(stmt.arg, str) and not lookup(stmt.arg):
                        errors.append(
                            f"  Semantic Error at line {stmt.line}: "
                            f"undefined variable '{stmt.arg}' "
                            f"passed to '{stmt.name}'"
                        )

            # ── REPEAT ────────────────────────────────────────────────────
            elif node_type == "Repeat":
                if isinstance(stmt.count, str) and not lookup(stmt.count):
                    errors.append(
                        f"  Semantic Error at line {stmt.line}: "
                        f"undefined variable '{stmt.count}' in REPEAT"
                    )
                push_scope()
                walk(stmt.body)
                pop_scope()

            # ── IF ────────────────────────────────────────────────────────
            elif node_type == "IfStmt":
                if isinstance(stmt.condition, str) and not lookup(stmt.condition):
                    errors.append(
                        f"  Semantic Error at line {stmt.line}: "
                        f"undefined variable '{stmt.condition}' in IF"
                    )
                push_scope()
                walk(stmt.then_body)
                pop_scope()
                if stmt.else_body:
                    push_scope()
                    walk(stmt.else_body)
                    pop_scope()

    walk(ast)

    if errors:
        print("\n[SEMANTIC] Errors found:")
        for e in errors:
            print(e)

    # Return the global scope (first item in stack) as the symbol table
    return ast, scope_stack[0], procedures