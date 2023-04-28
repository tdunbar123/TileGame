import pygame
import math
import random
import asyncio
import time

# Initialization and global variables
pygame.init()
pygame.mixer.init()
HEIGHT = 600
WIDTH = 600
CLOCK = pygame.time.Clock()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tiles")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
FONT = pygame.font.SysFont('Arial', 50, True, False)
NEWGAME = True
GAME = False
GAMEOVER = False
NEWROUND = False
BOARDSIZE = 3
BOARD = None
LEVEL = 0
LIVES = 3
TIMELEFT = WIDTH

CORRECT = pygame.mixer.Sound('./Sounds/Correct.wav')
WRONG = pygame.mixer.Sound('./Sounds/Wrong.wav')

# Rectangle object is used to modify the PyGame rectangles to include color characteristics, BLACK as default
# During game, don't draw White rectangles unless they've been clicked on which sets found to True
class Rectangle:
    color = BLACK
    rectangle = None
    found = False

    def __init__(self, rectangle, color=BLACK, found=False):
        self.rectangle = rectangle
        self.color = color
        self.found = found

# Board object used to represent the board state. Board will have black and white colored tiles. White tiles are
# clickable. PyGame Rectangles will be used to represent these tiles.
# __init__ will create all black tiles to begin with, then randomly choose numTiles tiles to change to white
class Board:
    tiles = []

    def __init__(self, boardSize, numTiles):
        global HEIGHT
        self.tiles = []
        size = int(math.floor(HEIGHT/boardSize))
        tempTiles = [[pygame.Rect(j * size, i * size, size-1, size-1) for j in range(boardSize)] for i in range(boardSize)]
        random.seed(int(time.time()))
        whiteTiles = random.sample(range(boardSize * boardSize), numTiles)

        # Convert tempTiles into my custom Rectangle object
        for i in range(len(tempTiles)):
            for j in range(len(tempTiles[0])):
                # Determine the color of the rectangle
                if i * boardSize + j in whiteTiles:
                    color = WHITE
                else:
                    color = BLACK
                self.tiles.append(Rectangle(tempTiles[i][j], color))


# Function for creating a board given current level
# Game starts as a 3x3 board and number of tiles to remember should be between 1/3-1/2 of total tiles in the grid
# Every 4th round the board will grow in size by 1 in each dimension
# This means sub-levels will be calculated by the remainder of level/3, 1 = 1, 2 = 2, 0 = 3
# Function should return a Board object
def createBoard(level):
    global BOARDSIZE
    sublevel = level % 3
    tiles = 0
    if sublevel == 0:
        tiles = math.floor(math.pow(BOARDSIZE, 2)/3)
    elif sublevel == 1:
        tiles = math.floor(math.pow(BOARDSIZE, 2)*1.25/3)
    elif sublevel == 2:
        tiles = math.floor(math.pow(BOARDSIZE, 2)/2)
    return Board(BOARDSIZE, int(tiles))

# Function for drawing the board
def drawBoard(window):
    global BOARD
    for rect in BOARD.tiles:
        pygame.draw.rect(window, rect.color, rect.rectangle)
        # Draw outline
        if rect.color == BLACK:
            pygame.draw.rect(window, WHITE, rect.rectangle, width=1)

# Function for drawing the board based on what squares have been found so far
def drawSolvedBoard(window):
    global BOARD
    for rect in BOARD.tiles:
        if rect.found and rect.color == WHITE:
            pygame.draw.rect(window, rect.color, rect.rectangle)
        elif not rect.found and rect.color == WHITE:
            pygame.draw.rect(window, BLACK, rect.rectangle)
        else:
            pygame.draw.rect(window, rect.color, rect.rectangle)
        pygame.draw.rect(window, WHITE, rect.rectangle, width=1)

# Function for drawing the home screen
def drawHome(window):
    window.fill(BLACK)
    text = FONT.render("Click To Play", False, WHITE, None)
    rand = FONT.render(str(random.random()))
    window.blit(rand, (WIDTH/3.3, HEIGHT/2))
    window.blit(text, (WIDTH/3.3, HEIGHT/2.5))
    pygame.display.flip()

# Function for drawing the end screen which shows score
def drawEnd(window):
    gameOverText = FONT.render("Game Over!", False, WHITE, None)
    scoreText = FONT.render("Final score: " + str(LEVEL), False, WHITE, None)
    playAgainText = FONT.render("Click To Play Again!", False, WHITE, None)
    window.blit(gameOverText, (WIDTH/3.3, HEIGHT/3))
    window.blit(scoreText, (WIDTH/3.3, HEIGHT/2.5))
    window.blit(playAgainText, (WIDTH/6, HEIGHT/2))

# Event listener function for home screen
def listenHome():
    global NEWGAME, NEWROUND, BOARD, LEVEL
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            NEWGAME = False
            NEWROUND = True
            BOARD = createBoard(LEVEL)

# Event listener function for new round screen, no actions except quit
def listenNewRound():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

# Event listener function for main game loop
def listenGame():
    global BOARD, LIVES
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            coords = pygame.mouse.get_pos()
            for rect in BOARD.tiles:
                if rect.rectangle.collidepoint(coords) and rect.color == WHITE and not rect.found:
                    rect.found = True
                    CORRECT.play()
                elif rect.rectangle.collidepoint(coords) and rect.color == BLACK:
                    rect.color = RED
                    LIVES -= 1
                    WRONG.play()

# Event listener function for end game. Actions are quit and restart
def listenEnd():
    global NEWROUND, GAMEOVER, BOARD, LEVEL, LIVES, BOARDSIZE, WIDTH, TIMELEFT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            GAMEOVER = False
            NEWROUND = True
            BOARDSIZE = 3
            LEVEL = 0
            BOARD = createBoard(LEVEL)
            LIVES = 3
            TIMELEFT = WIDTH

def updateBoardSize(level):
    global BOARDSIZE
    if level%3 == 0:
        BOARDSIZE += 1

# Function for drawing a timer at the bottom of the screen as a yellow progress bar that depletes before tiles are
# hidden. Rate variable will be how quickly the progress bar is depleted
def drawTimer(window):
    global NEWROUND, GAME, TIMELEFT, LEVEL, BOARDSIZE
    TIMELEFT -= 10/((BOARDSIZE-1)+(LEVEL/5))
    pygame.draw.rect(window, YELLOW, (0, HEIGHT-10, TIMELEFT, 10))
    if TIMELEFT <= 0:
        NEWROUND = False
        GAME = True

# Function to check if all white tiles have been found to proceed to the next round
def checkAllFound():
    global NEWROUND, GAME, LEVEL, BOARD, LIVES, TIMELEFT, WIDTH
    flag = True
    for rect in BOARD.tiles:
        if rect.color == WHITE and rect.found == False:
            flag = False
    if flag:
        NEWROUND = True
        GAME = False
        LEVEL += 1
        updateBoardSize(LEVEL)
        BOARD = createBoard(LEVEL)
        TIMELEFT = WIDTH
        LIVES = 3

# Function to check if your lives have expired
def checkGameOver():
    global LIVES, GAME, GAMEOVER
    if LIVES <= 0:
        GAME = False
        GAMEOVER = True

async def main():
    seed = int(time.time())
    random.seed(seed)
    while True:
        while NEWGAME:
            CLOCK.tick(60)
            listenHome()
            drawHome(WINDOW)
            await asyncio.sleep(0)
        while NEWROUND:
            CLOCK.tick(60)
            listenNewRound()
            WINDOW.fill(BLACK)
            drawBoard(WINDOW)
            drawTimer(WINDOW)
            pygame.display.flip()
            await asyncio.sleep(0)
        while GAME:
            CLOCK.tick(60)
            listenGame()
            WINDOW.fill(BLACK)
            drawSolvedBoard(WINDOW)
            pygame.display.flip()
            checkAllFound()
            checkGameOver()
            await asyncio.sleep(0)
        while GAMEOVER:
            CLOCK.tick(60)
            listenEnd()
            WINDOW.fill(BLACK)
            drawEnd(WINDOW)
            pygame.display.flip()
            await asyncio.sleep(0)
    await asyncio.sleep(0)

asyncio.run(main())