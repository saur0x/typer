import time
import sys
import re
from color import ANSI


class Typer:
    def __init__(self, text, duration=60):
        self.text = text
        self.pointer = 0

        # Current word that the pointer is on
        self.word = ''

        # Timing variables
        self.duration = duration
        self.time_remaining = self.duration

        self.init_time = None
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

        self.split_regex = re.compile(r"[\s\n]")

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

        sys.stdout.write(
            ANSI.background_red + ANSI.bold + ANSI.white + info
            + 500 * (' ' + ANSI.left + ANSI.right) + ANSI.reset
        )

    def show_text(self):
        pointer_passed = False
        buffer = ""

        for i, char in enumerate(self.text):
            # Show wrong input characters as different colored
            if i in self.error_pointers:
                buffer += ANSI.red

                # Show a colored underscore / underline
                # for unprintable characters.
                match = self.split_regex.fullmatch(char)
                if match is not None:
                    buffer += ANSI.underline

            # Underline the char that the pointer is currently on
            elif i == self.pointer:
                pointer_passed = True
                buffer += (
                    ANSI.bold + ANSI.underline
                    + ANSI.green + ANSI.background_black
                )

            # Make untyped chars bold
            if pointer_passed:
                buffer += ANSI.bold

            buffer += char + ANSI.reset

        sys.stdout.write(buffer)

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
        return (
            self.stopped
            or self.time_remaining <= 0
            or self.pointer >= len(self.text)
        )

    def show_end(self):
        """Shows end message after `Typer` is finished.
        """
        self.stopped = True
        self.clear_screen()
        self.show_info()
        self.show_separator(2)
        self.show_text()
        self.show_separator(1)

    def updater(self, blocking=True):
        """Thread used for continuously updating `Typer` information.
        """
        while not self.check_end():
            # Don't update `info` if `Typer` is not yet started
            if self.started:
                self.update()

            self.clear_screen()
            self.show_info()
            self.show_separator(2)
            self.show_text()
            self.show_separator(2)
            self.show_prompt()

            # self.show_separator(1)

            sys.stdout.flush()

            if not blocking:
                break

            time.sleep(0.5)
