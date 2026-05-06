import sys
from lexer import lexer
from parser import parser
from semantic import semantic_analysis
from ir import generate_ir
from optimizer import optimize_ir
from codegen import generate_svg


def debug_print(title, data):
    print(f"\n--- {title} ---")
    print(data)


def main():
    args = sys.argv

    # -------------------------
    # Usage check
    # -------------------------
    if len(args) < 2:
        print("Usage:")
        print("python main.py file.logo -o output.svg")
        print("python main.py file.logo --debug")
        return

    # -------------------------
    # Debug flag
    # -------------------------
    debug = "--debug" in args

    # -------------------------
    # Input file
    # -------------------------
    input_file = args[1]

    try:
        with open(input_file, "r") as f:
            code = f.read()
    except:
        print("Error: File not found")
        return

    # -------------------------
    # Output file
    # -------------------------
    output_file = "output.svg"
    if "-o" in args:
        idx = args.index("-o")
        if idx + 1 < len(args):
            output_file = args[idx + 1]

    # -------------------------
    # PIPELINE
    # -------------------------
    if debug:
        debug_print("SOURCE CODE", code)

    tokens = lexer(code)
    if debug:
        debug_print("TOKENS", tokens)

    ast = parser(tokens)
    if debug:
        debug_print("AST", ast)

    ast, symbols, procedures = semantic_analysis(ast)

    ir = generate_ir(ast)
    if debug:
        debug_print("IR BEFORE OPT", ir)

    ir = optimize_ir(ir)
    if debug:
        debug_print("IR AFTER OPT", ir)

    generate_svg(ir, output_file)

    print(f"\n✅ Output generated: {output_file}")


if __name__ == "__main__":
    main()