def semantic_analysis(ast):
    symbols = set()
    procedures = {}

    for stmt in ast:

        # Variable declaration
        if stmt.__class__.__name__ == "SetVar":
            symbols.add(stmt.name)

        # Variable usage check
        if stmt.__class__.__name__ == "Command":
            if isinstance(stmt.value, str) and stmt.value not in symbols:
                print(f"Semantic Error: Undefined variable '{stmt.value}'")
                exit(1)

        # Procedure store
        if stmt.__class__.__name__ == "Proc":
            procedures[stmt.name] = stmt

        # Procedure call check
        if stmt.__class__.__name__ == "Call":
            if stmt.name not in procedures:
                print(f"Semantic Error: Undefined procedure '{stmt.name}'")
                exit(1)

    return ast, symbols, procedures