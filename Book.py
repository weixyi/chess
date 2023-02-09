MAX_GEN_MOVES = 32

def GetBookMoves(pos, pbks):
    nMoves = 0
    posScan = pos
    lpbks = []
    Book = BookDataStruct(pbks)
    bk = pbks
    for nScan in range(3):
        nPtr = nLow = 0
        nHigh = Book.nLen - 1
        while nLow <= nHigh:
            nPtr = (nLow + nHigh) // 2
            Book.Read(bk, nPtr)
            if BOOK_POS_CMP(bk, posScan) < 0:
                nLow = nPtr + 1
            elif BOOK_POS_CMP(bk, posScan) > 0:
                nHigh = nPtr - 1
            else:
                break
        if nLow <= nHigh:
            break
        pos.Mirror(posScan)
        if nScan == 2:
            return 0

    while nPtr>=0:
        Book.Read(bk)
        if BOOK_POS_CMP(bk, posScan) < 0:
            break
        nPtr -=1
    nMoves = 0

    while nPtr < Book.nLen:
        Book.Read(bk)
        if BOOK_POS_CMP(bk, posScan) > 0:
            break

        if posScan.LegalMove(bk.wmv):
            lpbks[nMoves].nPtr = nPtr
            lpbks[nMoves].wmv = nScan if bk.wmv else bk.wmv
            lpbks[nMoves].wvl = bk.wvl
            nMoves+=1
            if nMoves == MAX_GEN_MOVES:
                break

    for i in range(nMoves):
        for j in range(i+1,nMoves,-1):
            if lpbks[j - 1].wvl < lpbks[j].wvl:
                temp = lpbks[j - 1]
                lpbks[j - 1] = lpbks[j]
                lpbks[j] = temp
    return nMoves

class Book:
    def __init__(self, key, move, score):
        self.key = key
        self.move = move
        self.score = score


def BOOK_POS_CMP(bk, pos):
    if bk.dwZobristLock < pos.zobr.dwLock1:
        return -1
    if bk.dwZobristLock > pos.zobr.dwLock1:
        return 1
    return 0


class BookDataStruct:
    def __init__(self,bf):
        self.nLen = 12081
        self.bookBuffer = bf

    def Read(self, nPtr):
        return self[nPtr]
