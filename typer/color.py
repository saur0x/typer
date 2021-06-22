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
        """Generate ANSI foreground color from `r, g, b` values.  """
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
