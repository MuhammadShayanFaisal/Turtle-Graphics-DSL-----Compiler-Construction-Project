MOVEMENT_CMDS = {"FORWARD", "BACK", "LEFT", "RIGHT"}


def optimize_ir(ir: list) -> list:
    ir = _pass_constant_propagation(ir)
    ir = _pass_dead_code(ir)
    ir = _pass_peephole_merge(ir)
    return ir


def _pass_constant_propagation(ir: list) -> list:
    known: dict = {}   
    out = []

    for instr in ir:
        op = instr[0]

        if op == "SET":
            _, var, val = instr
            if isinstance(val, (int, float)):
                known[var] = val       
            elif val in known:
                val = known[val]        
                known[var] = val
            else:
                known.pop(var, None)
            out.append(("SET", var, val))

        elif op == "CMD":
            _, cmd, val = instr
            if isinstance(val, str) and val in known:
                val = known[val]       
            out.append(("CMD", cmd, val))

        else:
            out.append(instr)

    return out

def _pass_dead_code(ir: list) -> list:
    out = []
    for instr in ir:
        op = instr[0]
        if op == "CMD":
            _, cmd, val = instr
            if cmd in MOVEMENT_CMDS and val == 0:
                continue                
        out.append(instr)
    return out

def _pass_peephole_merge(ir: list) -> list:
    """
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