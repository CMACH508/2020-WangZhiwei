import HexColor
import HexPoint
import Move

class Node:
    def __init__(self, move = None):
        self.m_property = {}
        self.m_setup_black = []
        self.m_setup_white = []
        self.m_setup_empty = []
        self.m_label = []
        self.setMove(move)

        self.m_parent = None
        self.m_prev = None
        self.m_next = None
        self.m_child = None

    def setMove(self, move):
        self.m_move = move

    def getMove(self):
        return self.m_move

    def hasMove(self):
        return self.m_move != None

    
    def setParent(self, parent):
        self.m_parent = parent

    def getParent(self):
        return self.m_parent


    def setPrev(self, prev):
        self.m_prev = prev

    def getPrev(self):
        return self.m_prev


    def setNext(self, next):
        self.m_next = next

    def getNext(self):
        return self.m_next


    def setFirstChild(self,child):
        '''
        Sets the first child of this node. 
        This does not update the sibling pointers of the child.
        '''
        self.m_child = child

    def removeSelf(self):
        '''
        Removes this node from the gametree.
        '''
        Prev = self.getPrev()
        Next = self.getNext()

        if Prev == None:
            if self.getParent() != None:
                self.getParent().setFirstChild(Next)
        else:
            Prev.setNext(Next)

        if Next != None:
            Next.setPrev(Prev)

    def addChild(self, child):
        '''
        Adds a child to the end of the list of children. 
        @param child Node to be added to end of list.
        '''
        child.setNext(None)
        child.setParent(self)

        if self.m_child == None:
            self.m_child = child
            child.setPrev(None)
        else:
            curnode = self.m_child
            while curnode.getNext() != None:
                curnode = curnode.getNext()
            curnode.setNext(child)
            child.setPrev(curnode)

    def numChildren(self):
        '''
        Returns the number of children of this node.
        '''
        num = 0
        curnode = self.m_child
        while curnode != None:
            num += 1
            curnode = curnode.getNext()

        return num

    def getChild(self, n = 0):
        '''
        Returns the nth child. 
	    @param n The number of the child to return. 
	    @return  The nth child or <code>None</code> that child does not exist.
        '''
        curnode = self.m_child
        i = 0
        while curnode != None:
            if i == n:
                return curnode
            curnode = curnode.getNext()
            i += 1
        return None

    def getChildContainingNode(self, node):
        '''
        Returns the child that contains <code>node</code> in its subtree.
        '''
        for i in range(self.numChildren()):
            c = self.getChild(i)
            if c == node: return c
        
        for i in range(self.numChildren()):
            c = self.getChild(i)
            if(c.getChildContainingNode(node) != None):
                return c
        
        return None

    def getDepth(self):
        '''
        Returns the depth of this node.
        '''
        depth = 0
        curnode = self
        while True:
            parent = curnode.getParent()
            if parent == None: break
            curnode = parent
            depth += 1

        return depth

    def isSwapAllowed(self):
        '''
        Determines if a swap move is allowed at this node.
        Returns <code>true</code> if we are on move #2.
        '''
        if self.getDepth() == 1:
            return True
        return False

    # -------------------------------------------------------------

    def setSgfProperty(self, key, value):
        '''
        Adds a property to this node. 
        Node properties are <code>(key, value)</code> pairs of strings.
        These properties will stored if the gametree is saved in SGF format.
        @param key name of the property
        @param value value of the property
        '''
        self.m_property[key] = value

    def appendSgfProperty(self, key, toadd):
        old = self.m_property.get(key,"")
        self.m_property[key] = old + toadd

    def getSgfProperty(self, key):
        '''
        Returns the value of a property. 
        @param key name of property
        @return value of <code>key</code> or <code>None</code> if key is
        not in the property list.
        '''
        return self.m_property.get(key)

    def getProperties(self):
        '''
        Returns a dict of the current set of properties.
	    @return dict containing the properties
        '''
        return self.m_property

    def setComment(self, comment):
        '''
        Sets the SGF Comment field of this node.
        '''
        self.setSgfProperty("C", comment)

    def getComment(self):
        return self.getSgfProperty("C")

    def hasCount(self):
        return self.getSgfProperty("CN") != None

    def getCount(self):
        return self.getSgfProperty("CN")

    
    def addSetup(self, color, point):
        '''
        Adds a stone of specified color to the setup list and the sgf
        property string.
        '''
        if color == HexColor.BLACK:
            if point not in self.m_setup_black:
                self.m_setup_black.append(point)
        elif color == HexColor.WHITE:
            if point not in self.m_setup_white:
                self.m_setup_white.append(point)
        elif color == HexColor.EMPTY:
            if point not in self.m_setup_empty:
                self.m_setup_empty.append(point)
        
    def removeSetup(self, color, point):
        try:
            if color == HexColor.BLACK:
                self.m_setup_black.remove(point)
            elif color == HexColor.WHITE:
                self.m_setup_white.remove(point)
            elif color == HexColor.EMPTY:
                self.m_setup_empty.remove(point)
        except ValueError:
            print("setup not exist")

    def getSetup(self, color):
        if color == HexColor.BLACK:
            return self.m_setup_black
        if color == HexColor.WHITE:
            return self.m_setup_white
        if color == HexColor.EMPTY:
            return self.m_setup_empty
        return None

    def hasSetup(self):
        return ((len(self.m_setup_black) > 0) or 
                (len(self.m_setup_white) > 0) or 
                (len(self.m_setup_empty) > 0))
        
    
    def hasLabel(self):
        return len(self.m_label) > 0

    def getLabels(self):
        return self.m_label

    def addLabel(self, toaddstr):
        self.m_label.append(toaddstr)

    def setPlayerToMove(self, color):
        '''
        Sets the PL proprety to the given color.
        '''
        if color == HexColor.BLACK:
            self.setSgfProperty("PL", "B")
        else:
            self.setSgfProperty("PL", "W")

    def getPlayerToMove(self):
        '''
        Returns the color in the "PL" property, null otherwise.
        '''
        cstr = self.getSgfProperty("PL")
        if cstr != None:
            if cstr == "B":
                return HexColor.BLACK
            if cstr == "W":
                return HexColor.WHITE
        return None

if __name__ == "__main__":
    a = Node()
    b = Node()
    c = Node()
    d = Node()
    a.setFirstChild(b)
    b.setParent(a)
    b.setNext(c)
    c.setParent(a)
    c.setPrev(b)
    c.setFirstChild(d)
    d.setParent(c)
    print(a.numChildren(),a.getChild(),a.getChild(1))
    print(c.numChildren(),c.getChild())
    print(a.getChildContainingNode(d))
    print(c.getChildContainingNode(d))
