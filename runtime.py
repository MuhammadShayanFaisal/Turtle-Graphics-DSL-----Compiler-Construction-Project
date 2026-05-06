import math

class TurtleState:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0
        self.pen = True
        self.color = "black"
        self.width = 1
        self.lines = []


def run(ast):
    state = TurtleState()
    symbols = {}
    procedures = {}

    def exec_stmt(stmt):
        if stmt.__class__.__name__ == "SetVar":
            symbols[stmt.name] = stmt.value

        elif stmt.__class__.__name__ == "Command":
            val = stmt.value if stmt.value is not None else 0

            if stmt.name == "FORWARD":
                nx = state.x + val * math.cos(math.radians(state.angle))
                ny = state.y + val * math.sin(math.radians(state.angle))

                if state.pen:
                    state.lines.append((state.x, state.y, nx, ny, state.color, state.width))

                state.x, state.y = nx, ny

            elif stmt.name == "RIGHT":
                state.angle += val

            elif stmt.name == "LEFT":
                state.angle -= val

            elif stmt.name == "PENUP":
                state.pen = False

            elif stmt.name == "PENDOWN":
                state.pen = True

            elif stmt.name == "COLOR":
                state.color = val

            elif stmt.name == "PENWIDTH":
                state.width = val

        elif stmt.__class__.__name__ == "Repeat":
            for _ in range(stmt.count):
                for s in stmt.body:
                    exec_stmt(s)

        elif stmt.__class__.__name__ == "Proc":
            procedures[stmt.name] = stmt

        elif stmt.__class__.__name__ == "Call":
            proc = procedures[stmt.name]
            local = symbols.copy()
            local[proc.param] = stmt.arg

            for s in proc.body:
                exec_stmt(s)

    for s in ast:
        exec_stmt(s)

    return state