import HexColor
import HexPoint
import Move
import Node
import GameInfo
import HexsgfTokenizer

class SgfReader():

    class SgfError(Exception):
        def __init__(self, message):
            Exception.__init__(self, message)

    __GM_HEXGAME = 11

    def __init__(self, instream):
        '''
        Constructor. 
	    Parse the input stream in sgf format.
        '''
        self.m_tokenizer = HexsgfTokenizer.HexsgfTokenizer(instream)
        self.m_gameinfo = GameInfo.GameInfo()
        self.m_warnings = []
        try:
            self.findGameTree()
            self.m_gametree = self.parseGameTree(None, True)
            print('gametree reading done')
        except IOError:
            raise self.SgfError("IO error occured while parsing file.")
    
    def getGameTree(self):
        return self.m_gametree

    def getGameInfo(self):
        return self.m_gameinfo

    def getWarnings(self):
        if len(self.m_warnings) == 0:
            return None
        return self.m_warnings

    # -----------------------------------------------------------------

    def findGameTree(self):
        while True:
            ttype = self.m_tokenizer.nextToken()
            if ttype == HexsgfTokenizer.TT_EOF:
                raise self.SgfError("No game tree found!")
            
            if (ttype == '('):
                self.m_tokenizer.pushBack()
                break
            
    def parseGameTree(self, parent, isroot):
        '''
        parent: Node
        isroot: bool
        '''
        ttype = self.m_tokenizer.nextToken()
        if ttype != '(':
            raise self.SgfError("Missing '(' at head of game tree.")
        
        node = self.parseNode(parent, isroot)

        ttype = self.m_tokenizer.nextToken()
        if ttype != ')':
            raise self.SgfError("Game tree not closed!")
        
        return node

    def parseNode(self, parent, isroot):
        '''
        parent: Node
        isroot: bool
        '''
        ttype = self.m_tokenizer.nextToken()
        if ttype != ';':
            raise self.SgfError("Error at head of node!")
        
        node = Node.Node()
        node.setParent(parent)
        if parent != None:
            parent.addChild(node)

        done = False
        while not done:
            ttype = self.m_tokenizer.nextToken()
            if ttype == '(':
                self.m_tokenizer.pushBack()
                self.parseGameTree(node, False)
            elif ttype == ';':
                self.m_tokenizer.pushBack()
                self.parseNode(node, False)
                done = True
            elif ttype == ')':
                self.m_tokenizer.pushBack()
                done = True
            elif ttype == HexsgfTokenizer.TT_WORD:
                self.parseProperty(node, isroot)
            elif ttype == HexsgfTokenizer.TT_EOF:
                raise self.SgfError("Unexpected EOF in node!")
            else:
                raise self.SgfError("Error in SGF file.")
        
        return node
    
    def parseProperty(self, node, isroot):
        '''
        parse contents in one node
        '''
        name = self.m_tokenizer.sval

        done = False
        while not done:
            ttype = self.m_tokenizer.nextToken()
            if ttype != '[':
                done = True
            self.m_tokenizer.pushBack()
            if done: break
            
            if name == 'C':
                val = self.parseComment()
            else:
                val = self.parseValue()
            # print(name + '[' + val + ']')

            if name == 'W':
                point = HexPoint.get(val)
                node.setMove(Move.Move(point, HexColor.WHITE))
            elif name == 'B':
                point = HexPoint.get(val)
                node.setMove(Move.Move(point, HexColor.BLACK))
            elif name == 'AB':
                node.addSetup(HexColor.BLACK, HexPoint.get(val))
            elif name == 'AW':
                node.addSetup(HexColor.WHITE, HexPoint.get(val))
            elif name == 'AE':
                node.addSetup(HexColor.EMPTY, HexPoint.get(val))
            elif name == 'LB':
                node.addLabel(val)
            elif name == 'FF':
                node.setSgfProperty(name, val)
                x = self.parseInt(val)
                if x < 1 or x > 4:
                    raise self.SgfError("Invalid SGF Version! (" + x + ")")
            elif name == 'GM':
                node.setSgfProperty(name, val)
                if not isroot:
                    self.sgfWarning("GM property in non-root node!")
                if self.parseInt(val) != self.__GM_HEXGAME:
                    raise self.SgfError("Not a Hex game!")
            elif name == 'SZ':
                node.setSgfProperty(name, val)
                if not isroot: self.sgfWarning("GM property in non-root node!")
                sp = val.split(':')
                if len(sp) == 1:
                    x = self.parseInt(sp[0])
                    self.m_gameinfo.setBoardSize(x,x)
                elif len(sp) == 2:
                    x = self.parseInt(sp[0])
                    y = self.parseInt(sp[1])
                    self.m_gameinfo.setBoardSize(x,y)
                else:
                    raise self.SgfError("Malformed boardsize!")
            else:
                node.setSgfProperty(name, val)
            
    def parseValue(self):
        '''
        parse value in []
        '''
        ttype = self.m_tokenizer.nextToken()
        if ttype != '[':
            raise self.SgfError("Property missing opening '['.")

        sb = ''
        quoted = False
        while True:
            c = self.m_tokenizer.f.read(1)
            if c == '':
                raise self.SgfError("Property runs to EOF.")
            
            if not quoted:
                if c == ']': break
                if c == '\\':
                    quoted = True
                else:
                    if c != '\r' and c != '\n':
                        sb += c
            else:
                quoted = True
                sb += c
        return sb

    def parseComment(self):
        '''
        parse comment in C[]
        '''
        ttype = self.m_tokenizer.nextToken()
        if ttype != '[':
            raise self.SgfError("Comment missing opening '['.")
        
        sb = ''
        quoted = False
        while True:
            c = self.m_tokenizer.f.read(1)
            if c == '':
                raise self.SgfError("Comment runs to EOF.")
            
            if not quoted:
                if c == ']': break

                if c == '\\':
                    quoted = True
                else:
                    sb += c
            else:
                quoted = False
                sb += c
        return sb

    def parseInt(self, string):
        '''
        parse string to integer
        '''
        try:
            ret = int(string)
        except ValueError:
            raise self.SgfError("Error parsing integer.")
        return ret
        
    def verifyGame(self, root):
        if self.m_gameinfo.getBoardSize() == (None,None):
            raise self.SgfError("Missing SZ property.")
    
    def sgfWarning(self, msg):
        self.m_warnings.append(msg)



if __name__ == "__main__":
    f = open('0001.sgf','r')
    SgfReaderTest = SgfReader(f)
    print(SgfReaderTest.m_gametree.m_child.m_move.m_point.m_string)