"""
This is main driver file.
It will be responsible for handling user input and displaying the current GameState object.
"""

import pygame as p
from chess import chessEngine

WIDTH = HEIGHT = 512 #400 is another option
DIMENSION = 8 #dimensions of a chess board are 8x8
SQ_SIZE = 15 #for animation later on
IMAGES = {}

'''
Initialise a global dictionary of images. This will be called exactly once in the main
'''

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+piece+".png"),(SQ_SIZE, SQ_SIZE))
    #Note: we can access an image by saying IMAGES['wp']

'''
The main driver for code.This will handle user input and updating the graphics.
'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessEngine.GameState()


'''end of the day'''