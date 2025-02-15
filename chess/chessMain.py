"""
This is main driver file.
It will be responsible for handling user input and displaying the current GameState object.
"""

import sys
import pygame as p
from chess import chessEngine, ChessAI
from multiprocessing import Process, Queue

#Initialize the mixer
p.mixer.init()

# Sound effects for various game actions
move_sound = p.mixer.Sound("sounds/move-sound.mp3") # Sound for a piece move
capture_sound = p.mixer.Sound("sounds/capture.mp3") #Sound for capturing a piece
promote_sound = p.mixer.Sound("sounds/promote.mp3") # Sound for pawn promotion


# Screen dimensions and other constants
WIDTH = HEIGHT = 512 # Main screen width and height in pixels
MOVE_LOG_PANEL_WIDTH = 250  # Panel dimensions
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8 # Chessboard grid (8x8 by default)
SQ_SIZE = HEIGHT // DIMENSION # Square size
MAX_FPS = 15 # Frame rate for rendering animations
IMAGES = {} # Dictionary to cache and load piece images

'''
This two variables used for defining AI player and human player.
'''

SET_WHITE_AS_BOT = True #if true Ai bot plays Setting for if the white side is controlled by AI
SET_BLACK_AS_BOT = True #if false human plays Setting for if the black side is controlled by AI


'''
These are colors used in the code
'''

colors = [p.Color("#EBECD0"), p.Color("#739552")]
LIGHT_SQUARE_COLOR = (237, 238, 209)
DARK_SQUARE_COLOR = (119, 153, 82)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (255, 255, 51)



'''
Initialise a global dictionary of images. This will be called exactly once in the main
Loads and caches chess piece images into the global `IMAGES` dictionary.
This function is used to improve performance by preloading all necessary assets so they can be reused throughout the application.

'''

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    try:
        for piece in pieces:
            # IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))
            # p.transform.smoothscale is a bit slower than p.transform.scale, using this to reduce pixelation and better visual quality for scaling images to larger sizes
            IMAGES[piece] = p.transform.smoothscale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    except Exception as e:
        print(f"Error while loading images: {e}")

#Note: we can access an image by saying IMAGES['wp']

'''
Displays a popup when a pawn reaches the last rank to allow the player to choose
a piece for promotion. Options typically include Queen, Rook, Bishop, or Knight.
'''

def pawnPromotionPopup(screen, gs):
    font = p.font.SysFont("Arial", 30, False, False)
    text = font.render("Choose promotion:", True, p.Color("black"))

    # Create buttons for promotion choices with images
    width, height = 100, 100
    buttons = [
        p.Rect(100, 200, width, height),
        p.Rect(200, 200, width, height),
        p.Rect(300, 200, width, height),
        p.Rect(400, 200, width, height)
    ]

    if gs.whiteToMove:
        button_images = [
            p.transform.smoothscale(p.image.load(
                "images1/bQ.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/bR.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/bB.png"), (100, 100)),
            p.transform.smoothscale(p.image.load("images1/bN.png"), (100, 100))
        ]
    else:
        button_images = [
            p.transform.smoothscale(p.image.load(
                "images1/wQ.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/wR.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/wB.png"), (100, 100)),
            p.transform.smoothscale(p.image.load("images1/wN.png"), (100, 100))
        ]

    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = e.pos
                for i, button in enumerate(buttons):
                    if button.collidepoint(mouse_pos): # Return the index of the selected piece
                        if i == 0:
                            return "Q"
                        elif i == 1:
                            return "R"
                        elif i == 2:
                            return "B"
                        else:
                            return "N"

        screen.fill(p.Color(LIGHT_SQUARE_COLOR))
        screen.blit(text, (110, 150))

        for i, button in enumerate(buttons):
            p.draw.rect(screen, p.Color("white"), button)
            screen.blit(button_images[i], button.topleft)

        p.display.flip()




'''
The main driver for code.This will handle user input and updating the graphics.
Key Features:
    - Handles human-vs-human and bot configuration.
    - Tracks and highlights legal/potential moves.
    - Manages animations and sounds for realism.
'''

def main():
    #initialise py game
    p.init()
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 12, False, False)
    # Creating GameState object calling our constructor
    gs = chessEngine.GameState()
    # this used to rotate board since player wants to play as black
    if gs.playerWantsToPlayAsBlack:
        gs.board = gs.board1
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    animate = False #flag variable for when we should animate a move
    # print(gs.board)
    loadImages() #only do this once before the while loop
    running = True
    sqSelected = () #no square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = [] #keep track of player clicks (two tuples: [(6, 4), (4,4)])
    gameOver = False
    playerOne = not SET_WHITE_AS_BOT #if a human is playing white, then this will be true. If AI is playing then false
    playerTwo = not SET_BLACK_AS_BOT #same as above but for black
    AIThinking = False #true if AI is thinking.
    moveFinderProcess = None
    moveUndone = False
    pieceCaptured = False
    positionHistory = ""
    previousPos = ""
    countMovesForDraw = 0
    COUNT_DRAW = 0



    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver: # allow mouse handling only if its not game over
                    location = p.mouse.get_pos() #(x, y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col) or col >= 8: #user clicked the same square twice
                        sqSelected = () #deselect
                        playerClicks = [] #clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append for both 1st and 2nd click
                    if len(playerClicks) == 2 and humanTurn: #after 2nd click
                        move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                # Check if a piece is captured at the destination square
                                if gs.board[validMoves[i].endRow][validMoves[i].endCol] != '--':
                                    pieceCaptured = True
                                gs.makeMove(validMoves[i])
                                if move.isPawnPromotion:
                                    # Show pawn promotion popup and get the selected piece
                                    promotion_choice = pawnPromotionPopup(screen, gs)
                                    # Set the promoted piece on the board
                                    gs.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotion_choice
                                    promote_sound.play()
                                    pieceCaptured = False
                                #add sound for human move
                                if pieceCaptured or move.isEnpassantMove:
                                    capture_sound.play() #plays capture sound
                                elif not move.isPawnPromotion:
                                    move_sound.play() #plays move sound
                                pieceCaptured = False
                                moveMade = True
                                animate = True
                                sqSelected = () #reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                    if e.key == p.K_z: #undo when 'z' is pressed
                        gs.undoMove()
                        moveMade = True
                        animate = False
                        gameOver = False
                        if AIThinking:
                            moveFinderProcess.terminate() # terminate the AI thinking if we undo
                            AIThinking = False
                        moveUndone = True
                    if e.key == p.K_r: #reset the board when 'r' is pressed
                        gs = chessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        animate = False
                        gameOver = False
                        if AIThinking:
                            moveFinderProcess.terminate() # terminate the AI thinking if we undo
                            AIThinking = False
                        moveUndone = False

        #AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue() #keep track of data, to pass data between threads
                moveFinderProcess = Process(target=ChessAI.findBestMove, args=(gs, validMoves, returnQueue)) # when processing start we call these process
                # call findBestMove(gs, validMoves, returnQueue) #rest of the code could still work even if the AI is thinking
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()  # return from returnQueue
                if AIMove is None:
                    AIMove = ChessAI.findRandomMove(validMoves)

                if gs.board[AIMove.endRow][AIMove.endCol] != '--':
                    pieceCaptured = True

                gs.makeMove(AIMove)

                if AIMove.isPawnPromotion:
                    # Show pawn promotion popup and get the selected piece
                    promotion_choice = pawnPromotionPopup(screen, gs)
                    # Set the promoted piece on the board
                    gs.board[AIMove.endRow][AIMove.endCol] = AIMove.pieceMoved[0] + promotion_choice
                    promote_sound.play()
                    pieceCaptured = False

                if pieceCaptured or AIMove.isEnpassantMove:
                    capture_sound.play()
                elif not AIMove.isPawnPromotion:
                    move_sound.play()

                pieceCaptured = False
                moveMade = True
                animate = True
                sqSelected = ()
                playerClicks = []
                AIThinking = False

            # AIMove = ChessAI.findBestMoveMinMax(gs, validMoves)
            # if AIMove is None:
            #     AIMove = ChessAI.findRandomMove(validMoves)
            # gs.makeMove(AIMove)
            # print("move by AI: " + AIMove.getChessNotation())  # Print the AI's move
            # moveMade = True
            # animate = True

        if moveMade:
            if countMovesForDraw == 0 or countMovesForDraw == 1 or countMovesForDraw == 2 or countMovesForDraw == 3:
                countMovesForDraw += 1
            if countMovesForDraw == 4:
                positionHistory += gs.getBoardString()
                if previousPos == positionHistory:
                    COUNT_DRAW += 1
                    positionHistory = ""
                    countMovesForDraw = 0
                else:
                    previousPos = positionHistory
                    positionHistory = ""
                    countMovesForDraw = 0
                    COUNT_DRAW = 0
            #call animateMove to animate the move
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            # Generate new set of valid move if valid move is made
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if COUNT_DRAW == 1:
            gameOver = True
            drawText(screen, "Draw due to repetition")
        elif gs.checkMate:
            gameOver = True
            drawText(screen, "Black wins by checkmate." if gs.whiteToMove else "White wins by checkmate.")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate.")

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlight the square and moves that the user has selected.
Highlights valid moves and important squares on the chessboard. 
Colors specified in configuration are applied for readability and gameplay ease.

'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"): #sqSelected is a piece that can be moved
            #highlight selected square
            # Surface in pygame used to add images or transparency feature
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transperancy value -> 0 transparent; 255 opaque
            s.fill(p.Color("yellow"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color("#ffff33"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))


'''
Responsible for all the graphics within a current game state.
Draws the complete game state on the Pygame window.
This includes the chessboard, pieces, move log, and any highlighted squares.

'''
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen) #draw squares on the board
    #add in piece highlighting or move suggestions
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw pieces on top of these squares
    drawMoveLog(screen, gs, moveLogFont)

'''
Draw the squares on the board.The top left square is always light.
Draws the chessboard grid based on the `LIGHT_SQUARE_COLOR` and `DARK_SQUARE_COLOR`
configurations. The board is rendered as an 8x8 grid with alternating colors.

'''
def drawBoard(screen):
    global colors
    colors = [p.Color("#EBECD0"), p.Color("#739552")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw the pieces on the board using the current GameState.board
Draws the chess pieces on top of the board grid based on the current game state.
Takes into account the location of all pieces on the `GameState.board` attribute.

'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the moveLog of the pieces moved in the game.
Draws a move log panel on the right side of the screen.
This log lists all moves made during the game in standard chess notation.
Useful for analyzing or reviewing gameplay history.

'''

def drawMoveLog(screen, gs, moveLogFont):
    p.draw.rect(screen, p.Color(LIGHT_SQUARE_COLOR), p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT))
    moveLog = gs.moveLog
    moveTexts = []

    for i in range(0, len(moveLog), 2):
        moveString = " " + str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i+1])
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 10 # Increase padding for better readability
    lineSpacing = 5  # Increase line spacing for better separation
    textY = padding

    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]

        textObject = moveLogFont.render(text, True, p.Color('black'))

        # Adjust text location based on padding and line spacing
        textLocation = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT).move(padding, textY)
        screen.blit(textObject, textLocation)

        # Update Y coordinate for the next line with increased line spacing
        textY += textObject.get_height() + lineSpacing

'''
Animating the moves.
Animates the movement of a piece from the starting square to the ending square.
This provides a smoother gameplay experience by making transitions visually clear.

'''

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5 #frames to move one square
    # how many frame the animation will take
    frameCount = (abs(dR) + abs(dC))*framesPerSquare
    for frame in range(frameCount + 1): # generate all the coordinates
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)  # pygame rectangle
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)
'''
Display text on the screen.
Draws any overlay or game-ending text on the screen.
For example, text like "Checkmate" or "Stalemate" is displayed when required.

'''
def drawText(screen, text):
    font = p.font.SysFont("Arial", 32, True, True)
    textObject = font.render(text, True, p.Color("black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(1, 1))

if __name__ == "__main__":
    main()

