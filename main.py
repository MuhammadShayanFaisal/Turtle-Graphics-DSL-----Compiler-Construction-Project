"""
main.py  —  TurtleScript Compiler Entry Point

Usage:
  python main.py <file.logo> [-o output.svg]   Compile file to SVG
  python main.py <file.logo> --debug           Compile with verbose phase output
  python main.py --interactive                 Start interactive REPL
"""

import sys

from lexer    import lexer
from parser   import parser
from semantic import semantic_analysis
from ir       import generate_ir
from optimizer import optimize_ir
from codegen  import generate_svg


# ─────────────────────────────────────────────────────────────────────────────
# Debug helpers
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_tokens(tokens: list) -> str:
    lines = []
    for t in tokens:
        lines.append(f"  {t!r}")
    return "\n".join(lines)


def _fmt_ast(ast: list, indent: int = 0) -> str:
    pad = "  " * indent
    lines = []
    for node in ast:
        name = node.__class__.__name__
        if name == "Repeat":
            lines.append(f"{pad}Repeat(count={node.count!r})")
            lines.append(_fmt_ast(node.body, indent + 1))
        elif name == "Proc":
            lines.append(f"{pad}Proc({node.name!r}, param={node.param!r})")
            lines.append(_fmt_ast(node.body, indent + 1))
        elif name == "IfStmt":
            lines.append(f"{pad}If(cond={node.condition!r})")
            lines.append(f"{pad}  THEN:")
            lines.append(_fmt_ast(node.then_body, indent + 2))
            if node.else_body:
                lines.append(f"{pad}  ELSE:")
                lines.append(_fmt_ast(node.else_body, indent + 2))
        else:
            lines.append(f"{pad}{node!r}")
    return "\n".join(lines)


def _fmt_ir(ir: list) -> str:
    lines = []
    for instr in ir:
        lines.append("  " + str(instr))
    return "\n".join(lines)


def debug_print(title: str, content: str):
    print(f"\n--- {title} ---")
    print(content)


# ─────────────────────────────────────────────────────────────────────────────
# Compile pipeline
# ─────────────────────────────────────────────────────────────────────────────

def compile_code(code: str, output_file: str = "output.svg", debug: bool = False):
    if debug:
        debug_print("SOURCE CODE", code)

    # ── Phase 1: Lexical Analysis ─────────────────────────────────────────
    tokens = lexer(code)
    if debug:
        debug_print("TOKENS", _fmt_tokens(tokens))

    # ── Phase 2: Syntax Analysis ──────────────────────────────────────────
    ast = parser(tokens)
    if debug:
        debug_print("AST", _fmt_ast(ast))

    # ── Phase 3: Semantic Analysis ────────────────────────────────────────
    ast, symbols, procedures = semantic_analysis(ast)
    if debug:
        debug_print("SYMBOL TABLE (global)", str(symbols))
        debug_print("PROCEDURES DEFINED",
                    str({k: f"param={v.param}" for k, v in procedures.items()}))

    # ── Phase 4: IR Generation ────────────────────────────────────────────
    ir = generate_ir(ast)
    if debug:
        debug_print("IR BEFORE OPTIMISATION", _fmt_ir(ir))

    # ── Phase 5: Optimisation ─────────────────────────────────────────────
    ir_opt = optimize_ir(ir)
    if debug:
        debug_print("IR AFTER OPTIMISATION", _fmt_ir(ir_opt))

    # ── Phase 6: Code Generation ──────────────────────────────────────────
    generate_svg(ir_opt, output_file)
    print(f"\n✅ Output generated: {output_file}")


# ─────────────────────────────────────────────────────────────────────────────
# Interactive REPL
# ─────────────────────────────────────────────────────────────────────────────

def repl():
    print("TurtleScript REPL — type multi-line programs, then blank line to run.")
    print("  Commands: 'exit' to quit, 'clear' to reset.\n")
    session_num = 0
    while True:
        lines_buf = []
        try:
            while True:
                prompt = ">>> " if not lines_buf else "... "
                line   = input(prompt)
                if line.strip().lower() == "exit":
                    print("Goodbye!")
                    return
                if line.strip().lower() == "clear":
                    lines_buf = []
                    print("[cleared]")
                    break
                if line == "" and lines_buf:
                    break
                lines_buf.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if not lines_buf:
            continue

        code = "\n".join(lines_buf)
        session_num += 1
        out_file = f"repl_{session_num:03d}.svg"
        compile_code(code, output_file=out_file, debug=False)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return

    # Interactive REPL
    if "--interactive" in args:
        repl()
        return

    # Normal compile
    input_file  = args[0]
    debug       = "--debug" in args
    output_file = "output.svg"

    if "-o" in args:
        idx = args.index("-o")
        if idx + 1 < len(args):
            output_file = args[idx + 1]

    try:
        with open(input_file, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: file '{input_file}' not found.")
        sys.exit(1)

    compile_code(code, output_file=output_file, debug=debug)


if __name__ == "__main__":
    main()