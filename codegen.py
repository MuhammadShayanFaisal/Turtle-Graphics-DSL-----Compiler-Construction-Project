"""
codegen.py  —  TurtleScript Code Generator / Runtime VM
Interprets the optimised TAC IR and produces an SVG file.

Turtle coordinate system:
  • angle = 0   → facing right (East)
  • angle is in degrees, increasing clockwise (SVG convention)
  • Starting position is the centre of the canvas

Handles:
  SET, CMD (FORWARD/BACK/LEFT/RIGHT/PENUP/PENDOWN/COLOR/PENWIDTH/CIRCLE),
  REPEAT_START/END, PROC_START/END, CALL, IF_FALSE/JUMP/LABEL
"""

import math


# ── Canvas settings ───────────────────────────────────────────────────────────
CANVAS_W = 800
CANVAS_H = 800
ORIGIN_X = CANVAS_W / 2
ORIGIN_Y = CANVAS_H / 2


def generate_svg(ir: list, output_file: str):
    # ── Turtle state ─────────────────────────────────────────────────────────
    state = {
        "x":     ORIGIN_X,
        "y":     ORIGIN_Y,
        "angle": -90.0,     # face upward (North) by convention, like LOGO
        "pen":   True,
        "color": "black",
        "width": 2,
    }

    symbols: dict  = {}   # global + local variable store
    lines:   list  = []   # collected SVG drawing elements
    circles: list  = []   # collected SVG circles

    # ── Build PROC definition table ───────────────────────────────────────────
    procs: dict = {}      # name → (param, [instructions])
    i = 0
    while i < len(ir):
        instr = ir[i]
        if instr[0] == "PROC_START":
            _, proc_name, param = instr
            body = []
            i += 1
            depth = 1
            while i < len(ir):
                inner = ir[i]
                if inner[0] == "PROC_START":
                    depth += 1
                if inner[0] == "PROC_END":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                body.append(inner)
                i += 1
            procs[proc_name] = (param, body)
        else:
            i += 1

    # ── Label map: label_name → index in ir ──────────────────────────────────
    label_map: dict = {}
    for idx, instr in enumerate(ir):
        if instr[0] == "LABEL":
            label_map[instr[1]] = idx

    # ── Resolve a value: constant or variable lookup ──────────────────────────
    def resolve(val):
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            return symbols.get(val, 0)
        return 0

    # ── Execute a flat list of TAC instructions ───────────────────────────────
    def execute(instructions: list, local_syms: dict | None = None):
        """
        Execute *instructions*.
        If *local_syms* is provided (proc call context), those bindings
        shadow the global symbols for the duration of the call.
        """
        nonlocal state

        # Overlay local scope on global symbols
        saved = {}
        if local_syms:
            for k, v in local_syms.items():
                saved[k] = symbols.get(k)   # save old value
                symbols[k] = v

        repeat_stack = []   # [(start_index, remaining_count)]
        pc = 0

        while pc < len(instructions):
            instr = instructions[pc]
            op    = instr[0]

            # ── SET ───────────────────────────────────────────────────────
            if op == "SET":
                symbols[instr[1]] = resolve(instr[2])
                pc += 1

            # ── CMD ───────────────────────────────────────────────────────
            elif op == "CMD":
                cmd = instr[1]
                val = resolve(instr[2])

                if cmd == "FORWARD":
                    _move(val)
                elif cmd == "BACK":
                    _move(-val)
                elif cmd == "LEFT":
                    state["angle"] -= val
                elif cmd == "RIGHT":
                    state["angle"] += val
                elif cmd == "PENUP":
                    state["pen"] = False
                elif cmd == "PENDOWN":
                    state["pen"] = True
                elif cmd == "COLOR":
                    state["color"] = str(instr[2]) if instr[2] else "black"
                elif cmd == "PENWIDTH":
                    state["width"] = max(1, val)
                elif cmd == "CIRCLE":
                    if state["pen"]:
                        circles.append((
                            state["x"], state["y"],
                            abs(val),
                            state["color"],
                            state["width"],
                        ))
                pc += 1

            # ── REPEAT ────────────────────────────────────────────────────
            elif op == "REPEAT_START":
                count = int(resolve(instr[1]))
                repeat_stack.append([pc, count])
                pc += 1

            elif op == "REPEAT_END":
                if repeat_stack:
                    start, count = repeat_stack[-1]
                    count -= 1
                    if count > 0:
                        repeat_stack[-1][1] = count
                        pc = start + 1      # jump back to first instr after REPEAT_START
                    else:
                        repeat_stack.pop()
                        pc += 1
                else:
                    pc += 1

            # ── PROC_START / PROC_END (skip at runtime, already indexed) ──
            elif op in ("PROC_START", "PROC_END"):
                pc += 1

            # ── CALL ──────────────────────────────────────────────────────
            elif op == "CALL":
                _, proc_name, arg = instr
                if proc_name in procs:
                    param, body = procs[proc_name]
                    local = {}
                    if param and arg is not None:
                        local[param] = resolve(arg)
                    execute(body, local_syms=local)
                pc += 1

            # ── IF / JUMP / LABEL (from IfStmt IR) ────────────────────────
            elif op == "IF_FALSE":
                cond_val = resolve(instr[1])
                if not cond_val:
                    # jump to else label
                    target = instr[2]
                    pc = _find_label(instructions, target) + 1
                else:
                    pc += 1

            elif op == "JUMP":
                target = instr[1]
                pc = _find_label(instructions, target) + 1

            elif op == "LABEL":
                pc += 1

            else:
                pc += 1

        # Restore overridden globals
        if local_syms:
            for k, old_val in saved.items():
                if old_val is None:
                    symbols.pop(k, None)
                else:
                    symbols[k] = old_val

    def _find_label(instructions: list, label: str) -> int:
        for idx, instr in enumerate(instructions):
            if instr[0] == "LABEL" and instr[1] == label:
                return idx
        return len(instructions) - 1

    def _move(distance: float):
        """Move turtle forward (positive) or backward (negative)."""
        rad = math.radians(state["angle"])
        nx  = state["x"] + distance * math.cos(rad)
        ny  = state["y"] + distance * math.sin(rad)
        if state["pen"]:
            lines.append((
                state["x"], state["y"], nx, ny,
                state["color"], state["width"],
            ))
        state["x"] = nx
        state["y"] = ny

    # ── Run the full IR ───────────────────────────────────────────────────────
    execute(ir)

    # ── Compute bounding box for viewBox ──────────────────────────────────────
    if lines or circles:
        all_x = [x1 for x1, y1, x2, y2, *_ in lines] + \
                [x2 for x1, y1, x2, y2, *_ in lines] + \
                [cx for cx, cy, r, *_ in circles]
        all_y = [y1 for x1, y1, x2, y2, *_ in lines] + \
                [y2 for x1, y1, x2, y2, *_ in lines] + \
                [cy for cx, cy, r, *_ in circles]
        pad  = 20
        minx = min(all_x) - pad
        miny = min(all_y) - pad
        maxx = max(all_x) + pad
        maxy = max(all_y) + pad
        vw, vh = maxx - minx, maxy - miny
        viewbox = f"{minx:.2f} {miny:.2f} {vw:.2f} {vh:.2f}"
    else:
        viewbox = f"0 0 {CANVAS_W} {CANVAS_H}"

    # ── Write SVG ─────────────────────────────────────────────────────────────
    with open(output_file, "w") as f:
        f.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{viewbox}" '
            f'width="{CANVAS_W}" height="{CANVAS_H}">\n'
        )
        f.write(f'  <rect width="100%" height="100%" fill="white"/>\n')

        for x1, y1, x2, y2, color, width in lines:
            f.write(
                f'  <line x1="{x1:.4f}" y1="{y1:.4f}" '
                f'x2="{x2:.4f}" y2="{y2:.4f}" '
                f'stroke="{color}" stroke-width="{width}" '
                f'stroke-linecap="round"/>\n'
            )

        for cx, cy, r, color, width in circles:
            f.write(
                f'  <circle cx="{cx:.4f}" cy="{cy:.4f}" r="{r:.4f}" '
                f'fill="none" stroke="{color}" stroke-width="{width}"/>\n'
            )

        f.write('</svg>\n')