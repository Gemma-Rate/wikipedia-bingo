# The main game window

import random
import sys
import numpy as np

from collections import Counter

import pygame
from pygame.locals import *
import pygame_textinput

# Create the constants (go ahead and experiment with different values)
BOARDWIDTH = 4  # number of columns in the board
BOARDHEIGHT = 4  # number of rows in the board
TILESIZE = 80
TILE_WIDTH = 200
TILE_HEIGHT = 80
WINDOWWIDTH = 1200
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

# R    G    B
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILE_WIDTH * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILE_HEIGHT * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

ALL_WORDS = list('qwertyuiopasdfghjklzxcvbn'.upper())


def main():
    """The main process."""

    # Initilise PyGame
    pygame.init()

    # Create the clock
    global FPSCLOCK
    FPSCLOCK = pygame.time.Clock()

    # Create the game board
    global WINDOW, BASICFONT
    WINDOW = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Unnamed Wiki Bingo game (not WikiBingo)')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Create the option buttons and their rectangles
    # Quit button
    global QUIT_SURF, QUIT_RECT
    QUIT_SURF, QUIT_RECT = makeText('QUIT', TEXTCOLOR, TILECOLOR,
                                     WINDOWWIDTH - 120, 30)

    # Generate a new puzzle
    board_words = get_starting_board()

    # Create list of red tiles
    board_counts = np.zeros((BOARDWIDTH, BOARDHEIGHT))

    # Create TextInput-object
    textinput = pygame_textinput.TextInput(text_color=TEXTCOLOR,
                                             cursor_color=TEXTCOLOR,)

    # Draw the board
    message_array = None
    draw_board(board_words, board_counts, textinput, message_array)
    pygame.display.update()

    # Main game loop
    while True:
        # event handling loop
        events = pygame.event.get()
        for event in events:
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(board_words, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if the user clicked on an option button
                    if QUIT_RECT.collidepoint(event.pos):
                        terminate()
                else:
                    # Clicked on a tile
                    #redtile = (spotx, spoty)
                    pass


        # Feed it with events every frame
        if textinput.update(events):
            # Pressed enter
            user_input = textinput.get_text()
            textinput.clear_text()

            # Extra commands
            if user_input and user_input[0] == "\ "[0]:
                command = user_input[1:]
                if command.lower() in ['q', 'quit']:
                    terminate()
            else:
                # parse all input "words"
                words = list(user_input)

                # Remove any words not on the board
                words = [word.upper() for word in words if word.upper() in board_words.flatten()]

                # Count the frequencies
                counter = Counter(words)
                #message_array = ['{} +{:.0f}'.format(k, j) for k, j in counts]

                message_array = []
                for word in sorted(counter, key=lambda x: counter[x], reverse=True):
                    x, y = tuple(np.argwhere(board_words == word.upper())[0])
                    current_count = board_counts[x][y]
                    new_count = current_count + counter[word]

                    # Create the message array for the left hand courner
                    message = '{} ({:.0f})+{:.0f} = {:.0f}'.format(word,
                                                                   current_count,
                                                                   counter[word],
                                                                   new_count)
                    message_array.append(message)

                    # Check if the counter has overflowed
                    new_word = None
                    if new_count > 3:
                        new_count = 0
                        new_word = get_new_word(board_words)
                        message_array.append('  OVERFLOW > {}'.format(new_word))

                    # Save the new count, new word (if needed) and message
                    board_counts[x][y] = new_count
                    if new_word:
                        board_words[x][y] = new_word

        # Draw the board
        draw_board(board_words, board_counts, textinput, message_array)

        # Check for exit
        check_for_quit()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

        # exit if won
        if game_won(board_counts):
            pygame.time.wait(1500)
            terminate()


def terminate():
    pygame.quit()
    sys.exit()


def check_for_quit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def get_starting_board():
    """Return a board data structure with tiles in the solved state."""
    words = random.sample(ALL_WORDS, BOARDWIDTH*BOARDHEIGHT)
    board_words = np.array(words).reshape((BOARDWIDTH, BOARDHEIGHT))
    return board_words


def get_new_word(board_words):
    """Get an unused word from the list of all words."""
    used_words = set(board_words.flatten())
    all_words = set(ALL_WORDS)
    unused_words = all_words - used_words
    return random.choice(list(unused_words))


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILE_WIDTH) + (tileX - 1)
    top = YMARGIN + (tileY * TILE_HEIGHT) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    # from the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILE_WIDTH, TILE_WIDTH)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def draw_board(board_words, board_counts, textinput, message_array=None):
    WINDOW.fill(BGCOLOR)
    # Draw the board
    for tilex in range(len(board_words)):
        for tiley in range(len(board_words[0])):
            word = board_words[tilex][tiley]
            count = board_counts[tilex][tiley]
            if 0 < count:
                colour = (255, 255 - count * 255 / 3, 255 - count * 255 / 3)
            else:
                colour = GREEN
            draw_tile(tilex, tiley, word, count, colour)

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILE_WIDTH
    height = BOARDHEIGHT * TILE_HEIGHT
    pygame.draw.rect(WINDOW, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    # Draw the message
    if message_array:
        for i, msg in enumerate(message_array):
            textSurf, textRect = makeText(msg, MESSAGECOLOR, BGCOLOR, 5, 5 + 20*i)
            WINDOW.blit(textSurf, textRect)

    # Draw the winning message if you've won
    if game_won(board_counts):
        textSurf, textRect = makeText('!! WINNER !!', MESSAGECOLOR, BGCOLOR, WINDOWWIDTH - 650, 5)
        WINDOW.blit(textSurf, textRect)

    # Draw the instructions
    instruct = 'type a word, type \quit to exit:'
    instructSurf, instructRect = makeText(instruct, MESSAGECOLOR, BGCOLOR, 5, WINDOWHEIGHT - 60)
    WINDOW.blit(instructSurf, instructRect)

    # Draw the text box
    WINDOW.blit(textinput.get_surface(), (5, WINDOWHEIGHT - 30))

    # Draw the quit button
    WINDOW.blit(QUIT_SURF, QUIT_RECT)


def draw_tile(tilex, tiley, word, count, colour=TILECOLOR):
    """draw a tile at board coordinates tilex and tiley, optionally a few
    pixels over (determined by adjx and adjy)"""
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(WINDOW, colour, (left, top, TILE_WIDTH, TILE_HEIGHT))

    textSurf = BASICFONT.render(str(word), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = (left + int(TILE_WIDTH / 2), top + int(TILE_HEIGHT / 2))
    WINDOW.blit(textSurf, textRect)

    countSurf = BASICFONT.render('{:.0f}'.format(count), True, TEXTCOLOR)
    countRect = countSurf.get_rect()
    countRect.center = (left + int(TILE_WIDTH / 2) + 80, top + int(TILE_HEIGHT / 2) + 20)
    WINDOW.blit(countSurf, countRect)


def game_won(board_counts):
    """Determine if anyone has won the game."""
    won = False

    # check for winning rows
    for row in board_counts:
        if all(row > 0):
            won = True

    # check for winning columns
    for col in board_counts.T:
        if all(col > 0):
            won = True

    return won


if __name__ == '__main__':
    main()
