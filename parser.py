class Node: pass

class Command(Node):
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

class Repeat(Node):
    def __init__(self, count, body):
        self.count = count
        self.body = body

class SetVar(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Proc(Node):
    def __init__(self, name, param, body):
        self.name = name
        self.param = param
        self.body = body

class Call(Node):
    def __init__(self, name, arg):
        self.name = name
        self.arg = arg


def parser(tokens):
    i = 0

    def parse_block():
        nonlocal i
        stmts = []

        while i < len(tokens):
            t = tokens[i]

            if t.value == "END":
                i += 1
                break

            # SET
            if t.value == "SET":
                name = tokens[i+1].value
                value = tokens[i+3].value
                stmts.append(SetVar(name, value))
                i += 4

            # REPEAT
            elif t.value == "REPEAT":
                count = tokens[i+1].value
                i += 2
                body = parse_block()
                stmts.append(Repeat(count, body))

            # PROC
            elif t.value == "PROC":
                name = tokens[i+1].value
                param = tokens[i+2].value
                i += 3
                body = parse_block()
                stmts.append(Proc(name, param, body))

            # CALL
            elif t.value == "CALL":
                name = tokens[i+1].value
                arg = tokens[i+2].value
                stmts.append(Call(name, arg))
                i += 3

            # COMMAND
            else:
                name = t.value
                val = None
                if i+1 < len(tokens) and tokens[i+1].type == "NUMBER":
                    val = tokens[i+1].value
                    i += 2
                else:
                    i += 1
                stmts.append(Command(name, val))

        return stmts

    return parse_block()