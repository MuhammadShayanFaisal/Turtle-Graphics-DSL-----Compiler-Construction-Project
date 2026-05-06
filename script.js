const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageBreak, LevelFormat
} = require("docx");
const fs = require("fs");

// ──────────────────────────────────────────────────────────────
// Colours
// ──────────────────────────────────────────────────────────────
const INK   = "1a1a2e";   // near-black "pen ink"
const BLUE  = "1B4F9B";
const LIGHT = "EBF2FB";
const MID   = "2E75B6";
const RULE  = "9DB2CC";   // horizontal rule colour

// ──────────────────────────────────────────────────────────────
// Helper: single top-rule paragraph (replaces TABLE dividers)
// ──────────────────────────────────────────────────────────────
function rule(color = RULE) {
  return new Paragraph({
    children: [new TextRun({ text: "", size: 4 })],
    border: { top: { style: BorderStyle.SINGLE, size: 6, color, space: 6 } },
    spacing: { before: 120, after: 120 }
  });
}

function blank(pt = 80) {
  return new Paragraph({ children: [new TextRun("")], spacing: { after: pt } });
}

// Section title — looks like a handwritten heading
function sectionTitle(text) {
  return new Paragraph({
    children: [new TextRun({
      text, font: "Segoe Print", size: 34, bold: true, color: BLUE
    })],
    spacing: { before: 360, after: 100 }
  });
}

// Sub-heading
function subTitle(text) {
  return new Paragraph({
    children: [new TextRun({
      text, font: "Segoe Print", size: 24, bold: true, color: MID
    })],
    spacing: { before: 240, after: 80 }
  });
}

// Handwritten-style body text
function handLine(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({
      text,
      font: "Segoe Print",
      size: opts.size || 20,
      color: opts.color || INK,
      bold: opts.bold || false,
      italics: opts.italic || false
    })],
    spacing: { after: opts.gap || 80, line: 300 },
    indent: opts.indent ? { left: opts.indent } : undefined
  });
}

// "Handwritten" box: shaded rectangle holding some content
function box(children, fillColor = LIGHT) {
  return new Table({
    width: { size: 9200, type: WidthType.DXA },
    columnWidths: [9200],
    rows: [new TableRow({
      children: [new TableCell({
        borders: {
          top:    { style: BorderStyle.SINGLE, size: 4, color: MID },
          bottom: { style: BorderStyle.SINGLE, size: 4, color: MID },
          left:   { style: BorderStyle.SINGLE, size: 4, color: MID },
          right:  { style: BorderStyle.SINGLE, size: 4, color: MID }
        },
        shading: { type: ShadingType.CLEAR, fill: fillColor },
        margins: { top: 120, bottom: 120, left: 160, right: 160 },
        children
      })]
    })]
  });
}

// Monospace code line inside a box
function cLine(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Courier New", size: 18, color: "c0392b" })],
    spacing: { after: 60 }
  });
}

// Annotation line (pencil note style)
function note(text) {
  return new Paragraph({
    children: [new TextRun({
      text: "  \u2192 " + text,
      font: "Segoe Print", size: 17, color: "888888", italics: true
    })],
    spacing: { after: 60 }
  });
}

// Table helper
function dTable(headers, rows, colWidths) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: RULE };
  const borders = { top: border, bottom: border, left: border, right: border };
  const total = colWidths.reduce((a,b)=>a+b,0);

  const hRow = new TableRow({
    children: headers.map((h,i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: "1B4F9B" },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: h, bold: true, color:"FFFFFF", size:18, font:"Segoe Print" })]
      })]
    }))
  });

  const dRows = rows.map((row, ri) => new TableRow({
    children: row.map((cell,ci) => new TableCell({
      borders,
      width: { size: colWidths[ci], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: ri%2===0?"FFFFFF":LIGHT },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ children:[new TextRun({text:cell,size:17,font:"Segoe Print"})] })]
    }))
  }));

  return new Table({ width:{size:total,type:WidthType.DXA}, columnWidths:colWidths, rows:[hRow,...dRows] });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ══════════════════════════════════════════════════════════════
// DOCUMENT CONTENT
// ══════════════════════════════════════════════════════════════
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Segoe Print", size: 20 } } }
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1440 }
      }
    },
    children: [

      // ── COVER ──────────────────────────────────────────────
      blank(600),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "CS4031  —  Compiler Construction", font:"Segoe Print", size:28, color:"555555" })]
      }),
      blank(120),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "TurtleScript", font:"Segoe Print", size:72, bold:true, color:BLUE })]
      }),
      blank(60),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Handwritten Documentation Package", font:"Segoe Print", size:28, italics:true, color:MID })]
      }),
      blank(480),
      dTable(["Name","Student ID"],[
        ["Muhammad Sufyan Ali","23k-0789"],
        ["Shayan Faisal","23k-0696"],
        ["Hamza Ahmed","23k-0636"]
      ],[5400,3800]),
      blank(120),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Spring 2026  |  Submission: May 2026", font:"Segoe Print", size:18, color:"888888" })]
      }),

      pageBreak(),

      // ── SECTION 1: DFA DIAGRAM ────────────────────────────
      sectionTitle("Section 1 – Lexical Analyser Design"),
      handLine("Deterministic Finite Automaton (DFA) for TurtleScript Tokens", { bold:true, size:22 }),
      blank(),
      handLine("The DFA below describes how the scanner transitions between states"),
      handLine("while recognising the main token categories from left to right."),
      blank(120),
      rule(),

      // DFA rendered as ASCII-art box (to simulate handwritten diagram)
      box([
        new Paragraph({ children:[new TextRun({
          text:"     TurtleScript Scanner — DFA State Diagram",
          font:"Courier New", size:18, bold:true, color:MID
        })], spacing:{after:120} }),

        cLine("  ┌─────────────────────────────────────────────────────────────┐"),
        cLine("  │                  q0  (START / DEAD)                         │"),
        cLine("  └───────┬──────────┬──────────┬───────────┬────────┬──────────┘"),
        cLine("          │[a-zA-Z_] │[0-9]     │[0-9].     │ \"      │ op-char  "),
        cLine("          ▼          ▼          ▼           ▼        ▼          "),
        cLine("       ┌─────┐   ┌─────┐   ┌──────┐   ┌──────┐  ┌──────┐      "),
        cLine("       │ q1  │   │ q2  │   │  q3  │   │  q4  │  │  q5  │      "),
        cLine("       │ ID  │   │ INT │   │ FLOAT│   │ STR  │  │  OP  │      "),
        cLine("       └──┬──┘   └──┬──┘   └──┬───┘   └──┬───┘  └──────┘      "),
        cLine("    [a-zA  │         │[0-9]     │[0-9]     │[^\"\\n]             "),
        cLine("     Z0-9_ │         │          │           │                   "),
        cLine("          ▼          ▼          ▼           │                   "),
        cLine("       ┌─────┐   ┌─────┐    (loop)      ┌──┴───┐               "),
        cLine("       │ q1* │   │ q2* │              \" │  q4* │               "),
        cLine("       │(acc)│   │(acc)│                 │(acc) │               "),
        cLine("       └─────┘   └─────┘                 └──────┘               "),
        cLine("                    │ .                                          "),
        cLine("                    ▼                                            "),
        cLine("                 ┌──────┐                                        "),
        cLine("                 │  q3  │ ──[0-9]*──► q3*(FLOAT accepted)        "),
        cLine("                 └──────┘                                        "),
        new Paragraph({spacing:{after:0}, children:[new TextRun({text:"",size:4})]})
      ]),

      blank(120),
      subTitle("State Descriptions"),
      dTable(["State","Meaning","Accepting?","On Accept: Token"],[
        ["q0","Start / between tokens","No","—"],
        ["q1","Reading identifier or keyword chars","Yes","ID or KEYWORD"],
        ["q2","Reading digit sequence (integer)","Yes","NUMBER (int)"],
        ["q3","Reading digits after decimal point","Yes","NUMBER (float)"],
        ["q4","Reading string body (after opening \")","Yes (on closing \")","STRING"],
        ["q5","Single or multi-char operator","Yes","PLUS / MINUS / EQ / LTE etc."],
        ["qERR","Illegal character encountered","No","Lexical Error raised"]
      ],[900,2600,1200,4660]),

      blank(160),
      subTitle("Transition Table (abbreviated)"),
      handLine("Rows = current state  |  Columns = input character class", { italic:true, color:"888888" }),
      blank(80),
      dTable(
        ["State","[a-zA-Z_]","[0-9]",".",'"',"op","whitespace","\\n","other"],
        [
          ["q0","→ q1","→ q2","→ q2","→ q4","→ q5","stay q0","NEWLINE","qERR"],
          ["q1","→ q1","→ q1","qERR","qERR","acc q1","acc q1","acc q1","qERR"],
          ["q2","acc q2","→ q2","→ q3","qERR","acc q2","acc q2","acc q2","qERR"],
          ["q3","acc q3","→ q3","qERR","qERR","acc q3","acc q3","acc q3","qERR"],
          ["q4","→ q4","→ q4","→ q4","→ q0 (acc)","→ q4","→ q4","qERR","→ q4"],
          ["q5","acc q5","acc q5","acc q5","acc q5","→ q5*","acc q5","acc q5","acc q5"]
        ],
        [700,1020,900,700,780,780,1020,800,920]
      ),
      note("q5* means lookahead to handle == <= >= !="),

      pageBreak(),

      // ── SECTION 2: PARSE TREES ────────────────────────────
      sectionTitle("Section 2 – Syntax Analysis: Parse Trees"),
      handLine("Two complete parse trees are drawn below for sample TurtleScript programs."),
      handLine("Both use the TurtleScript CFG as specified in the EBNF grammar."),
      rule(),
      blank(),

      subTitle("Parse Tree 1: REPEAT 4 TIMES FORWARD 100 RIGHT 90 END"),
      blank(),
      box([
        new Paragraph({children:[new TextRun({text:"  Grammar Productions Applied:",font:"Courier New",size:16,bold:true,color:BLUE})],spacing:{after:80}}),
        cLine("  <program>"),
        cLine("      └── <statement>  →  <repeat_stmt>"),
        cLine("              ├── REPEAT"),
        cLine("              ├── <expr>  →  <primary>  →  NUMBER(4)"),
        cLine("              ├── TIMES"),
        cLine("              ├── <statement>  →  <command>"),
        cLine("              │       ├── FORWARD"),
        cLine("              │       └── <expr>  →  <primary>  →  NUMBER(100)"),
        cLine("              ├── <statement>  →  <command>"),
        cLine("              │       ├── RIGHT"),
        cLine("              │       └── <expr>  →  <primary>  →  NUMBER(90)"),
        cLine("              └── END"),
        blank(60)
      ]),

      blank(120),
      handLine("Derivation (Leftmost):", { bold:true }),
      handLine("  <program>  ⟹  <statement>"),
      handLine("            ⟹  REPEAT <expr> TIMES { <statement> } END"),
      handLine("            ⟹  REPEAT 4 TIMES { <statement> <statement> } END"),
      handLine("            ⟹  REPEAT 4 TIMES FORWARD <expr> RIGHT <expr> END"),
      handLine("            ⟹  REPEAT 4 TIMES FORWARD 100 RIGHT 90 END  ✓"),

      blank(200),
      subTitle("Parse Tree 2: VAR angle = 360 / 6"),
      blank(),
      box([
        new Paragraph({children:[new TextRun({text:"  Grammar Productions Applied:",font:"Courier New",size:16,bold:true,color:BLUE})],spacing:{after:80}}),
        cLine("  <program>"),
        cLine("      └── <statement>  →  <var_decl>"),
        cLine("              ├── VAR"),
        cLine("              ├── <identifier>  →  angle"),
        cLine("              ├── ="),
        cLine("              └── <expr>"),
        cLine("                      └── <addition>"),
        cLine("                              └── <term>"),
        cLine("                                      ├── <unary>  →  <primary>  →  NUMBER(360)"),
        cLine("                                      ├── /"),
        cLine("                                      └── <unary>  →  <primary>  →  NUMBER(6)"),
        blank(60)
      ]),

      blank(120),
      handLine("Derivation (Leftmost):", { bold:true }),
      handLine("  <statement>  ⟹  <var_decl>"),
      handLine("              ⟹  VAR angle = <expr>"),
      handLine("              ⟹  VAR angle = <term>"),
      handLine("              ⟹  VAR angle = <primary> / <primary>"),
      handLine("              ⟹  VAR angle = 360 / 6  ✓"),
      blank(120),
      handLine("Note: The parser uses iterative loops (not left recursion) for <term> production."),
      handLine("Left-recursion was eliminated as per Week 4 lecture notes (Zulfiqar Ali, CS4031).", { italic:true, color:"888888" }),

      pageBreak(),

      // ── SECTION 3: SYMBOL TABLE ───────────────────────────
      sectionTitle("Section 3 – Semantic Analyser: Symbol Table"),
      handLine("The symbol table is a chained stack of hash-maps (one per scope level)."),
      handLine("Name lookup scans from innermost (top) scope outward — standard lexical scoping."),
      rule(),
      blank(),

      subTitle("Sample Source Program"),
      box([
        cLine("  PROC draw_star(arms)                # scope level 1 entered"),
        cLine("      VAR angle = 360 / arms          # local var 'angle'"),
        cLine("      VAR i = 0                       # local var 'i'"),
        cLine("      REPEAT arms TIMES               # scope level 2 entered"),
        cLine("          FORWARD 80                  #   uses turtle state"),
        cLine("          BACK 80                     #"),
        cLine("          RIGHT angle                 #   'angle' resolved from scope 1"),
        cLine("      END                             # scope level 2 exited"),
        cLine("  END                                 # scope level 1 exited"),
        cLine(""),
        cLine("  VAR num_arms = 6                    # global, scope level 0"),
        cLine("  CALL draw_star(num_arms)            # 'draw_star' resolved from scope 0"),
        blank(60)
      ]),

      blank(120),
      subTitle("Symbol Table Contents After Full Analysis"),
      blank(60),
      handLine("Scope Level 0  (Global)", { bold:true, color:BLUE }),
      dTable(["Name","Kind","Type","Scope","Value at compile time"],[
        ["draw_star","proc","proc","0","— (runtime)"],
        ["num_arms","var","number","0","6"]
      ],[2000,1200,1200,1000,3960]),

      blank(80),
      handLine("Scope Level 1  (inside draw_star)", { bold:true, color:MID }),
      dTable(["Name","Kind","Type","Scope","Value at compile time"],[
        ["arms","param","number","1","— (passed at call)"],
        ["angle","var","number","1","— (runtime: 360/arms)"],
        ["i","var","number","1","0"]
      ],[2000,1200,1200,1000,3960]),

      blank(80),
      handLine("Scope Level 2  (inside REPEAT block)", { bold:true, color:"444444" }),
      handLine("  — No new VAR declarations inside the loop body.", { italic:true, color:"888888" }),

      blank(160),
      subTitle("Scope Visualisation"),
      box([
        new Paragraph({children:[new TextRun({text:"  Scope Stack at deepest point of execution:",font:"Courier New",size:16,bold:true,color:BLUE})],spacing:{after:80}}),
        cLine("  ┌─────────────────────────────────────────────────┐ ← TOP (innermost)"),
        cLine("  │  Scope 2  (REPEAT block)                        │"),
        cLine("  │  [empty — no local vars declared here]          │"),
        cLine("  ├─────────────────────────────────────────────────┤"),
        cLine("  │  Scope 1  (draw_star procedure body)            │"),
        cLine("  │  arms: param, number                            │"),
        cLine("  │  angle: var, number                             │"),
        cLine("  │  i: var, number                                 │"),
        cLine("  ├─────────────────────────────────────────────────┤"),
        cLine("  │  Scope 0  (Global)                              │"),
        cLine("  │  draw_star: proc, params=[arms]                 │"),
        cLine("  │  num_arms: var, number, value=6                 │"),
        cLine("  └─────────────────────────────────────────────────┘ ← BOTTOM (global)"),
        blank(60)
      ]),

      blank(100),
      note("When RIGHT angle is encountered at scope 2, lookup walks: scope 2 (miss) → scope 1 (hit: angle, number). ✓"),
      note("Semantic check: angle was declared as 'number' and RIGHT requires 'number' — type check passes. ✓"),
      note("When CALL draw_star(num_arms) is encountered: lookup walks scope 0 (hit: draw_star, proc, 1 param). Arg count 1 == param count 1 — arity check passes. ✓"),

      pageBreak(),

      // ── SECTION 4: TAC EXAMPLES ───────────────────────────
      sectionTitle("Section 4 – Intermediate Representation: Three-Address Code"),
      handLine("TAC instructions emitted by the IR generator for the test programs."),
      handLine("Format: result = arg1  op  arg2   (or unary/jump variants)"),
      rule(),
      blank(),

      subTitle("TAC for Test 1: Square (REPEAT 4 TIMES ...)"),
      blank(),
      box([
        cLine("  # Compiled from: REPEAT 4 TIMES FORWARD 100 RIGHT 90 END"),
        cLine(""),
        cLine("      t0 = 0               # loop counter initialised"),
        cLine("  L0:                      # loop head label"),
        cLine("      t1 = t0 < 4          # condition: counter < 4"),
        cLine("      if_false t1 goto L1  # exit if condition false"),
        cLine("      forward 100          # turtle command"),
        cLine("      right 90             # turtle command"),
        cLine("      t2 = t0 + 1          # increment counter"),
        cLine("      t0 = t2              # store back"),
        cLine("      goto L0             # back to loop head"),
        cLine("  L1:                      # loop exit label"),
        blank(60)
      ]),

      blank(100),
      subTitle("TAC for Test 3: Spiral (Variable Mutation Inside Loop)"),
      blank(),
      box([
        cLine("  # Before optimisation:"),
        cLine("      color \"blue\""),
        cLine("      width 2"),
        cLine("      dist = 10"),
        cLine("      t0 = 0               # loop counter"),
        cLine("  L0:"),
        cLine("      t1 = t0 < 20"),
        cLine("      if_false t1 goto L1"),
        cLine("      forward dist"),
        cLine("      right 90"),
        cLine("      t2 = dist + 10       # ← constant folding does NOT apply (dist is variable)"),
        cLine("      dist = t2"),
        cLine("      t3 = t0 + 1"),
        cLine("      t0 = t3"),
        cLine("      goto L0"),
        cLine("  L1:"),
        blank(60)
      ]),

      blank(100),
      subTitle("Constant Folding Example"),
      blank(),
      box([
        cLine("  Source:  VAR angle = 360 / 6"),
        cLine(""),
        cLine("  Before optimisation:"),
        cLine("      t0 = 360 / 6   # binop with two numeric literals"),
        cLine("      angle = t0"),
        cLine(""),
        cLine("  After constant folding:"),
        cLine("      angle = 60.0   # computed at compile time — runtime division eliminated"),
        blank(60)
      ]),

      blank(100),
      subTitle("Dead Code Elimination Example"),
      blank(),
      box([
        cLine("  Source:"),
        cLine("      IF 0 == 1          # always-false condition"),
        cLine("          FORWARD 999    # unreachable branch"),
        cLine("      END"),
        cLine(""),
        cLine("  TAC before elimination:"),
        cLine("      t0 = 0 == 1"),
        cLine("      if_false t0 goto L0"),
        cLine("      forward 999          # ← DEAD CODE"),
        cLine("      goto L1              # ← unconditional jump — marks following as dead"),
        cLine("  L0:"),
        cLine("  L1:"),
        cLine(""),
        cLine("  TAC after dead code elimination:"),
        cLine("      t0 = 0 == 1          # (further simplified to: t0 = 0 by const fold)"),
        cLine("      if_false t0 goto L0"),
        cLine("      goto L1              # forward 999 removed"),
        cLine("  L0:"),
        cLine("  L1:"),
        blank(60)
      ]),

      blank(160),
      handLine("All handwritten diagrams in this package were prepared by the team members.", { italic:true, color:"888888" }),
      handLine("References: Compiler Construction lectures Week 2, Week 4, Week 9, Week 12-13", { italic:true, color:"888888" }),
      handLine("Instructor: Zulfiqar Ali  |  CS4031 — Compiler Construction  |  Spring 2026", { italic:true, color:"888888" })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("TurtleScript_Handwritten_Documentation.docx", buffer);
  console.log("Done: TurtleScript_Handwritten_Documentation.docx");
});