import sys,os

#sys.path.append('pyhex')
import SgfReader

NoneMoveList = ['invalid',  'swap-pieces', 'north', 'east', 'south', 'west']
passlist = []
unpasslist = []
errorlist = []
for name in os.listdir('all13x13'):
    try:
        #print(name)
        f = open('all13x13/'+name, 'r')
        reader = SgfReader.SgfReader(f,False)
        root = reader.getGameTree()
        root = root.m_child
        while root:
            if root.m_move.m_point.m_string in NoneMoveList:
                errorlist.append(name + root.m_move.m_point.m_string)
            else:
                print(name)
                print(root.m_move_m_point.m_string)
            root = root.m_child
        passlist.append(name)
    except:
        unpasslist.append(name)
print(len(passlist))
#print(unpasslist)
print(errorlist)
