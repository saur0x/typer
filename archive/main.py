"""
colorama:
    pip install pynput
    https://pypi.org/project/colorama/

pynput:
    pip install colorama
    https://pypi.org/project/pynput/
"""
import os
import time
import re
import threading
import sys
import random
from pynput import keyboard


# import colorama
# colorama.init()


class ANSI:
    bold = u"\u001b[1m"
    underline = u"\u001b[4m"

    reset = u"\u001b[0m"

    clear = "\033[H\033[2J"

    black = u"\u001b[30m"
    red = u"\u001b[31m"
    green = u"\u001b[32m"
    yellow = u"\u001b[33m"
    blue = u"\u001b[34m"
    magenta = u"\u001b[35m"
    cyan = u"\u001b[36m"
    white = u"\u001b[37m"

    bright_black = u"\u001b[30;1m"
    bright_red = u"\u001b[31;1m"
    bright_green = u"\u001b[32;1m"
    bright_yellow = u"\u001b[33;1m"
    bright_blue = u"\u001b[34;1m"
    bright_magenta = u"\u001b[35;1m"
    bright_cyan = u"\u001b[36;1m"
    bright_white = u"\u001b[37;1m"

    background_black = u"\u001b[40m"
    background_red = u"\u001b[41m"
    background_green = u"\u001b[42m"
    background_yellow = u"\u001b[43m"
    background_blue = u"\u001b[44m"
    background_magenta = u"\u001b[45m"
    background_cyan = u"\u001b[46m"
    background_white = u"\u001b[47m"

    background_bright_black = u"\u001b[40;1m"
    background_bright_red = u"\u001b[41;1m"
    background_bright_green = u"\u001b[42;1m"
    background_bright_yellow = u"\u001b[43;1m"
    background_bright_blue = u"\u001b[44;1m"
    background_bright_magenta = u"\u001b[45;1m"
    background_bright_cyan = u"\u001b[46;1m"
    background_bright_white = u"\u001b[47;1m"

    up = u"\u001b[1A"
    down = u"\u001b[1B"
    right = u"\u001b[1C"
    left = u"\u001b[1D"

    @classmethod
    def color(cls, r=0, g=0, b=0):
        """Generate ANSI foreground color from `r, g, b` values.
        """
        return f"\033[38;2;{r};{g};{b}m"

    @classmethod
    def background_color(cls, r=0, g=0, b=0):
        """Generate ANSI background color from `r, g, b` values.
        """
        return f"\033[48;2;{r};{g};{b}m"

    @classmethod
    def clear_screen(cls, mode=2):
        """Clear multiple lines.
        n=0 clears from cursor until end of screen,
        n=1 clears from cursor to beginning of screen
        n=2 clears entire screen
        """
        return u"\u001b[{}J".format(mode)

    @classmethod
    def clear_line(cls, mode=2):
        """Clears current line.
        n=0 clears from cursor to end of line
        n=1 clears from cursor to start of line
        n=2 clears entire line
        """
        return u"\u001b[{}K".format(mode)


class Typer:
    def __init__(self, text=None, duration=60):
        self.text = text

        self.split_regex = re.compile(r"[\s\n\t]")

        self.pointer = 0

        # Current word that the pointer is on
        self.word = ''

        # Timing variables
        self.init_time = None
        self.duration = duration
        self.time_remaining = self.duration
        self.time_elapsed = 0.0

        # Metric variables
        self.accuracy = 100
        self.wpm = 0.0
        self.net_wpm = 0.0
        self.cpm = 0.0
        self.cps = 0.0
        self.errors = 0

        self.error_pointers = []

        # Different `Typer` states
        self.parsing = False
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True
        self.init_time = time.time()

    def clear_screen(self):
        sys.stdout.write(ANSI.clear)

    def show_info(self):
        """Shows typer metrics.
        """
        separator = " "
        padding = " | "
        rjust = 5

        info = (
            "Time"
            + separator
            + str(self.time_remaining).rjust(6, ' ')
            + padding
            + "Accuracy"
            + separator
            + str(self.accuracy).rjust(3, ' ')
            + padding
            + "WPM"
            + separator
            + str(self.wpm).rjust(rjust, ' ')
            + padding
            + "Net WPM"
            + separator
            + str(self.net_wpm).rjust(rjust, ' ')
            + padding
            + "CPS"
            + separator
            + str(self.cps).rjust(rjust, ' ')
            + padding
            + "Errors"
            + separator
            + f"{self.errors} / {self.pointer}".rjust(9, ' ')
        )

        sys.stdout.write(ANSI.background_red + ANSI.bold + ANSI.white + info + 500 * (' ' + ANSI.left + ANSI.right) + ANSI.reset)

    def show_text(self):
        pointer_passed = False
        buf = ''

        for i, j in enumerate(self.text):
            # Show wrong input characters as different colored
            if i in self.error_pointers:
                buf += ANSI.red

                # Show a colored underscore / underline
                # for unprintable characters.
                match = self.split_regex.fullmatch(j)
                if match is not None:
                    buf += ANSI.underline

            # Underline the char that the pointer is currently on
            elif i == self.pointer:
                pointer_passed = True
                buf += ANSI.bold + ANSI.underline + ANSI.green + ANSI.background_black

            # Make untyped chars bold
            if pointer_passed:
                buf += ANSI.bold
            buf += j + ANSI.reset
        sys.stdout.write(buf)

    def show_separator(self, repeat=1):
        """Print a separator to separate different parts of the `Typer`.
        """
        sys.stdout.write('\n' * repeat)

    def show_prompt(self):
        """Show progress for the word that the pointer is currently on.
        """
        sys.stdout.write(f"> {self.word}")

    # Parsing user input
    def parse_backspace(self, key_char):
        """Handles `backspace` as user input.
        """
        self.pointer = max(1, self.pointer - 1)
        if self.pointer in self.error_pointers:
            self.error_pointers.remove(self.pointer)
        self.word = self.word[:-1]

    def parse_error(self):
        """Handles user input when the wrong character is entered.
        """
        if self.pointer not in self.error_pointers:
            self.error_pointers.append(self.pointer)

    def parse_input(self, key_char):
        """Parses user input for different cases,
        e.g., `backspace`, `error`, and correct input.
        """
        current_char = self.text[self.pointer]

        # Handling backspace
        if key_char == '\b':
            self.parse_backspace(key_char)
            return

        if key_char != current_char:
            self.parse_error()

        self.pointer += 1
        self.word += key_char

        # Updating word
        match = self.split_regex.fullmatch(key_char)
        if match is not None:
            self.word = ''

    def update(self):
        """Updates `info` of `Typer`.
        """
        current_time = time.time()
        self.errors = len(self.error_pointers)

        self.time_elapsed = round(current_time - self.init_time, 2)
        self.time_remaining = round(self.duration - self.time_elapsed, 2)

        if self.pointer:
            self.accuracy = (
                self.pointer - len(self.error_pointers)) * 100 // self.pointer
        else:
            self.accuracy = 100

        if self.time_elapsed:
            self.wpm = round(self.pointer * 60 / (5 * self.time_elapsed), 2)
            self.net_wpm = round((self.pointer - self.errors) * 60 / (
                5 * self.time_elapsed), 2)
            self.cpm = round(self.pointer * 60 / self.time_elapsed, 2)
            self.cps = round(self.pointer / self.time_elapsed, 2)
        else:
            self.wpm = 0.0
            self.net_wpm = 0.0
            self.cpm = 0.0
            self.cps = 0.0

    def check_end(self):
        """Checks if typing is finished.
        """
        return self.time_remaining <= 0 or self.pointer >= len(self.text) - 1

    def show_end(self):
        """Shows end message after `Typer` is finished.
        """
        self.stopped = True
        self.clear_screen()
        self.show_info()
        self.show_separator(2)
        self.show_text()
        self.show_separator(1)
        # colorama.deinit()
        sys.exit(0)


def updater(blocking=True):
    # Threading used for continuously updating typer info.
    while not typer.stopped:
        if typer.check_end():
            typer.show_end()
            return False

        # Don't update `info` if `Typer` is not yet started
        if typer.started:
            typer.update()

        typer.clear_screen()
        typer.show_info()
        typer.show_separator(2)
        typer.show_text()
        typer.show_separator(2)
        typer.show_prompt()
        typer.show_separator(1)
        # sys.stdout.flush()
        if not blocking:
            break
        time.sleep(0.5)


def on_press(key):
    try:
        key_char = KEYS.get(key)
        key_char = key.char if key_char is None else key_char
    except AttributeError:
        return

    if key_char == 'ESC' or typer.check_end():
        typer.show_end()
        return False

    if not typer.started:
        typer.start()

    typer.parse_input(key_char)
    updater(False)


SAMPLE = random.choice((
    """These memories lose their meaning when I think of love as something new, though I know I'll never lose affection for people and things that went before. I know I'll often stop and think about them.""",
    """I think about my daughter now, and what she was spared. Sometimes I feel grateful. The doctor said she didn't feel a thing, went straight into a coma. Then, somewhere in that blackness, she slipped off into another, deeper kind. Isn't that a beautiful way to go out, painlessly as a happy child? Trouble with dying later is you've already grown up. The damage is done. It's too late.""",
    """What's cool about really little kids is that they don't say stuff to try to hurt your feelings, even though sometimes they do say stuff that hurts your feelings. But they don't actually know what they're saying. Big kids, though: they know what they're saying. And that is definitely not fun for me.""",
    """You cannot entice a true thief, and thief by vocation, into the prose of honest vegetation by any gingerbread reward, or by the offer of a secure position, or by the gift of money, or by a woman's love: because there is here a permanent beauty of risk, a fascinating abyss of danger, the delightful sinking of the heart, the impetuous pulsation of life, the ecstasy!""",
    """When we pulled out into the winter night and the real snow, our snow, began to stretch out beside us and twinkle against the windows, and the dim lights of small Wisconsin stations moved by, a sharp wild brace came suddenly into the air. We drew in deep breaths of it as we walked back from dinner through the cold vestibules, unutterably aware of our identity with this country for one strange hour, before we melted indistinguishably into it again.""",
    """The one place where a man ought to get a square deal is in a courtroom, be he any color of the rainbow, but people have a way of carrying their resentments right into a jury box. As you grow older, you'll see white men cheat black men every day of your life, but let me tell you something and don't you forget it - whenever a white man does that to a black man, no matter who he is, how rich he is, or how fine a family he comes from, that white man is trash.""",
    """Gardeners know how to grow top-notch crops. They determine which plants thrive best under available conditions, plan their optimum placement, and nourish the seeds with plant food and water. Plants that receive the most attention thrive, blossoming into colorful fruits and flowers.""",
    """The Vital Apparatus Vent will deliver a Weighted Companion Cube in three, two, one.""",
    """I think that if I ever have kids, and they are upset, I won't tell them that people are starving in China or anything like that because it wouldn't change the fact that they were upset. And even if somebody else has it much worse, that doesn't really change the fact that you have what you have.""",
    """No, I don't think so; no. Mr. Kane was a man who got everything he wanted and then lost it. Maybe Rosebud was something he couldn't get, or something he lost. Anyway, it wouldn't have explained anything. I don't think any word can explain a man's life. No, I guess Rosebud is just a piece in a jigsaw puzzle... a missing piece."""
))

KEYS = {keyboard.Key.esc: 'ESC', keyboard.Key.space: ' ', keyboard.Key.backspace: '\b', keyboard.Key.enter: '\n'}

# Press `escape` to quit
typer = Typer(SAMPLE, 120)
thread = threading.Thread(target=updater)
thread.start()

# Collect events until released
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
