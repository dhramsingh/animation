"""Visual theme for the Module 8 graphic book.

Every colour, font and size used on a page comes from here, so the whole
book can be restyled from this one file.

Colour meaning is fixed across the book (see the "visual legend" page):
  GO      goroutines (G)            AMBER   OS threads (M)
  VIOLET  logical processors (P)    GREEN   channels, success
  RED     locks, errors, danger     YELLOW  highlights, rules
  PINK    data values / messages    BLUE    time, the kernel, I/O
"""

# ---------------------------------------------------------------- page
RESOLUTION = (2560, 1440)          # 16:9 landscape pages

# ---------------------------------------------------------------- colours
BG = "#0B1220"          # page background
BG_DEEP = "#070C16"     # cover / darkest
PANEL = "#111B2E"       # cards and boxes
PANEL2 = "#16233B"      # nested boxes, table stripes
CODE_BG = "#0D1628"     # code listings
STROKE = "#26385C"      # hairlines and borders
STROKE2 = "#334A75"

TEXT = "#E7EEF8"        # body text
TEXT2 = "#A9B8D0"       # secondary text
MUTED = "#6F819F"       # captions, line numbers

GO = "#00ADD8"          # Go brand cyan
GO_LIGHT = "#7FD8EE"
GO_DARK = "#00799A"
AMBER = "#F5A524"
VIOLET = "#A78BFA"
GREEN = "#34D399"
RED = "#F87171"
YELLOW = "#FACC15"
PINK = "#F472B6"
BLUE = "#60A5FA"
ORANGE = "#FB923C"
TEAL = "#2DD4BF"
GREY = "#94A3B8"
WHITE_ = "#FFFFFF"
BLACK_ = "#0A0F1A"

# Gopher mascot
GOPHER = "#6AD7E5"
GOPHER_DARK = "#2A9FB5"
SNOUT = "#F6D2A2"

# Named colours usable inside text as {name|text}
NAMED = {
    "go": GO, "golight": GO_LIGHT, "amber": AMBER, "violet": VIOLET,
    "green": GREEN, "red": RED, "yellow": YELLOW, "pink": PINK,
    "blue": BLUE, "orange": ORANGE, "teal": TEAL, "grey": GREY,
    "muted": MUTED, "text2": TEXT2, "white": WHITE_,
}

# ---------------------------------------------------------------- fonts
SANS = "Inter"
MONO = "JetBrains Mono"
INLINE_CODE = "#8BE0F2"

# ---------------------------------------------------------------- type scale
# (ManimGL font_size; 24 is roughly 0.17 frame units cap height)
SIZE_COVER = 84
SIZE_H1 = 40          # page titles
SIZE_H2 = 27          # section headings
SIZE_H3 = 22
SIZE_BODY = 20
SIZE_SMALL = 17
SIZE_TINY = 14
SIZE_CODE = 17
SIZE_CODE_SMALL = 15

# Syntax colours for Go listings
SYN = {
    "keyword": "#FF79C6",    # go, chan, select, func, for ...
    "type": "#7FD8EE",       # int, string, error, struct types
    "builtin": "#FFCB6B",    # make, close, len, cap, new, panic
    "func": "#82AAFF",       # function names
    "string": "#C3E88D",
    "number": "#F78C6C",
    "comment": "#6F819F",
    "operator": "#E7EEF8",
    "arrow": "#FACC15",      # the channel operator <-
    "text": "#E7EEF8",
    "package": "#A78BFA",
}
