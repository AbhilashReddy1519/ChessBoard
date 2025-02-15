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

        self.board1 = [
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']]

        self.moveFunctions = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N':self.getKnightMoves,
            'B':self.getBishopMoves,
            'Q':self.getQueenMoves,
            'K':self.getKingMoves
        }
        # Game state variables
        self.whiteToMove = True
        self.playerWantsToPlayAsBlack = False
        self.moveLog = []
        if self.playerWantsToPlayAsBlack:
            self.whiteKingLocation = (0, 4)
            self.blackKingLocation = (7, 4)
        else:
            self.whiteKingLocation = (7, 4)
            self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.inCheck = False
        self.score = 0
        self.pins = []
        self.checks = []
        self.enpassantPossible = () #coordinates for the square where the en passant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]

        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]



    '''
    Takes a move as parameter and executes it.(this will not work for castling, pawn promotion and en passant)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" # Clear initial square
        self.board[move.endRow][move.endCol] = move.pieceMoved # Move piece to target square
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players
        # update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)  # if self.whiteToMove else (move.startRow, move.startCol)
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)  # if self.whiteToMove else (move.startRow, move.startCol)
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False

        #pawn promotion
        # if move.isPawnPromotion:
        #     self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #enpassasnt move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" #capturing the pawn

        #update enpassant possible variable
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: #only on 2 square a pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves the rook
                self.board[move.endRow][move.endCol+1] = '--' #erase old rook
            else: #queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #move the rook
                self.board[move.endRow][move.endCol-2] = '--' #erase old rook

        #update castling rights -- whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))



    '''
    Undo the last move made.
    '''

    def undoMove(self):
        if len(self.moveLog) != 0:  # Make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # Switch turns back

            # Update the king's position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo en passant move
            if move.isEnPassantMove:
                self.board[move.endRow][move.startCol] = '--'  # Restore captured pawn
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            # Undo en passant possible log
            if len(self.enpassantPossibleLog) > 0:
                self.enpassantPossibleLog.pop()
                self.enpassantPossible = self.enpassantPossibleLog[-1] if self.enpassantPossibleLog else ()
            else:
                self.enpassantPossible = ()  # Default to no en passant possible

            # Undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]

            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # Kingside castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # Queenside castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkMate = False
            self.staleMate = False

    '''
    Update the castling rights based on the move that was just made.
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.bks = False




    '''
    All moves considering checks.
    '''
    def getValidMoves(self):
        # 1. generate all possible moves
        moves = self.getAllPossibleMoves()
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            # only one check to the king, move the king or block the check with a piece
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                # (row, col) of the piece which is causing the check
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                # position of the piece which is causing the check
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # squares that pieces can move to
                # if check is from knight than either move the king or take the knight
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        # check[2], check[3] are the check directions
                        validSq = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSq)
                        # upto the piece applying check
                        if validSq[0] == checkRow and validSq[1] == checkCol:
                            break
                # remove the move that doesn't prevent from check
                # going backward in all possible moves
                for i in range(len(moves) - 1, -1, -1):
                    # as the king is not moved it should block the check if not then remove the move from moves
                    if moves[i].pieceMoved[1] != 'K':
                        # if not in validSquares then it do not block check or capture the piece making check
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])  # remove the moves
                        #till now, we will be able to find check and can move piece to block check but, we are doing nothing about the pin so it will allow us to move the pin pieced
                        #what if we move the king and is in the position of pinned we would still be able to move the pinned piece and let king be in check
            else:  # if double check then king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check all checks in moves are fine
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:  # either checkmate or stalemate
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else: # Reset checkmate and stalemate if moves are available
            self.checkMate = False
            self.staleMate = False

        # self.enpassantPossible = tempEnpassantPossible
        # self.currentCastlingRight = tempCastleRights
        return moves



    '''
    Determine if the current player is in check.
    '''

    # def inCheck(self):
    #     if self.whiteToMove:
    #         return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
    #     else:
    #         return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if the enemy can attack the square rc
    '''

    def squareUnderAttack(self, row, col, allyColor):
        enemyColor = 'w' if allyColor == 'b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:  # no attack from that direction
                        break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # Possibilities
                        # 1) Rook in any orthogonal directions
                        # 2) Bishop in any diagonal
                        # 3) Queen in orthogonal or diagonal directions
                        # 4) Pawn if onw square away in any diagonal
                        # 5) King in any direction to 1 square (to prevent king move controlled by another king)
                        # For Rook we will check only if directions and up, down, left, right which is in range 0 <= j <=  3 in directions.
                        # Similarity for bishop, in directions we have added the bishop direction in directions (4 to 7).
                        # For pawn if one forward diagonal square in front of king has opponent's pawn
                        if (0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            return True
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break


    '''
    All moves without considering checks.
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[0])): #number of cols in given row
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
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.playerWantsToPlayAsBlack:
            if self.whiteToMove:
                moveAmount = 1
                startRow = 1
                enemyColor = 'b'
                kingRow, kingCol = self.whiteKingLocation
            else:
                moveAmount = -1
                startRow = 6
                enemyColor = 'w'
                kingRow, kingCol = self.blackKingLocation
        else:
            if self.whiteToMove:
                moveAmount = -1
                startRow = 6
                enemyColor = 'b'
                kingRow, kingCol = self.whiteKingLocation
            else:
                moveAmount = 1
                startRow = 1
                enemyColor = 'w'
                kingRow, kingCol = self.blackKingLocation

        if self.board[r + moveAmount][c] == "--":  # first square move
            # if piece is not pinned then its fine or if it is pinned but from forward direction then we can still move
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(
                    Move((r, c), (r+moveAmount, c), self.board))
                # Check if pawn can directly advance to second square
                if r == startRow and self.board[r+2*moveAmount][c] == "--":
                    moves.append(
                        Move((r, c), (r+2*moveAmount, c), self.board))
        # capture
        if c - 1 >= 0:  # there is a col to the left for white
            # check if there is a black piece to the left of your pawn that you can capture
            # if piece is not pinned then its fine or if it is pinned but from left direction then we can capture left piece
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    moves.append(
                        Move((r, c), (r + moveAmount, c - 1), self.board))
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:  # king is left of the pawn
                            # between king and pawn
                            insideRange = range(kingCol + 1, c - 1)
                            # between pawn and boarder
                            outsideRange = range(c + 1, 8)
                        else:  # king is right of the pawn
                            insideRange = range(kingCol - 1, c, - 1)
                            outsideRange = range(c - 2, -1, -1)
                        for i in insideRange:
                            # other piece blocking check
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, isEnpassantMove=True))

        if c + 1 <= 7:  # there is a col to the right for white
            # check if there is a black piece to the right of your pawn that you can capture
            # if piece is not pinned then its fine or if it is pinned but from left direction then we can capture right piece
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    moves.append(
                        Move((r, c), (r + moveAmount, c + 1), self.board))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:  # king is left of the pawn
                            # between king and pawn
                            insideRange = range(kingCol + 1, c)
                            # between pawn and boarder
                            outsideRange = range(c + 2, 8)
                        else:  # king is right of the pawn
                            insideRange = range(kingCol - 1, c + 1, - 1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            # other piece blocking check
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c + 1),
                                          self.board, isEnpassantMove=True))
    '''
    Get all the rook moves for the rook located at row, col and add them to the list of moves.
    '''
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        # down #up #right #left (row, col)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        # enemy color is b if whiteToMove or vice versa
        enemy_color = 'b' if self.whiteToMove else 'w'

        for direction in directions:
            for i in range(1, 8):  # from one position rook can go upto max 7th square
                endRow = r + direction[0] * i  # destination row
                endCol = c + direction[1] * i  # destination col

                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on the board
                    # if piece is not pinned then its fine or if it is pinned but from forward direction then we can still move in both forward and backward direction
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        # check if next square is empty
                        if self.board[endRow][endCol] == '--':
                            # if empty then add moves
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                        # check if piece on next square is opponent
                        elif self.board[endRow][endCol][0] == enemy_color:
                            # if piece is not pinned then its fine or if it is pinned but from forward direction then we can still move
                            if not piecePinned or pinDirection == direction:
                                # then you can at it to the move as you can capture it
                                moves.append(
                                    Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # if neither then break
                            break
                    else:  # out of the board
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
        # allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                if not piecePinned:
                    # if white to move and destination either have no piece or have a black piece
                    if self.whiteToMove and (self.board[endRow][endCol] == '--' or self.board[endRow][endCol][0] == 'b'):
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    # if black to move and destination either have no piece or have a black piece
                    elif not self.whiteToMove and (self.board[endRow][endCol] == '--' or self.board[endRow][endCol][0] == 'w'):
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))

    '''
    Get all the Bishop moves for the rook located at row, col and add them to the list of moves.
    '''
    def getBishopMoves(self,r ,c , moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = [(1, 1), (-1, -1), (-1, 1), (1, -1)]  # diagonals
        # enemy color is b if whiteToMove or vice versa
        enemy_color = 'b' if self.whiteToMove else 'w'

        for direction in directions:
            for i in range(1, 8):  # from one position bishop can go upto max 7th square
                endRow = r + direction[0] * i  # destination row
                endCol = c + direction[1] * i  # destination col
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on the board
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        # check if next square is empty
                        if self.board[endRow][endCol] == '--':
                            # if empty then add moves
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                        # check if piece on next square is opponent
                        elif self.board[endRow][endCol][0] == enemy_color:
                            # then you can at it to the move as you can capture it
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # if neither then break
                            break
                    else:  # out of the board
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
        allyColor = 'w' if self.whiteToMove else 'b'
        # these for loops denote all possible moves for the king
        for i in range(-1, 2):
            for j in range(-1, 2):
                allyColor = 'w' if self.whiteToMove else 'b'
                if i == 0 and j == 0:  # same square
                    continue
                if 0 <= r + i <= 7 and 0 <= c + j <= 7:
                    endPiece = self.board[r + i][c + j]
                    if endPiece[0] != allyColor:  # the square is empty or has an enemy piece
                        # temporarily move the king to check if it returns in check
                        if allyColor == 'w':
                            self.whiteKingLocation = (r + i, c + j)
                        else:
                            self.blackKingLocation = (r + i, c + j)

                        inCheck, pins, checks = self.checkForPinsAndChecks()
                        # if king's move doesn't return in check, append to moves
                        if not inCheck:
                            moves.append(
                                Move((r, c), (r + i, c + j), self.board))
                        # move the king back to its original location
                        if allyColor == 'w':
                            self.whiteKingLocation = (r, c)
                        else:
                            self.blackKingLocation = (r, c)
        self.getCastleMoves(r, c, moves, allyColor)

    '''
    Get all the castle moves for the king located at row, col and add them to the list of moves. generated for king
    '''
    def getCastleMoves(self,r ,c , moves, allyColor):
        if self.squareUnderAttack(r, c, allyColor):
            return #we can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves,allyColor)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r,c,moves,allyColor)


    def getKingsideCastleMoves(self,r,c,moves,allyColor):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--" and not self.squareUnderAttack(r, c + 1, allyColor) and not self.squareUnderAttack(r, c + 2, allyColor):
            moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))
    def getQueensideCastleMoves(self,r,c,moves,allyColor):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--" and not self.squareUnderAttack(r, c - 1, allyColor) and not self.squareUnderAttack(r, c - 2, allyColor):
            moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
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
        # from king position in all directions, look for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    # find if there is a piece
                    endPiece = self.board[endRow][endCol]
                    # if it's your piece it could be pinned by enemy
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # so add it to the possiblePin
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # after that square if there is another of allied piece, no pins or check is possible
                            break
                    elif endPiece[0] == enemyColor:  # if an enemy piece is found
                        type = endPiece[1]
                        # Possibilities
                        # 1) Rook in any orthogonal directions
                        # 2) Bishop in any diagonal
                        # 3) Queen in orthogonal or diagonal directions
                        # 4) Pawn if onw square away in any diagonal
                        # 5) King in any direction to 1 square (to prevent king move controlled by another king)
                        if ((0 <= j <= 3 and type == 'R') or
                                (4 <= j <= 7 and type == 'B') or
                                (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or
                                                             (enemyColor == 'b' and 4 <= j <= 5))) or
                                (type == 'Q') or (i == 1 and type == 'K')):
                            '''
                            now check if king is pinned or in check
                            '''
                            if possiblePin == ():  # no ally piece front of king, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece front of king but not applying any check
                            break
                    else:
                        break  # off board
            # check for knight checks
            knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                           (1, -2), (1, 2), (2, -1), (2, 1))
            for m in knightMoves:
                endRow = startRow + m[0]
                endCol = startCol + m[1]
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == enemyColor and endPiece[1] == 'N':
                        inCheck = True
                        checks.append((endRow, endCol, m[0], m[1]))
            return inCheck, pins, checks

    def getBoardString(self):
        # Convert the board state to a string
        boardString = ""
        for row in self.board:
            for square in row:
                boardString += square
        return boardString


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs




class Move:
    #maps keys to values
    #key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    pieceNotation = {
        "P": "",
        "R": "R",
        "N": "N",
        "B": "B",
        "Q": "Q",
        "K": "K"
    }

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]

        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        if isEnpassantMove:
            self.pieceCaptured = board[self.startRow][self.endCol]
        else:
            self.pieceCaptured = board[self.endRow][self.endCol]
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow * 1000 + self.startCol * \
                      100 + self.endRow * 10 + self.endCol
        # pawn promotion
        gs = GameState()
        if gs.playerWantsToPlayAsBlack:
            self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 7) or (
                    self.pieceMoved == "bp" and self.endRow == 0)
        else:
            self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (
                    self.pieceMoved == "bp" and self.endRow == 7)

        # enpassant
        self.isEnpassantMove = isEnpassantMove

        #castle move
        self.isCastleMove = isCastleMove



    '''
    Overriding the equals method to compare two moves.
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        #you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def getPieceNotation(self, piece, col):
        if piece[1] == 'p':
            return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        return self.pieceNotation[piece[1]] + self.colsToFiles[col]

    # overriding the str() function
    def __str__(self):
        # castle move:
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        startSquare = self.getRankFile(self.startRow, self.startCol)
        endSquare = self.getRankFile(self.endRow, self.endCol)

        # pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return startSquare + "x" + endSquare
            else:
                return startSquare+endSquare

        # pawn promotion (add later)
        # add + for check # for checkmate

        # piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            return moveString + self.colsToFiles[self.startCol] + "x" + endSquare
        return moveString + self.colsToFiles[self.startCol] + endSquare