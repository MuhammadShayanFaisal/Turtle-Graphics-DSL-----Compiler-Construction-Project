"""
optimizer.py  —  TurtleScript IR Optimiser
Applies three passes over the TAC instruction list:

  Pass 1 — Constant Folding
    Replaces SET instructions whose value is a numeric constant expression
    that was already folded by the parser. Also propagates constants into
    CMD arguments when the variable is a known compile-time constant.

  Pass 2 — Dead Code Elimination
    Removes CMD instructions with a numeric argument of 0
    (e.g. FORWARD 0, BACK 0, LEFT 0, RIGHT 0 have no visible effect).

  Pass 3 — Peephole / Instruction Merging
    Merges consecutive same-direction movement commands
    (FORWARD+FORWARD, BACK+BACK, LEFT+LEFT, RIGHT+RIGHT) into one.
"""

MOVEMENT_CMDS = {"FORWARD", "BACK", "LEFT", "RIGHT"}


def optimize_ir(ir: list) -> list:
    ir = _pass_constant_propagation(ir)
    ir = _pass_dead_code(ir)
    ir = _pass_peephole_merge(ir)
    return ir


# ── Pass 1: constant propagation ─────────────────────────────────────────────

def _pass_constant_propagation(ir: list) -> list:
    """
    Track SET instructions with known numeric values and substitute those
    values into CMD arguments that reference the variable.
    This is true constant propagation (compile-time value substitution).
    """
    known: dict = {}   # var_name → numeric value (only if constant)
    out = []

    for instr in ir:
        op = instr[0]

        if op == "SET":
            _, var, val = instr
            if isinstance(val, (int, float)):
                known[var] = val        # remember for propagation
            elif val in known:
                val = known[val]        # propagate transitively
                known[var] = val
            else:
                # value is a non-constant expression; evict from known
                known.pop(var, None)
            out.append(("SET", var, val))

        elif op == "CMD":
            _, cmd, val = instr
            if isinstance(val, str) and val in known:
                val = known[val]        # substitute constant
            out.append(("CMD", cmd, val))

        else:
            out.append(instr)

    return out


# ── Pass 2: dead code elimination ────────────────────────────────────────────

def _pass_dead_code(ir: list) -> list:
    """Remove movement commands with a zero (or None) argument."""
    out = []
    for instr in ir:
        op = instr[0]
        if op == "CMD":
            _, cmd, val = instr
            if cmd in MOVEMENT_CMDS and val == 0:
                continue                # dead — skip
        out.append(instr)
    return out


# ── Pass 3: peephole / instruction merging ───────────────────────────────────

def _pass_peephole_merge(ir: list) -> list:
    """
    Merge two consecutive same-direction movement commands into one.
    Only merges when both arguments are numeric constants.
    Example:
        FORWARD 40  }
        FORWARD 60  }  →  FORWARD 100
    """
    out = []
    i = 0
    while i < len(ir):
        instr = ir[i]
        if (
            instr[0] == "CMD"
            and instr[1] in MOVEMENT_CMDS
            and isinstance(instr[2], (int, float))
            and i + 1 < len(ir)
            and ir[i + 1][0] == "CMD"
            and ir[i + 1][1] == instr[1]                # same direction
            and isinstance(ir[i + 1][2], (int, float))
        ):
            merged_val = instr[2] + ir[i + 1][2]
            out.append(("CMD", instr[1], merged_val))
            i += 2
        else:
            out.append(instr)
            i += 1
    return out