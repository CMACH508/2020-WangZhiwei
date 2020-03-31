class HexColor:
    def __init__(self, string):
        self.m_string = string
    
    # opposite color
    def setOtherColor(self, color):
        self.m_otherColor = color
    
    def toString(self):
        return self.m_string

    def otherColor(self):
        return self.m_otherColor

BLACK = HexColor("black")
WHITE = HexColor("white")
EMPTY = HexColor("empty")
BLACK.setOtherColor(WHITE)
WHITE.setOtherColor(BLACK)
EMPTY.setOtherColor(EMPTY)

def get(name):
    if name == "black": return BLACK
    if name == "white": return WHITE
    if name == "empty": return EMPTY
    return None