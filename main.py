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
GRAY = (155, 155, 155)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
FONT = pygame.font.SysFont('Arial', 50, True, False)
PLAY_AGAIN_FONT = pygame.font.SysFont('Arial', 33, True, False)
NEWGAME = True
GAME = False
GAMEOVER = False
NEWROUND = False
ROUNDEND = False
BOARDSIZE = 3
BOARD = None
LEVEL = 0
LIVES = 3
TIMELEFT = WIDTH

PLAY_AGAIN = pygame.Rect(WIDTH/2-75, HEIGHT-100, 150, 50)

# Leaderboard stuff
INPUT_BOX = pygame.Rect(WIDTH/6, HEIGHT/1.5, 400, 50)
LEADERBOARD_TEXT = ""

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

# Function for end of game to show where the player missed white tiles. These tiles will be displayed in yellow
def drawMissedTiles(window):
    global BOARD
    for rect in BOARD.tiles:
        if not rect.found and rect.color == WHITE:
            pygame.draw.rect(window, YELLOW, rect.rectangle)

# Function for drawing the home screen
def drawHome(window):
    window.fill(BLACK)
    text = FONT.render("Click To Play", False, WHITE, None)
    window.blit(text, (WIDTH/3.3, HEIGHT/2.5))
    pygame.display.flip()

# Function for fetching top 3 scores from leaderboard.txt
# Best way to do this is to split the file on the newline character then for each line split on the colon to get pairs
# of players with their scores. Then we can sort and take the top 3 pairs and return them.
def getTop3():
    leaders = []
    dict = {}
    with open("leaderboard.txt", "r") as file:
        text = file.readlines()
        for line in text:
            temp = line.split(":")
            name = temp[0].replace(":", "")
            score = int(temp[1])
            dict[name] = score
    top_3 = sorted(dict.items(), key=lambda x: x[1], reverse=True)[:3]
    for x in top_3:
        leaders.append(x[0] + ": " + str(x[1]))
    return leaders

# Function for drawing the end screen which shows score
def drawEnd(window):
    global LEADERBOARD_TEXT, INPUT_BOX, PLAY_AGAIN, PLAY_AGAIN_FONT
    coords = pygame.mouse.get_pos()
    leaders = getTop3()
    leader1 = None
    leader2 = None
    leader3 = None
    top3 = FONT.render("Top 3", False, (0, 255, 0), None)
    play_again = PLAY_AGAIN_FONT.render("Play Again", False, BLACK, None)
    if len(leaders) > 0:
        leader1 = FONT.render(leaders[0], False, WHITE, None)
    if len(leaders) > 1:
        leader2 = FONT.render(leaders[1], False, WHITE, None)
    if len(leaders) > 2:
        leader3 = FONT.render(leaders[2], False, WHITE, None)
    gameOverText = FONT.render("Game Over!", False, WHITE, None)
    scoreText = FONT.render("Final score: " + str(LEVEL), False, WHITE, None)
    enterName = FONT.render("Enter Name:", False, WHITE, None)
    pygame.draw.rect(window, WHITE, INPUT_BOX, 2)
    if PLAY_AGAIN.collidepoint(coords):
        pygame.draw.rect(window, GRAY, PLAY_AGAIN)
    else:
        pygame.draw.rect(window, WHITE, PLAY_AGAIN)
    leaderboard_text = FONT.render(LEADERBOARD_TEXT, True, (255, 255, 255))
    window.blit(leaderboard_text, (INPUT_BOX.x + 5, INPUT_BOX.y))
    window.blit(gameOverText, (WIDTH/3.3, HEIGHT/3))
    window.blit(scoreText, (WIDTH/3.3, HEIGHT/2.4))
    window.blit(enterName, (WIDTH/3.3, HEIGHT/2))
    window.blit(play_again, (PLAY_AGAIN.x + 5, PLAY_AGAIN.y))
    if leader1:
        window.blit(leader1, (5, 50))
    if leader2:
        window.blit(leader2, (5, 100))
    if leader3:
        window.blit(leader3, (5, 150))
    window.blit(top3, (5, 1))

# Event listener function for home screen
def listenHome():
    global NEWGAME, NEWROUND, BOARD, LEVEL
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
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
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            if event.type == pygame.FINGERDOWN:
                coords = (event.x, event.y)
            else:
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
    global NEWROUND, GAMEOVER, BOARD, LEVEL, LIVES, BOARDSIZE, WIDTH, TIMELEFT, LEADERBOARD_TEXT, PLAY_AGAIN
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            if event.type == pygame.FINGERDOWN:
                coords = (event.x, event.y)
            else:
                coords = pygame.mouse.get_pos()
            if PLAY_AGAIN.collidepoint(coords):
                GAMEOVER = False
                NEWROUND = True
                BOARDSIZE = 3
                LEVEL = 0
                BOARD = createBoard(LEVEL)
                LIVES = 3
                TIMELEFT = WIDTH
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(LEADERBOARD_TEXT) > 0:
                # Save the text to file
                with open("leaderboard.txt", "a") as file:
                    file.write(LEADERBOARD_TEXT + ": " + str(LEVEL) + "\n")
                # Reset the input box
                LEADERBOARD_TEXT = ""
                GAMEOVER = False
                NEWROUND = True
                BOARDSIZE = 3
                LEVEL = 0
                BOARD = createBoard(LEVEL)
                LIVES = 3
                TIMELEFT = WIDTH
            elif event.key == pygame.K_BACKSPACE:
                LEADERBOARD_TEXT = LEADERBOARD_TEXT[:-1]
            else:
                if len(LEADERBOARD_TEXT) < 16:
                    LEADERBOARD_TEXT += event.unicode

def updateBoardSize(level):
    global BOARDSIZE
    if level % 3 == 0:
        BOARDSIZE += 1

# Function for drawing a timer at the bottom of the screen as a yellow progress bar that depletes before tiles are
# hidden. Rate variable will be how quickly the progress bar is depleted
def drawTimer(window):
    global NEWROUND, GAME, TIMELEFT, LEVEL, BOARDSIZE, ROUNDEND, GAMEOVER
    TIMELEFT -= 10/((BOARDSIZE-1)+(LEVEL/5))
    pygame.draw.rect(window, YELLOW, (0, HEIGHT-10, TIMELEFT, 10))
    if TIMELEFT <= 0 and ROUNDEND:
        ROUNDEND = False
        GAMEOVER = True
    elif TIMELEFT <= 0:
        NEWROUND = False
        GAME = True


# Function to check if all white tiles have been found to proceed to the next round
def checkAllFound():
    global NEWROUND, GAME, LEVEL, BOARD, LIVES, TIMELEFT, WIDTH
    flag = True
    for rect in BOARD.tiles:
        if rect.color == WHITE and not rect.found:
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
    global LIVES, GAME, ROUNDEND, TIMELEFT, WIDTH
    if LIVES <= 0:
        GAME = False
        ROUNDEND = True
        TIMELEFT = WIDTH

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
        while ROUNDEND:
            CLOCK.tick(60)
            listenNewRound()
            WINDOW.fill(BLACK)
            drawSolvedBoard(WINDOW)
            drawMissedTiles(WINDOW)
            drawTimer(WINDOW)
            pygame.display.flip()
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