"""
This is AI module file.
This is responsible for handling AI moves by using different algorithms.
"""
import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0


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

    # Save original checkmate and stalemate states
    originalCheckmate = gs.checkMate
    originalStalemate = gs.staleMate

    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE

        # Save states before opponent's moves
        tempCheckmate = gs.checkMate
        tempStalemate = gs.staleMate

        for opponentMove in opponentMoves:
            gs.makeMove(opponentMove)
            # Evaluate the position
            if gs.checkMate:
                score = -turnMultiplier * CHECKMATE
            elif gs.staleMate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
            # Reset checkmate/stalemate after undo
            gs.checkMate = tempCheckmate
            gs.staleMate = tempStalemate

        # Restore original states after evaluating all opponent moves
        gs.undoMove()
        gs.checkMate = originalCheckmate
        gs.staleMate = originalStalemate

        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove

    return bestPlayerMove
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








