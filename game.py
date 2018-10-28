"""Wikipedia Bingo code."""

import sys
from collections import Counter

import numpy as np


import pygame
import pygame.locals as loc

from pygame_textinput import TextInput

from validate_numbers import Validation

from word_generation import TargetWord, get_word_list


# Create the constants (go ahead and experiment with different values)
BOARDSIZE = 1
TILESIZE = 80
TILE_WIDTH = 200
TILE_HEIGHT = 80
WINDOWWIDTH = 1900
WINDOWHEIGHT = 800
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

XMARGIN = int((WINDOWWIDTH - (TILE_WIDTH * BOARDSIZE + (BOARDSIZE - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILE_HEIGHT * BOARDSIZE + (BOARDSIZE - 1))) / 2)

ALL_WORDS = get_word_list('no_stop_g2.txt')


def make_text(text, color, bgcolor, top, left):
    """Create the Surface and Rect objects for some text."""
    surface = BASICFONT.render(text, True, color, bgcolor)
    rect = surface.get_rect()
    rect.topleft = (top, left)
    return (surface, rect)


class Button(object):
    """A button object."""

    def __init__(self, text, text_color, back_color, x, y):
        self.surface, self.rect = make_text(text, text_color, back_color, x, y)


class Game(object):
    """The game instance."""

    def __init__(self):
        # Create the clock
        self.clock = pygame.time.Clock()

        # Create the game window
        self.window = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Unnamed Wiki Bingo game (not WikiBingo)')

    def run(self):
        """Run the game until it quits."""
        self.running = True
        while self.running:
            # Display the start screen
            self.start_screen()
            # Start screen quit

            # Display the main screen
            self.main_screen()
            # Main screen quit

        # Exit
        self.terminate()

    def start_screen(self):
        """Create the start screen."""
        self.loop_stage = True

        # Define buttons
        self.buttons = {}
        self.buttons['start'] = Button('START',
                                       TEXTCOLOR, TILECOLOR,
                                       WINDOWWIDTH / 2 - 100, WINDOWHEIGHT - 100)
        self.buttons['start'].action = self.next_stage

        self.buttons['quit'] = Button('QUIT',
                                      TEXTCOLOR, TILECOLOR,
                                      WINDOWWIDTH / 2 + 50, WINDOWHEIGHT - 100)
        self.buttons['quit'].action = self.terminate

        while self.loop_stage:
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

            # Check for exit
            self.check_for_quit(events)

            # Draw the board
            self.draw_start_screen()

            # Tick the FPS clock
            self.clock.tick(FPS)

    def draw_start_screen(self):
        """Draw the start screen."""
        self.window.fill(BGCOLOR)
        # Draw the name
        instruct = 'Wikipedia Bingo (not affiliated with WikiBingo)'
        instructSurf, instructRect = make_text(instruct,
                                               MESSAGECOLOR, BGCOLOR,
                                               500, 60)
        self.window.blit(instructSurf, instructRect)

        # Draw the buttons
        for button_name in self.buttons:
            button = self.buttons[button_name]
            self.window.blit(button.surface, button.rect)

        # Update the dipslay
        pygame.display.update()

    def main_screen(self):
        """Create the main screen."""
        self.loop_stage = True

        # Generate a new puzzle
        self.get_starting_board()

        # Create list of red tiles
        self.board_counts = np.zeros((BOARDSIZE, BOARDSIZE))

        # Quit button
        self.buttons = {}
        self.buttons['restart'] = Button('RESTART', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 150, 30)
        self.buttons['restart'].action = self.next_stage
        self.buttons['quit'] = Button('QUIT', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 150, 60)
        self.buttons['quit'].action = self.terminate

        # Create TextInput-object
        self.textinput = TextInput(text_color=TEXTCOLOR, cursor_color=TEXTCOLOR)

        # Create the message array (starts blank)
        self.message_array = None

        # Draw the initial board
        self.draw_main_screen()

        while self.loop_stage:
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
                    # DEBUG
                    print(self.board_words)

                    # Put the title in the top left
                    self.message_array = [user_input + ':']

                    # Get the wikipedia article
                    validation = Validation(user_input)
                    try:
                        validation.scrape_wiki()
                        validation.process_wiki()
                        words = validation.token
                    except Exception:
                        self.message_array.append('Article not found')
                        words = []

                    # Remove any words not on the board
                    words = [word.lower()
                             for word in words
                             if word.lower() in self.board_words.flatten()]

                    # Count the frequencies
                    counter = Counter(words)

                    # Create the message for the top left
                    if len(words) == 0:
                        self.message_array.append('No valid words')

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
                            print(new_word)
                            self.board_words[x][y] = new_word
                            self.board_limits[x][y] = new_range

            # Check for exit
            self.check_for_quit(events)

            # Draw the board
            self.draw_main_screen()

            # Tick the FPS clock
            self.clock.tick(FPS)

            # Exit if won
            if self.game_won():
                pygame.time.wait(5000)
                return

    def draw_main_screen(self):
        """Draw the main screen."""
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
        width = BOARDSIZE * TILE_WIDTH
        height = BOARDSIZE * TILE_HEIGHT
        pygame.draw.rect(self.window, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

        # Draw the message
        if self.message_array:
            for i, msg in enumerate(self.message_array):
                textSurf, textRect = make_text(msg, MESSAGECOLOR, BGCOLOR, 5, 5 + 20 * i)
                self.window.blit(textSurf, textRect)

        # Draw the winning message if you've won
        if self.game_won():
            textSurf, textRect = make_text('!! WINNER !!',
                                           MESSAGECOLOR, BGCOLOR,
                                           WINDOWWIDTH / 2 - 75, 5)
            self.window.blit(textSurf, textRect)

        # Draw the instructions
        instruct = 'Enter the name of a Wikipedia article:'
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

    def next_stage(self):
        """Go to the next stage."""
        self.loop_stage = False

    def terminate(self):
        """Quit the game."""
        pygame.quit()
        sys.exit()

    def check_for_quit(self, events):
        """Check for quit events."""
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
        for _ in range(BOARDSIZE * BOARDSIZE):
            word, limit = self.get_new_word()
            words.append(word)
            ranges.append(limit)
        self.board_words = np.array(words, dtype=object).reshape((BOARDSIZE, BOARDSIZE))
        self.board_limits = np.array(ranges).reshape((BOARDSIZE, BOARDSIZE))

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

    def get_tile_courner(self, tilex, tiley):
        """Get the coordinates of the top left courner of a tile."""
        left = XMARGIN + (tilex * TILE_WIDTH) + (tilex - 1)
        top = YMARGIN + (tiley * TILE_HEIGHT) + (tiley - 1)
        return (left, top)

    def draw_tile(self, tilex, tiley, word, count, limit, colour=TILECOLOR):
        """Draw a tile at board coordinates tilex and tiley."""
        left, top = self.get_tile_courner(tilex, tiley)
        pygame.draw.rect(self.window, colour, (left, top, TILE_WIDTH, TILE_HEIGHT))

        text_surf = BASICFONT.render(str(word), True, TEXTCOLOR)
        text_rect = text_surf.get_rect()
        text_rect.center = (left + int(TILE_WIDTH / 2), top + int(TILE_HEIGHT / 2))
        self.window.blit(text_surf, text_rect)

        count_surf = BASICFONT.render('{:.0f}/{:.0f}'.format(count, limit), True, TEXTCOLOR)
        count_rect = count_surf.get_rect()
        count_rect.center = (left + int(TILE_WIDTH / 2) + 75, top + int(TILE_HEIGHT / 2) + 20)
        self.window.blit(count_surf, count_rect)

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
    """Run the main process."""
    # Initilise PyGame
    pygame.init()

    # Create a game instance
    game = Game()

    # Run the game
    game.run()


if __name__ == '__main__':
    main()
