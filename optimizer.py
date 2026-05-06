def optimize_ir(ir):
    optimized = []
    i = 0

    while i < len(ir):
        instr = ir[i]

        # REMOVE useless MOVE 0
        if instr[0] == "CMD" and instr[2] == 0:
            i += 1
            continue

        # MERGE consecutive MOVE
        if (
            i + 1 < len(ir)
            and instr[0] == "CMD"
            and ir[i+1][0] == "CMD"
            and instr[1] == "FORWARD"
            and ir[i+1][1] == "FORWARD"
        ):
            merged = instr[2] + ir[i+1][2]
            optimized.append(("CMD", "FORWARD", merged))
            i += 2
            continue

        optimized.append(instr)
        i += 1

    return optimized