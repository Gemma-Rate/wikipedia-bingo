"""Wikipedia Bingo code"""

import sys
from collections import Counter

import numpy as np
import pandas as pd

import pygame
import pygame.locals as loc

from pygame_textinput import TextInput

from validate_numbers import Validation

from word_generation import TargetWord, get_word_list


# Create the constants (go ahead and experiment with different values)
BOARDWIDTH = 3  # number of columns in the board
BOARDHEIGHT = 3  # number of rows in the board
TILESIZE = 80
TILE_WIDTH = 200
TILE_HEIGHT = 80
WINDOWWIDTH = 1600
WINDOWHEIGHT = 600
FPS = 30
BLANK = None

# Colours (R, G, B)
BLACK = (78, 0, 105)
WHITE = (255, 255, 255)
LIGHTBLUE = (207, 228, 255)
GREEN = (117, 213, 148)

BGCOLOR = LIGHTBLUE
TILECOLOR = GREEN
TEXTCOLOR = BLACK
BORDERCOLOR = BLACK
BUTTONCOLOR = BLACK
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = BLACK

BASICFONTSIZE = 20
BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

XMARGIN = int((WINDOWWIDTH - (TILE_WIDTH * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILE_HEIGHT * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

ALL_WORDS = get_word_list('no_stop_g2.txt')


def make_text(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    surface = BASICFONT.render(text, True, color, bgcolor)
    rect = surface.get_rect()
    rect.topleft = (top, left)
    return (surface, rect)


class Button():
    def __init__(self, text, text_color, back_color, x, y):
        self.surface, self.rect = make_text(text, text_color, back_color, x, y)


class Game():
    """The class to hold the game instance."""
    def __init__(self):
        # Create the clock
        self.clock = pygame.time.Clock()

        # Create the game board
        self.window = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Unnamed Wiki Bingo game (not WikiBingo)')

        # Create the option buttons and their rectangles
        self.buttons = {}
        # Quit button
        self.buttons['quit'] = Button('QUIT', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, 30)
        self.buttons['quit'].action = self.terminate

        # Generate a new puzzle
        self.get_starting_board()

        # Create list of red tiles
        self.board_counts = np.zeros((BOARDWIDTH, BOARDHEIGHT))

        # Create TextInput-object
        self.textinput = TextInput(text_color=TEXTCOLOR, cursor_color=TEXTCOLOR)

        # Create the message array (starts blank)
        self.message_array = None

        # Initial score.
        self.score = 0

    def run(self):
        """Run the game until it quits."""

        # Draw the initial board
        self.draw_board()

        # Main game loop
        while True:
            # Get events
            events = pygame.event.get()

            # Check clicks
            for event in events:
                if event.type == loc.MOUSEBUTTONUP:
                    # check if the user clicked on an option button
                    for button_name in self.buttons:
                        button = self.buttons[button_name]
                        if button.rect.collidepoint(event.pos):
                            button.action()

            # Send events to the text reader
            if self.textinput.update(events):
                # Pressed enter
                user_input = self.textinput.get_text()
                self.textinput.clear_text()

                # Extra commands
                if user_input and user_input[0] == "\ "[0]:
                    command = user_input[1:].lower()
                    if command in ['q', 'quit']:
                        self.terminate()
                else:
                    # Get the wikipedia article
                    validation = Validation(user_input)
                    try:
                        validation.scrape_wiki()
                        validation.process_wiki()
                        words = validation.token
                        self.score += 1
                        print(self.score)
                    except Exception:
                        print('Article not found')
                        words = []
                        self.score += 1
                        print(self.score)

                    # Remove any words not on the board
                    words = [word.lower()
                             for word in words
                             if word.lower() in self.board_words.flatten()]

                    # Count the frequencies
                    counter = Counter(words)

                    # Create the message for the top left
                    self.message_array = [user_input + ':']
                    for word in sorted(counter, key=lambda x: counter[x], reverse=True):
                        x, y = tuple(np.argwhere(self.board_words == word.lower())[0])
                        current_count = self.board_counts[x][y]
                        limit = self.board_limits[x][y]
                        new_count = current_count + counter[word]

                        # Create the message array for the left hand courner
                        message = '{} ({:.0f})+{:.0f} = {:.0f}/{:.0f}'.format(word,
                                                                              current_count,
                                                                              counter[word],
                                                                              new_count,
                                                                              limit)
                        self.message_array.append(message)

                        # Check if the counter has overflowed
                        new_word = None
                        new_range = None
                        if new_count >= limit:
                            new_count = 0
                            new_word, new_range = self.get_new_word()
                            self.message_array.append('  OVERFLOW > {}'.format(new_word))

                        # Save the new count, new word (if needed) and message
                        self.board_counts[x][y] = new_count
                        if new_word:
                            self.board_words[x][y] = new_word
                            self.board_limits[x][y] = new_range

            # Check for exit
            self.check_for_quit(events)

            # Draw the board
            self.draw_board()

            # Tick the FPS clock
            self.clock.tick(FPS)

            # exit if won
            if self.game_won():
                pygame.time.wait(10000)
                self.terminate()

    def terminate(self):
        pygame.quit()
        sys.exit()

    def check_for_quit(self, events):
        for event in events:
            if event.type == loc.QUIT:
                # terminate if any QUIT events are present
                self.terminate()
            if event.type == loc.KEYUP and event.key == loc.K_ESCAPE:
                # terminate if the KEYUP event was for the Esc key
                self.terminate()

    def get_starting_board(self):
        """Return a board data structure with tiles in the solved state."""
        words = []
        ranges = []
        for i in range(BOARDWIDTH * BOARDHEIGHT):
            word, limit = self.get_new_word()
            words.append(word)
            ranges.append(limit)
        self.board_words = np.array(words).reshape((BOARDWIDTH, BOARDHEIGHT))
        self.board_limits = np.array(ranges).reshape((BOARDWIDTH, BOARDHEIGHT))

    def get_new_word(self):
        """Get an unused word from the list of all words."""
        while True:
            target = TargetWord(ALL_WORDS)
            target.word_gen()
            word = target.word.lower()
            target.range_gen()
            limit = 7  # target.upper

            try:
                if word not in self.board_words.flatten():
                    break
            except Exception:
                break

        return word, limit

    def get_tile_courner(self, tileX, tileY):
        left = XMARGIN + (tileX * TILE_WIDTH) + (tileX - 1)
        top = YMARGIN + (tileY * TILE_HEIGHT) + (tileY - 1)
        return (left, top)

    def draw_board(self):
        self.window.fill(BGCOLOR)
        # Draw the board
        for tilex in range(len(self.board_words)):
            for tiley in range(len(self.board_words[0])):
                word = self.board_words[tilex][tiley]
                count = self.board_counts[tilex][tiley]
                limit = self.board_limits[tilex][tiley]
                if 0 < count < limit:
                    colour = (255, 255 - count * 255 / limit, 255 - count * 255 / limit)
                else:
                    colour = GREEN
                self.draw_tile(tilex, tiley, word, count, limit, colour)

        left, top = self.get_tile_courner(0, 0)
        width = BOARDWIDTH * TILE_WIDTH
        height = BOARDHEIGHT * TILE_HEIGHT
        pygame.draw.rect(self.window, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

        # Draw the message
        if self.message_array:
            for i, msg in enumerate(self.message_array):
                textSurf, textRect = make_text(msg, MESSAGECOLOR, BGCOLOR, 5, 5 + 20 * i)
                self.window.blit(textSurf, textRect)

        # Draw the winning message if you've won
        if self.game_won():

            name = 'tst' # Put input from user here!
            new_win = pd.DataFrame(columns=['score', 'name'])
            new_win.loc[0] = [self.score, name]
            leaderboard = pd.read_csv('leaderboard.csv')
            new_leaderboard = pd.concat([leaderboard, new_win])
            new_leaderboard = new_leaderboard.sort_values('score')
            new_leaderboard.to_csv('leaderboard.csv', index=False)
            # Update the leaderboard.

            textSurf, textRect = make_text('!! WINNER !!',
                                           MESSAGECOLOR, BGCOLOR,
                                           WINDOWWIDTH - 650, 5)
            self.window.blit(textSurf, textRect)

        # Draw the instructions
        instruct = 'type a word, type \quit to exit:'
        instructSurf, instructRect = make_text(instruct,
                                               MESSAGECOLOR, BGCOLOR,
                                               5, WINDOWHEIGHT - 60)
        self.window.blit(instructSurf, instructRect)

        # Draw the text box
        self.window.blit(self.textinput.get_surface(), (5, WINDOWHEIGHT - 30))

        # Draw the buttons
        for button_name in self.buttons:
            button = self.buttons[button_name]
            self.window.blit(button.surface, button.rect)

        # Update the dipslay
        pygame.display.update()

    def draw_tile(self, tilex, tiley, word, count, limit, colour=TILECOLOR):
        """draw a tile at board coordinates tilex and tiley, optionally a few
        pixels over (determined by adjx and adjy)"""
        left, top = self.get_tile_courner(tilex, tiley)
        pygame.draw.rect(self.window, colour, (left, top, TILE_WIDTH, TILE_HEIGHT))

        textSurf = BASICFONT.render(str(word), True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.center = (left + int(TILE_WIDTH / 2), top + int(TILE_HEIGHT / 2))
        self.window.blit(textSurf, textRect)

        countSurf = BASICFONT.render('{:.0f}/{:.0f}'.format(count, limit), True, TEXTCOLOR)
        countRect = countSurf.get_rect()
        countRect.center = (left + int(TILE_WIDTH / 2) + 75, top + int(TILE_HEIGHT / 2) + 20)
        self.window.blit(countSurf, countRect)

    def game_won(self):
        """Determine if anyone has won the game."""
        won = False

        # check for winning rows
        for row in self.board_counts:
            if all(row > 0):
                won = True

        # check for winning columns
        for col in self.board_counts.T:
            if all(col > 0):
                won = True

        return won


def main():
    """The main process."""
    # Initilise PyGame
    pygame.init()

    # Create a game instance
    game = Game()

    # Run the game
    game.run()


if __name__ == '__main__':
    main()
