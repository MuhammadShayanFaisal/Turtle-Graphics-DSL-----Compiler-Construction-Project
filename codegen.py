import math

def generate_svg(ir, output_file):
    # -------------------------------
    # Turtle State
    # -------------------------------
    x, y = 0, 0
    angle = 0

    pen = True
    color = "black"
    width = 1

    lines = []

    # -------------------------------
    # Runtime Memory (Variables)
    # -------------------------------
    symbols = {}

    # -------------------------------
    # Helper: Resolve values
    # -------------------------------
    def resolve(val):
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            return symbols.get(val, 0)  # default 0 if not found
        return 0

    # -------------------------------
    # REPEAT Stack
    # -------------------------------
    stack = []

    i = 0
    while i < len(ir):
        instr = ir[i]

        # -------------------------------
        # SET (Variable assignment)
        # -------------------------------
        if instr[0] == "SET":
            var_name = instr[1]
            value = resolve(instr[2])
            symbols[var_name] = value

        # -------------------------------
        # COMMANDS
        # -------------------------------
        elif instr[0] == "CMD":
            cmd, val = instr[1], instr[2]

            val = resolve(val)

            if cmd == "FORWARD":
                nx = x + val * math.cos(math.radians(angle))
                ny = y + val * math.sin(math.radians(angle))

                if pen:
                    lines.append((x, y, nx, ny, color, width))

                x, y = nx, ny

            elif cmd == "BACK":
                nx = x - val * math.cos(math.radians(angle))
                ny = y - val * math.sin(math.radians(angle))

                if pen:
                    lines.append((x, y, nx, ny, color, width))

                x, y = nx, ny

            elif cmd == "RIGHT":
                angle += val

            elif cmd == "LEFT":
                angle -= val

            elif cmd == "PENUP":
                pen = False

            elif cmd == "PENDOWN":
                pen = True

            elif cmd == "COLOR":
                # val should be string like "red"
                color = str(val)

            elif cmd == "PENWIDTH":
                width = val

        # -------------------------------
        # REPEAT START
        # -------------------------------
        elif instr[0] == "REPEAT_START":
            count = resolve(instr[1])
            stack.append((i, count))

        # -------------------------------
        # REPEAT END
        # -------------------------------
        elif instr[0] == "REPEAT_END":
            start, count = stack[-1]
            count -= 1

            if count > 0:
                stack[-1] = (start, count)
                i = start
            else:
                stack.pop()

        i += 1

    # -------------------------------
    # WRITE SVG
    # -------------------------------
    with open(output_file, "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg">\n')

        for x1, y1, x2, y2, c, w in lines:
            f.write(
                f'<line x1="{x1}" y1="{y1}" '
                f'x2="{x2}" y2="{y2}" '
                f'stroke="{c}" stroke-width="{w}"/>\n'
            )

        f.write('</svg>')