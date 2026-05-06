KEYWORDS = {
    "FORWARD", "BACK", "LEFT", "RIGHT",
    "PENUP", "PENDOWN", "SET",
    "REPEAT", "PROC", "CALL",
    "END", "COLOR", "PENWIDTH"
}

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

def lexer(code):
    tokens = []
    words = code.replace("\n", " \n ").split()

    for word in words:
        if word in KEYWORDS:
            tokens.append(Token("KEYWORD", word))
        elif word.isdigit():
            tokens.append(Token("NUMBER", int(word)))
        elif word == "\n":
            tokens.append(Token("NEWLINE", word))
        else:
            tokens.append(Token("IDENT", word))

    return tokens