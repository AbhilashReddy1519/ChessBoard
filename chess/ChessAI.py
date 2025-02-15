"""
This is AI module file.
This is responsible for handling AI moves by using different algorithms.
"""
import random
"""
A dictionary that assigns a score value to each type of chess piece.
These values are used in heuristics for AI decision-making.
The king ('K') has the highest value for prioritization, and pawns ('p') have the lowest.
"""

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

"""
A table that assigns specific scores based on the positions of knights on the board.
This heuristic encourages knights to move towards favorable squares (e.g., central positions).
"""

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

"""
Position-specific scores for bishops.
Encourages bishops to occupy stronger positions (e.g., diagonals or controlled squares).
"""

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

"""
Position-based scoring for the queen.
Generally allows queens to dominate central or active squares for potential attacks.
"""

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

"""
A table evaluating rook positions.
Encourages placement of rooks on open files or connected ranks.
"""

rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 2, 1, 1, 2, 3, 4]]

"""
Positional scoring for white pawns. Favors advanced pawns and protects valuable pawn structures.
"""

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

"""
Positional scoring for black pawns. Highlights the importance of stable pawn structures 
and penalizes backward or isolated pawns.
"""

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]

"""
A mapping of chess pieces to their respective positional score tables.
Used for evaluating piece placement on the board during scoring.
"""

piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores,
                       "R": rookScores, "wp": whitePawnScores, "bp": blackPawnScores}

CHECKMATE = 1000 # Value assigned to a checkmate scenario, representing a winning state.
STALEMATE = 0 # Value assigned to a stalemate scenario, representing a draw.
"""
The maximum depth for the AI search tree (in levels).
The AI evaluates moves up to this depth using algorithms like minimax or alpha-beta pruning.
We can set the depth up to 4, but anything beyond 4 makes the game slow. A depth of 2 is ideal for fast response times.
"""

DEPTH = 2 # Defines the depth of the AI's move search in the decision tree.
nextMove = None # Placeholder for the best move determined by the AI during search.
SET_WHITE_AS_BOT = -1 # Flag to determine if the white side is controlled by the AI (-1: Human, 1: AI).


'''
Picks and returns a random move.
Selects and returns a random valid move from the list of available moves.
    
    Parameters:
        validMoves (list): A list of moves that are legal in the current game state.
    
    Returns:
        Move: A randomly chosen move object.
    
    Purpose:
    - Used for simple AI behavior or testing, where randomness replaces more complex logic.
'''
def findRandomMove(validMoves):
    if not validMoves:  # Check for empty list of moves
        return None
    return validMoves[random.randint(0, len(validMoves) - 1)]

'''
Find the best move based on material alone.
Finds the best move using basic heuristic evaluation.
    
    Parameters:
        gs (GameState): The current game state instance.
        validMoves (list): A list of all valid moves for the current turn.
    
    Returns:
        Move: The move that gives the highest score after evaluation.
    
    Purpose:
    - Implements a decision-making strategy for AI to choose the most promising move based
      on static evaluation (e.g., material advantage or position).
'''
def findBestMove(gs, validMoves, returnQueue):
    global nextMove, whitePawnScores, blackPawnScores
    nextMove = None
    random.shuffle(validMoves)

    if gs.playerWantsToPlayAsBlack:
        # Swap the variables
        whitePawnScores, blackPawnScores = blackPawnScores, whitePawnScores

    BOT = 1 if gs.whiteToMove else -1

    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -
    CHECKMATE, CHECKMATE, BOT)

    returnQueue.put(nextMove)


'''
Finds best move by minimax algorithm.
Uses the NegaMax algorithm with alpha-beta pruning to evaluate the best move.
    
    Parameters:
        gs (GameState): The game state instance to analyze.
        validMoves (list): A list of all valid moves for the current turn.
        depth (int): The current depth of the search tree.
        alpha (float): The alpha value in alpha-beta pruning (best already explored option for maximizer).
        beta (float): The beta value in alpha-beta pruning (best already explored option for minimizer).
        turnMultiplier (int): Multiplier (1 or -1) to switch evaluation based on player's turn.
    
    Returns:
        (float): The score of the best move found.
    
    Purpose:
    - Explores the decision tree to a specified depth.
    - Ensures computational efficiency by pruning branches that cannot influence the outcome.
    - Prioritizes moves leading to gains while avoiding losses.

'''


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    # (will add later) move ordering - like evaluate all the move first that results in check or evaluate all the move first that results in capturing opponent's queen

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()  # opponent valid moves
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(move, score)
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore  # alpha is the new max
        if alpha >= beta:  # if we find new max is greater than minimum so far in a branch then we stop iterating in that branch as we found a worse move in that branch
            break
    return maxScore

'''
Evaluate the board state for scoring the AI's decision-making.
This function combines material and positional evaluation.
Evaluates the entire board to generate a score for the given game state.
    
    Parameters:
        gs (GameState): The current game state.
    
    Returns:
        int: The score representing the strength or advantage of the current player's position.
    
    Scoring Criteria:
    - Material Advantage: Adds/removes scores based on captured or remaining pieces.
    - Positional Advantage: Uses piece position tables to give bonuses/penalties.
    - Special Considerations: Accounts for checkmate, stalemate, or other terminal conditions.
    
    Purpose:
    - Acts as a heuristic function for the AI search algorithms like minimax or NegaMax.

'''
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            gs.checkMate = False
            return -CHECKMATE  # black wins
        else:
            gs.checkMate = False
            return CHECKMATE  # white wins
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piecePositionScore = 0
                # score positionally based on piece type
                if square[1] != "K":
                    # return score of the piece at that position
                    if square[1] == "p":
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]
                if SET_WHITE_AS_BOT:
                    if square[0] == 'w':
                        score += pieceScore[square[1]] + piecePositionScore * .1
                    elif square[0] == 'b':
                        score -= pieceScore[square[1]] + piecePositionScore * .1
                else:
                    if square[0] == 'w':
                        score -= pieceScore[square[1]] + piecePositionScore * .1
                    elif square[0] == 'b':
                        score += pieceScore[square[1]] + piecePositionScore * .1

    return score









