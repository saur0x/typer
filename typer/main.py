import os
import threading
from pathlib import Path
from getkey import getkey, keys

import sample
from typer import Typer


UPDATING = True
SAMPLE_PATH = Path(__file__).joinpath("../../data/samples.json").resolve()
SAMPLE = sample.get_random_sample(SAMPLE_PATH).get("sample")
KEYS = {keys.SPACE: ' ', keys.BACKSPACE: '\b', keys.ENTER: '\n'}

if os.name == "nt":
    import colorama
    colorama.init()

typer = Typer(SAMPLE, 30)

if UPDATING:
    updater_thread = threading.Thread(target=typer.updater)
    updater_thread.start()
else:
    typer.updater(False)

while not typer.check_end():
    key = getkey(True)
    key_char = KEYS.get(key, key)

    if not typer.started:
        typer.start()

    if key_char == keys.ESC:
        typer.stopped = True
    else:
        typer.parse_input(key_char)
        typer.updater(False)

typer.show_end()

if os.name == "nt":
    colorama.deinit()
