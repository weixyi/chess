"""
Describe a chess state.
Determine current legal move.
"""

import numpy as np


class GameState:
    def __init__(self):
        # main chess board
        self.board = np.array([["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                               ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"]])
        self.board = np.vstack((self.board, np.full((4, 8), "ES")))
        self.board = np.vstack((self.board, np.array(
            [["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
             ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]])))
        # pawn structure
        self.WPawnKing = np.zeros((8, 8))
        self.WPawnKing[6] = [1, 1, 1, 1, 1, 1, 1, 1]
        self.WPawnKing[7][4] = -1
        self.BPawnKing = np.zeros((8, 8))
        self.BPawnKing[1] = [1, 1, 1, 1, 1, 1, 1, 1]
        self.BPawnKing[0][4] = -1

        # example: wN: white kNight, bK: black King, ES: Empty Space

        self.moveLog = []
        self.whiteToMove = True
        self.moveFunctions = {"R": self.getRookMoves,
                              "N": self.getKnightMoves,
                              "B": self.getBishopMoves,
                              "Q": self.getQueenMoves,
                              "K": self.getKingMoves,
                              "P": self.getPawnMoves, }
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = True  # king's in check && no valid moves
        self.stalemate = True  # king's not in check && no valid moves
        self.pins = []
        self.checks = []
        self.enPassantGrid = ()  # store the square where en passant is possible

        self.currentCastle = CastleRights(True, True, True, True)
        self.castleLog = [self.currentCastle.makeCopy()]

    def getTurn(self):
        if self.whiteToMove:
            return "w"
        return "b"

    def makeMove(self, move):
        self.board[move.row0][move.col0] = "ES"
        self.board[move.row1][move.col1] = move.pieceToMove
        # update kings location
        if move.pieceToMove == "wK":
            self.whiteKingLocation = (move.row1, move.col1)
            self.WPawnKing[move.row0][move.col0] = 0
            self.WPawnKing[move.row1][move.col1] = -1
        elif move.pieceToMove == "bK":
            self.blackKingLocation = (move.row1, move.col1)
            self.BPawnKing[move.row0][move.col0] = 0
            self.BPawnKing[move.row1][move.col1] = -1
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # update pawn structure
        if move.pieceToMove == "wP":
            self.WPawnKing[move.row0][move.col0] = 0
            self.WPawnKing[move.row1][move.col1] = 1
        elif move.pieceToMove == "bP":
            self.BPawnKing[move.row0][move.col0] = 0
            self.BPawnKing[move.row1][move.col1] = 1
        # if pawn promotion:
        if move.isPawnPromotion:
            if move.promotionChoice == "Q":
                self.board[move.row1][move.col1] = move.pieceToMove[0] + "Q"
        # if enpassant:
        if move.isEnPassantMove:
            self.board[move.row0][move.col1] = "ES"
        # if the move is 2-step pawn advance: enpassant possible
        if move.pieceToMove[1] == "P" and abs(move.row1 - move.row0) == 2:
            self.enPassantGrid = ((move.row1 + move.row0) // 2, move.col0)
        else:
            self.enPassantGrid = ()  # only valid for one step
        # if castling
        if move.isCastling:
            # if move rightward -- king side castle
            if move.col1 - move.col0 == 2:
                self.board[move.row1][move.col1 - 1] = self.board[move.row1][move.col1 + 1]
                self.board[move.row1][move.col1 + 1] = "ES"
            # else queen side castle
            else:
                self.board[move.row1][move.col1 + 1] = self.board[move.row1][move.col1 - 2]
                self.board[move.row1][move.col1 - 2] = "ES"
        # update castling rights
        if move.pieceToMove == "wK":
            self.currentCastle.wks = False
            self.currentCastle.wqs = False
        elif move.pieceToMove == "bK":
            self.currentCastle.bks = False
            self.currentCastle.bqs = False
        elif move.pieceToMove == "wR":
            if self.currentCastle.wqs == True or self.currentCastle.wks == True:
                if move.row0 == 7:
                    if move.col0 == 0:
                        self.currentCastle.wqs = False
                    elif move.col0 == 7:
                        self.currentCastle.wks = False
        elif move.pieceToMove == "bR":
            if self.currentCastle.bqs == True or self.currentCastle.bks == True:
                if move.row0 == 0:
                    if move.col0 == 0:
                        self.currentCastle.bqs = False
                    elif move.col0 == 7:
                        self.currentCastle.bks = False
        self.castleLog.append(CastleRights(wks=self.currentCastle.wks, wqs=self.currentCastle.wqs,
                                           bks=self.currentCastle.bks, bqs=self.currentCastle.bqs))

    def undoMove(self):
        if len(self.moveLog) == 0:
            return
        else:
            move = self.moveLog.pop()
            self.board[move.row0][move.col0] = move.pieceToMove
            self.board[move.row1][move.col1] = move.pieceToCapture
            # update kings location
            if move.pieceToMove == "wK":
                self.whiteKingLocation = (move.row0, move.col0)
            elif move.pieceToMove == "bK":
                if move.pieceToMove == "wK":
                    self.blackKingLocation = (move.row0, move.col0)
            self.whiteToMove = not self.whiteToMove
            # undo en passant
            if move.isEnPassantMove:
                self.board[move.row1][move.col1] = "ES"
                self.board[move.row0][move.col1] = move.pieceToCapture
                self.enPassantGrid = (move.row1, move.col1)
            # undo two-square pawn advance
            if move.pieceToMove[1] == "P" and abs(move.row1 - move.row0) == 2:
                self.enPassantGrid = ()
            # undo the change of castle rights
            self.castleLog.pop()
            self.currentCastle = self.castleLog[-1]
            # undo the castle moves
            if move.isCastling:
                # if move rightward -- king side castle
                if move.col1 - move.col0 == 2:
                    self.board[move.row1][move.col1 + 1] = self.board[move.row1][move.col1 - 1]
                    self.board[move.row1][move.col1 - 1] = "ES"

                # else queen side castle
                else:
                    self.board[move.row1][move.col1 - 2] = self.board[move.row1][move.col1 + 1]
                    self.board[move.row1][move.col1 + 1] = "ES"
            self.checkmate = False
            self.stalemate = False

    # generate all moves, cannot leave the king in check
    def getValidMoves(self):
        moves = self.getPossibleMoves(castle=True)
        enpassantGrid = self.enPassantGrid
        castlingPossible = self.currentCastle.makeCopy()
        # for each move make the move
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])  # it's now opponent's turn
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        self.enPassantGrid = enpassantGrid
        self.currentCastle = castlingPossible
        return moves

    # determine if current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.underAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        return self.underAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # determine if current player's r-c square is under attack
    def underAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getPossibleMoves()  # moves that might attack the r-c grid
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.row1 == r and move.col1 == c:
                return True
        return False

    # generate all possible moves, some may leave the king in check
    def getPossibleMoves(self, castle=False):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    if castle and piece == "K":
                        self.getKingMoves(row, col, moves, True)
                    else:
                        self.moveFunctions[piece](row, col, moves)
        return moves

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove:
            if row - 1 >= 0 and self.board[row - 1][col] == "ES":
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "ES":
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enPassantGrid:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, enpassant=True))
            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enPassantGrid:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, enpassant=True))
        else:
            # black pawn move down the board ( row++
            if row + 1 <= 7 and self.board[row + 1][col] == "ES":
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "ES":
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enPassantGrid:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, enpassant=True))
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enPassantGrid:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, enpassant=True))

    def getRookMoves(self, row, col, moves):
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for direction in directions:
            for i in range(1, 8):
                row1 = row + i * direction[0]
                col1 = col + i * direction[1]
                if 0 <= row1 <= 7 and 0 <= col1 <= 7:
                    if self.board[row1][col1] == "ES":
                        moves.append(Move((row, col), (row1, col1), self.board))
                    elif self.board[row1][col1][0] != self.getTurn():
                        moves.append(Move((row, col), (row1, col1), self.board))
                        break
                    else:
                        break

    def getBishopMoves(self, row, col, moves):
        directions = ((1, 1), (-1, -1), (-1, 1), (1, -1))
        for direction in directions:
            for i in range(1, 8):
                row1 = row + i * direction[0]
                col1 = col + i * direction[1]
                if 0 <= row1 <= 7 and 0 <= col1 <= 7:
                    if self.board[row1][col1] == "ES":
                        moves.append(Move((row, col), (row1, col1), self.board))
                    elif self.board[row1][col1][0] != self.getTurn():
                        moves.append(Move((row, col), (row1, col1), self.board))
                        break
                    else:
                        break

    def getKingMoves(self, row, col, moves, castle=False):
        directions = ((1, 0), (-1, 0), (1, 1), (0, 1), (-1, 1), (1, -1), (0, -1), (-1, -1))
        for direction in directions:
            row1 = row + direction[0]
            col1 = col + direction[1]
            if 0 <= row1 <= 7 and 0 <= col1 <= 7:
                if self.board[row1][col1] == "ES" or self.board[row1][col1][0] != self.getTurn():
                    moves.append(Move((row, col), (row1, col1), self.board))
        if castle:
            self.getCastleMoves(row, col, moves)
            # get all valid castle moves for the color king at (row,col) and append

    def getCastleMoves(self, row, col, moves):
        # check if king is in check
        if self.underAttack(row, col):
            return
        if (self.whiteToMove and self.currentCastle.wks) or (not self.whiteToMove and self.currentCastle.bks):
            self.getKingCastleMove(row, col, moves)
        if (self.whiteToMove and self.currentCastle.wqs) or (not self.whiteToMove and self.currentCastle.bqs):
            self.getQueenCastleMove(row, col, moves)

    def getKingCastleMove(self, row, col, moves):
        if self.board[row][col + 1] != "ES" or self.board[row][col + 2] != "ES":
            return
        if self.underAttack(row, col + 1) or self.underAttack(row, col + 2):
            return
        moves.append(Move((row, col), (row, col + 2), self.board, castling=True))

    def getQueenCastleMove(self, row, col, moves):
        # queen side -- left
        if self.board[row][col - 1] != "ES" or self.board[row][col - 2] != "ES" or self.board[row][col - 3] != "ES":
            return
        if self.underAttack(row, col - 1) or self.underAttack(row, col - 2):
            return
        moves.append(Move((row, col), (row, col - 2), self.board, castling=True))

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKnightMoves(self, row, col, moves):
        directions = ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1))
        for direction in directions:
            row1 = row + direction[0]
            col1 = col + direction[1]
            if 0 <= row1 <= 7 and 0 <= col1 <= 7:
                if self.board[row1][col1] == "ES" or self.board[row1][col1][0] != self.getTurn():
                    moves.append(Move((row, col), (row1, col1), self.board))


class CastleRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs

    def __str__(self):
        wksStr = "True" if self.wks else "False"
        wqsStr = "True" if self.wqs else "False"
        bksStr = "True" if self.bks else "False"
        bqsStr = "True" if self.bqs else "False"
        return "wks:" + wksStr + " wqs:" + wqsStr + " bks:" + bksStr + " bqs:" + bqsStr

    def makeCopy(self):
        copy = CastleRights(wks=self.wks, wqs=self.wqs, bks=self.bks, bqs=self.bqs)
        return copy


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start_square, end_square, board, enpassant=False, castling=False):
        self.row0, self.col0 = start_square
        self.row1, self.col1 = end_square
        self.pieceToMove = board[self.row0][self.col0]
        self.pieceToCapture = board[self.row1][self.col1]

        self.promotionChoice = "Q"
        self.isPawnPromotion = (self.pieceToMove == "wP" and self.row1 == 0) or \
                               (self.pieceToMove == "bP" and self.row1 == 7)

        self.isEnPassantMove = enpassant
        self.isCastling = castling
        if enpassant:
            self.pieceToCapture = "wP" if self.pieceToMove == "bP" else "bP"

    def __hash__(self):
        return hash((self.row0, self.col0, self.row1, self.col1))

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.row0 == other.row0 and self.col0 == other.col0 and \
               self.row1 == other.row1 and self.col1 == other.col1

    def getChessNotation(self):
        # TODO: Convert to formal chess notation
        return self.colsToFiles[self.col0] + self.rowsToRanks[self.row0] + "->" + \
               self.colsToFiles[self.col1] + self.rowsToRanks[self.row1]


materialValue = {"K": 0, "Q": 9, "P": 1, "R": 5, "B": 3, "N": 3}


def materialBalance(gameState):
    board = gameState.board
    wSum = 0
    bSum = 0
    for row in board:
        for sq in row:
            if sq[0] == "w":
                wSum += materialValue[sq[1]]
            elif sq[0] == "b":
                bSum += materialValue[sq[1]]
    return wSum - bSum


def mobility(gameState):
    return len(gameState.getValidMoves())


class PawnKingStructure:
    def __init__(self, white=True):
        self.pk = np.zeros((8, 8))
        if white:
            self.pk[6] = [1, 1, 1, 1, 1, 1, 1, 1]
            self.pk[7][4] = -1
        else:
            self.pk = [1, 1, 1, 1, 1, 1, 1, 1]
            self.pk[0][4] = -1

    #def __hash__(self):


    def __eq__(self, other):
        if not isinstance(other, PawnKingStructure):
            return False
        if self.pk == other.pk:
            return True
        np.flip(other.pk, axis=0)
        if self.pk == other.pk:
            return True
        return False
