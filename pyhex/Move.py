class Move:
    '''
    Move.
    Contains a HexPoint and a HexColor.  To construct a swap moves or
    other special moves use the appropriate HexPoint.  Immutable.
    '''
    def __init__(self,p,c):
        """ 
        Constructs a move with the given point and color.
        @param p location of move
        @param c black or white. 
        """
        self.m_point = p
        self.m_color = c
    
    def __eq__(self, other):
        if (type(other) == Move):
            return self.m_point == other.getPoint() and self.m_color == other.getColor()

    def getPoint(self):
        # Returns the point of this move.
        return self.m_point

    def getColor(self):
        return self.m_color