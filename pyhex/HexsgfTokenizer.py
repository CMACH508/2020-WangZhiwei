class HexsgfTokenizer:
    def __init__(self, instream = None):
        '''
        instream: a file stream
        self.curToken: current token to be returned
        self.sval: current string value if self.curToke == TT_WORD
        '''
        self.f = instream
        self.curToken = None
        self.sval = ''
        self.pushBackVal = None

        self.__tokenList = ['[', ']', '(', ')', ';']
    
    def nextToken(self):
        '''
        return the next token or TT_WORD ignore \\n and \\r
        user can take the string value by self.sval if it returns TT_WORD
        '''           
        if self.f == None: return None

        if self.pushBackVal != None:
            ret = self.pushBackVal
            self.pushBackVal = None
            return ret

        self.sval = ''
        while True:
            char = self.f.read(1)
            if char in self.__tokenList:
                if self.sval == '':
                    self.curToken = char
                    return self.curToken
                else:
                    self.curToken = TT_WORD
                    self.f.seek(self.f.tell() - 1)
                    return self.curToken
            elif char == '\n' or char == '\r':
                if self.sval == '':
                    continue
                else:
                    self.sval += char
            elif char == '': #EOF
                if self.sval == '':
                    self.curToken = TT_EOF
                    return self.curToken
                else:
                    self.curToken = TT_WORD
                    return self.curToken
            else:
                self.sval += char

    def pushBack(self):
        '''
        let the call to the nextToken return the same value as the last time,
        not change the sval value.
        used in some trick in sgfreader.
        '''
        self.pushBackVal = self.curToken

class Ttype:
    '''
    two special token type
    '''
    def __init__(self,typename):
        self.typename = typename

TT_WORD = Ttype('word')
TT_EOF = Ttype('EOF')

if __name__ == "__main__":
    f = open('sgf/0001.sgf','r',encoding='utf-8')
    testTokenizer = HexsgfTokenizer(f)
    for i in range(20):
        print(testTokenizer.nextToken(),testTokenizer.sval)
    f.close()