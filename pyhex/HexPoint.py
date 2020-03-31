class HexPoint:
    MAX_WIDTH = 19
    MAX_HEIGHT = 19
    MAX_POINTS = MAX_WIDTH * MAX_HEIGHT + 7

    def __init__(self, *args):
        if len(args) == 2:
            p, name = args
            self.x = p & (self.MAX_WIDTH-1)
            self.y = p // self.MAX_WIDTH
            self.m_string = name
        elif len(args) == 3:
            x, y, name = args
            self.x = x
            self.y = y
            self.m_string = name
    
    def __lt__(self, other):
        if (type(other) == HexPoint):
            if(self.x == other.x):
                return self.y < other.y
            return self.x < other.x
        return False

    def __eq__(self, other):
        if (type(other) == HexPoint):
            return self.x == other.x and self.y == other.y
        return False
    
    def toString(self):
        return self.m_string
        
s_points = [i for i in range(HexPoint.MAX_POINTS)]
INVALID = s_points[0] = HexPoint(0,"invalid")
RESIGN = s_points[1] = HexPoint(1,"resign")
SWAP_PIECES = s_points[2] = HexPoint(2,"swap-pieces")

NORTH = s_points[3] = HexPoint(3,"north")
EAST = s_points[4] = HexPoint(4,"east")
SOUTH = s_points[5] = HexPoint(5,"south")
WEST = s_points[6] = HexPoint(6,"west")

for y in range(HexPoint.MAX_HEIGHT):
    for x in range(HexPoint.MAX_WIDTH):
        name = chr(ord('a') + x) + str(y+1)
        s_points[7 + y*HexPoint.MAX_WIDTH + x] = HexPoint(x,y,name)

def get(*arg):
    if len(arg) == 1:
        i = arg[0]

        # Returns the point with the given index.
        # @param i index of the point. 
        # @return point with index i.
        if type(i) == int:
            assert i >= 0
            assert i < HexPoint.MAX_POINTS
            return s_points[i]

        # Returns the point with the given string represention.
        # Valid special moves include: "north", "south", "east", "west" 
        # "swap-sides", "swap-pieces", "resign", and "forfeit".
        if type(i) == str:
            if i.lower() == 'swap':
                return SWAP_PIECES
            for x in range(HexPoint.MAX_POINTS):
                if i.lower() == s_points[x].toString().lower():
                    return s_points[x]
            print(i)
            assert False
            return None

    # Returns the point with the given coordinates.  Note that it is
	# not possible to obtain points for board edges and special
	# moves with this method.  Use the <code>get(String)</code>
	# method for these types of points.
    if len(arg) == 2:
        x, y = arg
        assert x >= 0
        assert y >= 0
        assert x < HexPoint.MAX_WIDTH
        assert y < HexPoint.MAX_HEIGHT
        return s_points[7 + y*HexPoint.MAX_WIDTH + x]

if __name__ == "__main__":
    for i in range(10):
        print(s_points[i].x, s_points[i].y, s_points[i].toString())