from typing import Callable

import pystray
from PIL import Image, ImageDraw

STATUS_COLORS: dict[str, tuple[int, int, int]] = {
    "idle": (70, 130, 180),
    "recording": (220, 20, 60),
    "transcribing": (255, 165, 0),
    "error": (128, 0, 0),
}

STATUS_LABELS: dict[str, str] = {
    "idle": "whiper-local — pronto",
    "recording": "whiper-local — gravando...",
    "transcribing": "whiper-local — transcrevendo...",
    "error": "whiper-local — erro",
}


def _make_image(status: str) -> Image.Image:
    color = STATUS_COLORS.get(status, STATUS_COLORS["idle"])
    img = Image.new("RGB", (64, 64), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 56, 56], fill=color)
    return img


class TrayIcon:
    def __init__(self, on_exit: Callable[[], None]):
        self._on_exit = on_exit
        self._icon: pystray.Icon | None = None

    def set_status(self, status: str) -> None:
        if self._icon is None:
            return
        self._icon.icon = _make_image(status)
        self._icon.title = STATUS_LABELS.get(status, "whiper-local")

    def run(self) -> None:
        menu = pystray.Menu(
            pystray.MenuItem("Exit", self._exit_action),
        )
        self._icon = pystray.Icon(
            "whiper-local",
            icon=_make_image("idle"),
            title="whiper-local — pronto",
            menu=menu,
        )
        self._icon.run()

    def stop(self) -> None:
        if self._icon is not None:
            self._icon.stop()

    def _exit_action(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._on_exit()
