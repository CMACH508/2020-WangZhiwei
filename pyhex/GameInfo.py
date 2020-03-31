class GameInfo:
    '''
    Properties of a game.
    Holds properties that appear in a SGF root node.
    '''
    def __init__(self, width = None, height = None):
        self.width = width
        self.height = height

    def setBoardSize(self, width, height):
        self.width = width
        self.height = height
    
    def getBoardSize(self):
        return self.width, self.height