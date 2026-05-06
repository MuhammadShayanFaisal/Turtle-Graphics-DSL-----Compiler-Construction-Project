def generate_ir(ast):
    ir = []

    def gen(stmt):
        name = stmt.__class__.__name__

        if name == "SetVar":
            ir.append(("SET", stmt.name, stmt.value))

        elif name == "Command":
            ir.append(("CMD", stmt.name, stmt.value))

        elif name == "Repeat":
            ir.append(("REPEAT_START", stmt.count))
            for s in stmt.body:
                gen(s)
            ir.append(("REPEAT_END", None))

        elif name == "Proc":
            ir.append(("PROC_START", stmt.name, stmt.param))
            for s in stmt.body:
                gen(s)
            ir.append(("PROC_END", stmt.name))

        elif name == "Call":
            ir.append(("CALL", stmt.name, stmt.arg))

    for stmt in ast:
        gen(stmt)

    return ir