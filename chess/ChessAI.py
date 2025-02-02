"""
This is AI module file.
This is responsible for handling AI moves by using different algorithms.
"""
import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
nextMove = None


'''
Picks and returns a random move.
'''
def findRandomMove(validMoves):
    if not validMoves:  # Check for empty list of moves
        return None
    return validMoves[random.randint(0, len(validMoves) - 1)]

'''
Find the best move based on material alone.
'''
def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    # Loop through all player's legal moves
    for playerMove in validMoves:
        gs.makeMove(playerMove) # Make the player's move
        opponentMoves = gs.getValidMoves()
        if gs.staleMate:
            opponentMaxScore = STALEMATE
        elif gs.checkMate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            # Loop through opponent's legal moves
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)  # Make the opponent's move
                gs.getValidMoves()
                # Evaluate game state
                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove() # Undo opponent's move
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()  # Undo player's move

    return bestPlayerMove

'''
Helper method to make first recursive call.
'''
def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove

'''
Finds best move by minimax algorithm.
'''

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = -findMoveMinMax(gs, nextMoves, depth - 1, False)
            gs.undoMove()
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move

        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            gs.undoMove()
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move

        return minScore

'''
A positive score is good for white. A negative score is good for black.
'''

def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if not square:  # Check if square is empty
                continue
            if square[0] == 'w':  # White pieces
                score += pieceScore.get(square[1], 0)  # Use .get to avoid KeyError
            elif square[0] == 'b':  # Black pieces
                score -= pieceScore.get(square[1], 0)  # Use .get to avoid KeyError

    return score

'''
Score the board based on material.
'''
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if not square:  # Check if square is empty
                continue
            if square[0] == 'w':  # White pieces
                score += pieceScore.get(square[1], 0)  # Use .get to avoid KeyError
            elif square[0] == 'b':  # Black pieces
                score -= pieceScore.get(square[1], 0)  # Use .get to avoid KeyError

    return score








