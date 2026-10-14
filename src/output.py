import time

import keyboard
import pyperclip

from .config import Config


class OutputHandler:
    def __init__(self, config: Config):
        self._mode = config.output_mode

    def send(self, text: str) -> None:
        if self._mode == "paste":
            self._paste(text)
        else:
            pyperclip.copy(text)

    def _paste(self, text: str) -> None:
        try:
            saved = pyperclip.paste()
        except Exception:
            saved = ""

        pyperclip.copy(text)
        time.sleep(0.01)
        keyboard.send("ctrl+v")
        time.sleep(0.05)

        try:
            pyperclip.copy(saved)
        except Exception:
            pass
