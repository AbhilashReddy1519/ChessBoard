"""
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining the valid moves at current state.
It will also keep mov log.
"""


class GameState:
    def __init__(self):
        #board is 8x8 2d list ,each element of the list has 2 characters.
        #The first character represents the color of the piece, 'b' or 'w'
        #The second character represents the type of the piece 'K', 'Q', 'R', 'B', 'N', or 'P'
        #"--" - represent an empty space with no piece.

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N':self.getKnightMoves,
                               'B':self.getBishopMoves, 'Q':self.getQueenMoves, 'K':self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []


    '''
    Takes a move as parameter and executes it.(this will not work for castling, pawn promotion and en passant)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players
        #update the king's location if moved
        if move.pieceMoved[1] == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol) # if self.whiteToMove else (move.startRow, move.startCol)
        elif move.pieceMoved[1] == "bk":
            self.blackKingLocation = (move.endRow, move.endCol) #if self.whiteToMove else (move.startRow, move.startCol)
    '''
    Undo the last move made.
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:  #make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns back
            #update the king's position if needed
            if move.pieceMoved[1] == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol) #if self.whiteToMove else (move.endRow, move.endCol)
            elif move.pieceMoved[1] == "bk":
                self.blackKingLocation = (move.startRow, move.startCol) #if self.whiteToMove else (move.endRow, move.endCol)


    '''
    All moves considering checks.
    '''
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                #to block a check you must move a piece into one of the square between the enemy piece and king
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #enemy piece causing the check
                validSquares = [] #squares that pieces can move to
                #if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquares = (kingRow + check[2] * i, kingCol + check[3] * i) #check[2] and check[3] are the check directions
                        validSquares.append(validSquares)
                        if validSquares[0] == checkRow and validSquares[1] == checkCol: #once you get to piece and checks
                            break
                #get rif of any moves that don't block check or moves king
                for i in range(len(moves) - 1, -1, -1): #go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K': #move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doesn't block check or capture piece
                            moves.remove(moves[i])
            else: #double check, king has to move
                self.getRookMoves(kingRow, kingCol, moves)
        else: #not in check so all moves are fine
            moves = self.getAllPossibleMoves()

        return moves


    '''
    All moves without considering checks.
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls the appropriate move functions based on piece type
        return moves




    '''
    Get all the pawn moves for the pawn located at row, col and add them to the list of moves.
    '''
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3]) == c
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == "--": #1 square pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r,c), (r-1,c), self.board))
                    if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                        moves.append(Move((r,c), (r-2,c), self.board))

            if c-1 >= 0: #capture to the left
                if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r,c), (r-1,c-1), self.board)) #here check if code not work change r-1,c-1 after move
            if c+1 <= 7: #captures to right
                if self.board[r-1][c+1][0] == 'b': #captures to right
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r,c), (r-1,c+1), self.board))

        else: #black pawn moves
            if self.board[r+1][c] == "--": #1 square pawn advance
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r,c), (r+1,c), self.board))
                    if r == 1 and self.board[r+2][c] == "--": #2 square pawn advance
                        moves.append(Move((r,c), (r+2,c), self.board))

            if c-1 >= 0: #capture to the left
                if self.board[r+1][c-1][0] == 'w': #captures to right
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r,c), (r+1,c-1), self.board))
            if c+1 <= 7: #captures to right
                if self.board[r+1][c+1][0] == 'w': #captures to right
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r,c), (r+1,c+1), self.board))
        #let's add pawn promotions
    '''
    Get all the rook moves for the rook located at row, col and add them to the list of moves.
    '''
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3]) == c
                if self.board[r][c][1] != "Q": #can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break


        directions = {(-1, 0), (0, -1), (1, 0), (0, 1)} #up left down right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #empty space valid
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy piece valid
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                            break
                        else: ##friendly piece invalid
                            break
                else: #off board
                    break

    '''
    Get all the Knight moves for the rook located at row, col and add them to the list of moves.
    '''
    def getKnightMoves(self,r ,c , moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #not an ally piece (empty or enemy piece)
                        moves.append(Move((r,c), (endRow,endCol), self.board))


    '''
    Get all the Bishop moves for the rook located at row, col and add them to the list of moves.
    '''
    def getBishopMoves(self,r ,c , moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3]) == c
                self.pins.remove(self.pins[i])
                break


        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #4 diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8): #bishop can move max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #is it on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #empty space valid
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy piece valid
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                            break
                        else: #friendly piece invalid
                            break
                else: #off board
                    break

    '''
    Get all the Queen moves for the rook located at row, col and add them to the list of moves.
    '''
    def getQueenMoves(self,r ,c , moves): #since queen moves are combination of knight and bishop
        self.getRookMoves(r ,c , moves)
        self.getBishopMoves(r ,c , moves)

    '''
    Get all the king moves for the rook located at row, col and add them to the list of moves.
    '''
    def getKingMoves(self,r ,c , moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not an ally piece (empty or enemy piece)
                    #place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                    #place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    '''
    Returns if the player is in check, a list of pins, and a list of checks.
    '''
    def checkForPinsAndChecks(self):
        pins = [] #squares where the allied pinned piece is and direction pinned from
        checks  = [] #squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): #1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type =  endPiece[1]
                        #5 possibilities here in this complex conditional
                        # 1. orthogonally away from king and piece is a rook
                        # 2. diagonally away from king and piece is rook
                        # 3. 1 square away diagonally from king and piece is a pawn
                        # 4. any direction and piece is a queen
                        # 5. any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p') and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5)) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): #no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: #enemy piece not applying check.
                            break
                else: #off board
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': #enemy knight attack king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

class Move:
    #maps keys to values
    #key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol


    '''
    Overriding the equals method to compare two moves.
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

